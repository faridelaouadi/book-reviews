import os
from flask import Flask, session, render_template, request, redirect,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

#export DATABASE_URL=""postgres://zfpxvcfcktpgux:246b08f96280da1e48c6c52cdab1fde03115a5ad381bea88e2c5fb024bcfba8d@ec2-184-73-192-251.compute-1.amazonaws.com:5432/d568l8r6oti6l4""

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def login():
    if session.get("username") == None:
        return render_template("login.html")
    else:
        return redirect(url_for('search'))

@app.route('/log_out')
def log_out():
    session.pop("username")
    return redirect(url_for('login'))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == 'POST':
        #get form entries
        name = request.form.get("username")
        password = request.form.get("password")

        #get the data we have on the particular user
        user_details = db.execute("SELECT * FROM users WHERE username = :id", {"id": name})


        # Does the user even exist
        if user_details.rowcount == 0:
            return render_template("notice.html", message="User does not exist, please sign up!")
        else:
            #user exists, check if the password is correct
            if user_details.fetchone()[1] == password:
                session["username"] = name
                return render_template("search.html",username=name)
            else:
                return render_template("notice.html", message="The password was incorrect!")
    else:
        if session.get("username") == None:
            return redirect(url_for('login'))
        return render_template("search.html",username=session.get("username"))


@app.route("/registerUser", methods=["POST"])
def registerUser():
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    user_details = db.execute("SELECT * FROM users WHERE username = :id", {"id": username})
    user_already_exists = user_details.rowcount != 0
    if not user_already_exists:
        #user does not already exist
        if password == confirm_password:
            #add the data to the database
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username": username, "password": password})
            db.commit()
            session["username"] = username
            return redirect(url_for('login'))
        else:
            return render_template("notice.html", message="Password and confirm password do not match")
    else:
        #user already exists
        return render_template("notice.html", message="User already exists")

@app.route("/books", methods=["POST"])
def bookPage():
    book_identifier_value = request.form.get("book")
    book_identifier_category = request.form.get("options")

    sql_query = "select * from books where (author like '%{}%') or (title like '%{}%') or (isbn like '%{}%') limit 60;".format(book_identifier_value,book_identifier_value,book_identifier_value)

    books_found = db.execute(sql_query)
    if books_found.rowcount == 0:
        return render_template("notice.html", message="No book exists with this search")
    return render_template("books.html", books=books_found)

@app.route("/books/<string:isbn>")
def singleBook(isbn):
    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("notice.html", message="No such book.")

    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

    user_reviewed_before = db.execute("SELECT * FROM reviews WHERE username = '{}' and isbn = '{}'".format(session.get("username"), isbn)).rowcount != 0
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "DJ0P8S06EUvhfm35RoYjw", "isbns": book.isbn})
    if res == None:
        rating = "Rating Unavailable"
        number_of_stars = 0
    else:
        rating = res.json()['books'][0]['average_rating']
        number_of_stars = round(float(rating))
    session["current_book_isbn"] = isbn
    return render_template("singleBook.html", book=book, rating=rating, number_of_stars= number_of_stars, reviews=reviews, user_reviewed_before=user_reviewed_before)

@app.route("/new_review", methods=["POST"])
def new_review():
    content = str(request.form.get("content"))
    username = session.get("username")
    isbn = session.get("current_book_isbn")
    star_rating = request.form.get("star_rating")

    sql_query = "INSERT INTO reviews values ('{}','{}','{}','{}');".format(isbn,username,content,star_rating)
    add_review = db.execute(sql_query)
    db.commit()
    return redirect(url_for('singleBook', isbn=isbn))


@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    book_data = db.execute("select * from books where isbn = '{}'".format(isbn))
    if book_data.rowcount == 0:
        return render_template("404.html", message="The ISBN you entered was either invalid or not in our database.")
    else:
        book_data = book_data.fetchone()
        #we have isbn,title,author and year
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "DJ0P8S06EUvhfm35RoYjw", "isbns": isbn})
        rev_count = res.json()['books'][0]['reviews_count']
        average_rating = res.json()['books'][0]['average_rating']
        return jsonify(title=book_data.title,
                        author = book_data.author,
                        year = book_data.year,
                        isbn = book_data.isbn,
                        review_count = rev_count,
                        average_rating = average_rating)
