from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
from charset_normalizer import from_path

# Define the file for storing library data
DATA_FILE = "library.json"

# Flask app setup
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Load or initialize the book database


def load_books():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:  # Use UTF-8 encoding
            content = file.read().strip()
            return json.loads(content) if content else []
    except UnicodeDecodeError:
        print("Encoding error: Attempting to fix...")
        # Attempt to auto-detect encoding
        from charset_normalizer import from_path
        result = from_path(DATA_FILE).best()
        if result:
            encoding = result.encoding
            with open(DATA_FILE, "r", encoding=encoding) as file:
                content = file.read().strip()
                return json.loads(content) if content else []
        else:
            print("Failed to detect encoding.")
            return []


def save_books(books):
    with open(DATA_FILE, "w", encoding="utf-8") as file:  # Specify UTF-8 encoding
        json.dump(books, file, indent=4)


# Load translations
def load_translations(language):
    lang_file = f"languages/{language}.json"
    try:
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                return json.load(file)  # Load JSON content
        else:
            print(f"Translation file not found: {lang_file}")
            return {}  # Return an empty dictionary if the file is missing
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error loading translations: {e}")
        return {}  # Return an empty dictionary if the file is invalid


@app.before_request
def set_language():
    # Set default language to English if not already selected
    if "language" not in session:
        session["language"] = "en"

@app.route("/set_language/<lang>")
def set_language_route(lang):
    # Allow users to change the language
    session["language"] = lang
    return redirect(url_for("index"))

@app.route("/")
def index():
    translations = load_translations(session["language"])
    books = load_books()
    return render_template("index.html", translations=translations, books=books)

@app.route("/add", methods=["GET", "POST"])
def add_book():
    translations = load_translations(session["language"])
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")
        if not title or not author or not year:
            return render_template("error.html", message=translations["all_fields_required"])
        
        books = load_books()
        new_id = len(books) + 1
        new_book = {"id": new_id, "title": title, "author": author, "year": int(year), "status": "in stock"}
        books.append(new_book)
        save_books(books)
        return redirect(url_for("index"))
    return render_template("add_book.html", translations=translations)


@app.route("/search", methods=["GET", "POST"])
def search_books():
    translations = load_translations(session.get("language", "en"))
    if request.method == "POST":
        keyword = request.form.get("keyword").lower()
        books = load_books()
        results = [book for book in books if keyword in book["title"].lower() or keyword in book["author"].lower()]
        return render_template("search.html", translations=translations, books=results, keyword=keyword)
    return render_template("search.html", translations=translations, books=None)



if __name__ == "__main__":
    # Create the JSON file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    app.run(debug=True)
