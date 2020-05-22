import os
import random
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///aglib.db")

# Stories that should be centered
exceptions = [3,4,5]

@app.route("/")
def welcome():
    """WELCOME PAGE"""
    return render_template("welcome.html")

@app.route("/about")
def about():
    """ABOUT PAGE"""
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """CONTACT PAGE"""
    if request.method == "POST":
        # Get user's input from the form
        name = request.form.get("name")
        email = request.form.get("email")
        title = request.form.get("title")
        text = request.form.get("text")
        # This allows us to get the current timestamp in JST
        currentDT = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        time = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        # Input the story submission into SQL table called "submissions"
        db.execute("INSERT INTO submissions (title, story, email, author, timestamp) VALUES (:title, :text, :email, :name, :time);",
                    title=title, text=text, email=email, name=name, time=time)
        return render_template("contact.html")
    else:
        return render_template("contact.html")

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    """ADMIN PAGE"""
    # If the admin user clicks on any of the buttons/stories
    if request.method == "POST":
        story_id = request.form.get("story_id")
        story = db.execute("SELECT * FROM submissions WHERE story_id = :id", id=story_id)
        # render display page for the selected story so that admin can read the story
        return render_template("display_admin.html", story_id=story_id, story=story, first_name=session["first_name"])
    else:
        # When you open the page, just display a table of all the submissions (submissions must not be already approved and must not be deleted)
        submissions = db.execute("SELECT * FROM submissions WHERE approved='FALSE' AND deleted='FALSE';")
        length = len(submissions)
        return render_template("admin.html", submissions=submissions, length=length, first_name=session["first_name"])


@app.route("/display_admin", methods=['POST'])
@login_required
def display_admin():
    """STORY DISPLAY PAGE FOR ADMIN"""
    # Based on what button is pressed, either delete_id or approve_id will be None and the other will have the id of the displayed story
    delete_id = request.form.get("delete")
    approve_id = request.form.get("approve")
    if delete_id is None:
        # Admin wants to approve the story
        db.execute("UPDATE submissions SET approved='TRUE' WHERE story_id=:id", id=approve_id)
        story = db.execute("SELECT * FROM submissions WHERE story_id = :id", id=approve_id)
        # Check if author is already in authors database
        rows = db.execute("SELECT * FROM authors WHERE name=:name", name=story[0]["author"])
        if len(rows) != 0:
            # Author is already in the database
            author_id = rows[0]["author_id"]
        else:
            # New Author
            db.execute("INSERT INTO authors (name) VALUES (:name)", name=story[0]["author"])
            # Get new id
            rows = db.execute("SELECT * FROM authors WHERE name=:name", name=story[0]["author"])
            author_id = rows[0]["author_id"]
        # Insert the story into stories database using new author_id
        db.execute("INSERT INTO stories (title,story,clicks,finished,author_id) VALUES (:title, :story, 0,0, :author_id);",
                title=story[0]["title"], story=story[0]["story"], author_id=author_id)
    else:
        # Admin wants to delete the story
        db.execute("UPDATE submissions SET deleted='TRUE' WHERE story_id=:id", id=delete_id)
    # Returns admin to the "Admin" page
    submissions = db.execute("SELECT * FROM submissions WHERE approved='FALSE' AND deleted='FALSE';")
    length = len(submissions)
    return render_template("admin.html", submissions=submissions, length=length, first_name=session["first_name"])


@app.route("/user")
@login_required
def user():
    """USER DASHBOARD"""
    # Presenting with favorites
    fav_stories = db.execute("SELECT stories.story_id, stories.title, authors.name FROM stories JOIN authors ON stories.author_id = authors.author_id WHERE story_id IN (SELECT story_id FROM favorites WHERE user_id=:user_id);", user_id=session["user_id"])
    if len(fav_stories) != 0:
        # This recommendation system relies on user having favorited at least one story
        have_favorites = True
        # Select a random favorited story to base recommendations off of
        num = random.randint(0, len(fav_stories)-1)
        rand_story_id = fav_stories[num]["story_id"]
        rand_story_title = db.execute("SELECT title FROM stories WHERE story_id=:story_id;", story_id=rand_story_id)
        total_recs = db.execute("SELECT stories.story_id, stories.title, authors.name FROM stories JOIN authors ON stories.author_id = authors.author_id WHERE story_id IN (SELECT DISTINCT story_id FROM favorites WHERE user_id != :user_id AND user_id IN (SELECT user_id FROM favorites WHERE story_id=:story_id));",
                        user_id=session["user_id"], story_id=rand_story_id)
        # Remove redundancies in recommendations list
        recs = []
        for i in range(len(total_recs)):
            if total_recs[i] not in fav_stories:
                recs.append(total_recs[i])
        # Check whether there are any recommended stories
        if len(recs) != 0:
            have_recs = True
        else:
            have_recs = False
        return render_template("user.html", first_name=session["first_name"], fav_stories=fav_stories, have_favorites=have_favorites, rand_story_title=rand_story_title, recs=recs, have_recs=have_recs)
    else:
        have_favorites = False
        return render_template("user.html", first_name=session["first_name"], fav_stories=fav_stories, have_favorites=have_favorites)



@app.route("/browse", methods=["GET", "POST"])
def browse():
    """BROWSE PAGE"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # If the user has selected a story
        story_id = request.form.get("story_id")
        story = db.execute("SELECT story_id, title, story, name FROM stories JOIN authors ON stories.author_id = authors.author_id WHERE story_id = :id", id=story_id)
        db.execute("UPDATE stories SET clicks=(clicks+1) WHERE story_id=:id", id=story_id)
        # Check if the user has logged in or not
        if session.get("user_id") is None:
            return render_template("display.html", story=story, story_id=story_id, exceptions=exceptions)
        else:
            # Check if the user has already liked this story
            rows = db.execute("SELECT * FROM favorites WHERE story_id=:story_id AND user_id=:user_id;", story_id=story_id, user_id=session["user_id"])
            if len(rows) != 0:
                liked = True
            else:
                liked = False
            return render_template("display.html", story=story, story_id=story_id, liked=liked, exceptions=exceptions)
    # User reached route via GET
    else:
        # Present all the stories
        first_name = ""
        # Check if user has logged in
        if not session.get("user_id") is None:
            # Get first name from database
            first_name = session["first_name"]
        # Query stories database
        stories = db.execute("SELECT story_id, title, story, name FROM stories JOIN authors ON stories.author_id = authors.author_id ORDER BY clicks DESC;")
        story_num = len(stories)
        # Find how many rows needed
        if (story_num < 3):
            rows = 1
        else:
            rows = int(story_num/3)
            if (story_num % 3 != 0):
                rows += 1
        return render_template("browse.html", stories=stories, rows=rows, length=story_num, first_name=first_name)


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """PASSWORD CHANGE"""
    if request.method == "POST":
        # Check that all boxes are filled in
        if not request.form.get("old"):
            return apology ("Must provide old password.", 403)

        elif not request.form.get("new"):
            return apology ("Must provide new password.", 403)

        elif not request.form.get("confirmation"):
            return apology ("Must confirm password.", 403)

        elif (request.form.get("confirmation") != request.form.get("new")):
            return apology("Passwords do not match.", 403)

        # Update password in database
        pass_hash = generate_password_hash(request.form.get("new"))
        db.execute("UPDATE users SET pass_hash=:hash WHERE id=:id", hash=pass_hash, id=session["user_id"])

        # Return to dashboard
        return redirect("/user")

    else:
        return render_template("change.html")

@app.route("/display", methods=["POST"])
#@login_required
def display():
    """DISPLAY STORY"""
    # POST method only
    story_id = request.form.get("favorite")
    story = db.execute("SELECT story_id, title, story, name FROM stories JOIN authors ON stories.author_id = authors.author_id WHERE story_id = :id", id=story_id)
    # Check if the user has already liked this story
    rows = db.execute("SELECT * FROM favorites WHERE story_id=:story_id AND user_id=:user_id;", story_id=story_id, user_id=session["user_id"])
    if len(rows) != 0:
        db.execute("DELETE FROM favorites WHERE story_id=:story_id AND user_id=:user_id;", story_id=story_id, user_id=session["user_id"])
        liked = False
    else:
        db.execute("INSERT INTO favorites (story_id, user_id) VALUES (:story_id, :user_id)", story_id=story_id, user_id=session["user_id"])
        liked = True
    return render_template("display.html", story=story, story_id=story_id, liked=liked, exceptions=exceptions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """LOG USER IN"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password.", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pass_hash"], request.form.get("password")):
            return apology("Invalid username and/or password.", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["admin"] = rows[0]["admin"]
        session["first_name"] = rows[0]["first_name"]

        # Redirect user to home page
        return redirect("/user")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    """SEARCH STORY DATABASE"""
    if request.method == "POST":
        # Get search term
        search = request.form.get("search")
        # This allows for us to use the LIKE keyword
        searchKey = "%"+search+"%"
        # Search for anything in titles or author names that resembles the search key
        result = db.execute("SELECT story_id, title, story, name FROM stories JOIN authors ON stories.author_id = authors.author_id WHERE title LIKE :search OR name LIKE :search", search=searchKey)
        story_num = len(result)
        # Find rows necessary to format the page
        if (story_num < 3):
            rows = 1
        else:
            rows = int(story_num/3)
            if (story_num % 3 != 0):
                rows += 1
        # result.html is very similar to browse.html in format
        return render_template("result.html", result=result, rows=rows, length=story_num, search=search)
    else:
        return render_template("search.html")

@app.route("/logout")
def logout():
    """LOG USER OUT"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """REGISTER"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.", 403)

        # Ensure first name was submitted
        elif not request.form.get("first_name"):
            return apology("Must provide first name.", 403)

        # Ensure last name was submitted
        elif not request.form.get("last_name"):
            return apology("Must provide last name.", 403)

        # Ensure birthday was submitted
        elif not request.form.get("birthday"):
            return apology("Must provide birthday.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password.", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Must confirm password.", 403)

        #Ensure that password and confirmed password match
        elif (request.form.get("confirmation") != request.form.get("password")):
            return apology("Passwords do not match.", 403)

        # Query database to check if username is taken
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("Username already exists.", 403)

        # Store information in database
        pass_hash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, first_name, last_name, birthday, pass_hash) VALUES (:username, :first_name, :last_name, :birthday, :hash)", username=request.form.get("username"), first_name=request.form.get("first_name"), last_name=request.form.get("last_name"), birthday=request.form.get("birthday"), hash=pass_hash)

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """FORGOT PASSWORD"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.", 403)

        # Ensure first name was submitted
        elif not request.form.get("first_name"):
            return apology("Must provide first name.", 403)

        # Ensure last name was submitted
        elif not request.form.get("last_name"):
            return apology("Must provide last name.", 403)

        # Ensure birthday was submitted
        elif not request.form.get("birthday"):
            return apology("Must provide birthday.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password.", 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Must confirm password.", 403)

        #Ensure that password and confirmed password match
        elif (request.form.get("confirmation") != request.form.get("password")):
            return apology("passwords do not match", 403)

        userinfo = db.execute("SELECT * FROM users WHERE username=:username AND first_name=:first_name AND last_name=:last_name AND birthday=:birthday", username=request.form.get("username"), first_name=request.form.get("first_name"), last_name=request.form.get("last_name"), birthday=request.form.get("birthday"))
        if len(userinfo) != 1:
            return apology("User does not exist.", 403)
        else:
            pass_hash = generate_password_hash(request.form.get("password"))
            db.execute("UPDATE users SET pass_hash=:hash WHERE username=:username", hash=pass_hash, username=request.form.get("username"))
            return redirect("/login")

    else: return render_template("forgot.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
