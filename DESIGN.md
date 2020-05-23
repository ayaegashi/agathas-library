For our project, Agatha's Library, we made a website that displayed stories from users' submissions. In order to create this,
we used Flask/Python with HTML, CSS, SQL, and Javascript. The following is a rundown of how we implemented our project and the
design decisions that we made, organized by the programming language that we used.



-SQL-
We implemented a database consisting of five tables. These tables are authors, favorites, users, stories, and submissions.
In "authors", we have the author_id and name columns. Author_id automatically increments, and can be linked to the "stories"
table by setting authors.author_id=stories.author_id. This table keeps track of all the authors, as the name implies, as well
as the authors of newly submitted stories that the admin approves.
"Favorites" consists of story_id and user_id and stores information about which user liked what story. Story_id is used to link
to the stories table and user_id is used to link to the users table.
"Users" manages all the users who have registered. It has user_id, username, pass_hash, first_name, and admin columns.
These are used in various pages, namely user_id is used to see which user is in the current session. The admin column
is made a global variable by setting it to session["admin"]. This boolean allows us to decide whether or not to reveal
the "Admin" tab on the navigation bar.
"Stories" is the heart of our website and stores story_id, title, story, clicks, finished and author_id. The 'clicks' columns tracks
how many times a story has been viewed, which determines the order in which the stories are displayed to users in \browse.
Lastly, "submissions" is the table that stories sent by users result in. It consists of story_id, title, story, email, author,
approved, timestamp, and deleted columns. The approved and deleted columns are important to decide whether or not to display
a story on the "Admin" page (if a story has columns deleted=TRUE and/or approved=TRUE it will not appear to the admin).
It is essentially possible to link all of our tables together, and we felt this was important because it allowed us to accomplish
a number of tasks:
-by linking author_id across the authors and stories tables, we are able to display the name of the author alongside the title and
text of the table
-by doing the same linking, if a story is approved, we can create a new author in the authors table and use author_id to create a
new row for this story in the stories table. (See lines 97-113 in application.py).
-by linking user_id to story_id through the favorites table we are able to produce graphic table to the user on the "Dashboard" page
-by linking user_id to story_id through the favorites table we are able to recommend new stories to the user. Our recommendation
system first randomly selected the story_id (i.e. story_id=3) of a story that the present user has favorited. Then, using a SQL query,
our website searches for other story_id's that other users, who have also favorited story_id=3, have also favorited. Then, to make sure
that our website does not recommend a story that has already been favorited by this user, we make sure that non of the stories in our
recommendation list are also in the user's favorites list. (For our recommendation system, see lines 129-147 in application.py).



-Flask-
In our application.py, we have several @app.route so that a particular function will occur in certain websites.
/about and / (welcome.html, cover page), two of our simplest ones, render to open their respective pages. These two pages are mostly
text, although / also has three buttons that redirect to various other routes.
Our other @app.route are more complicated as we will explain below.

/contact, /admin, and /display_admin
These routes have two methods, GET and POST. When called on by GET, this returns a simple input form that allows users to input their submissions
for our website. The POST method is more complicated (lines 57-68 in application.py). When a user submits something to this form, their
submission is inputted into a table in our database called "submissions". Upon users’ submissions, their information, in addition to the time of
submission, is stored in respective columns of the submission table. Automatically, the columns approved and deleted are set to FALSE. When a user
with administrative permission logs into our website, they can access this submission via the "Admin" page. If there are submissions that are not
yet approved and not deleted (approved=FALSE and deleted=FALSE) then these stories will appear to the administrator. If the administrator clicks on
a story to read it, she then has the option to approve, delete, or do nothing to this story. If she chooses either of the first two options, the story
will no longer appear on the "Admin" page. This is because, if she approves the story, approved=TRUE so it will not be listed on "Admin". Our Python
code gets the story_id for this story and uses this to insert this story and author into the "stories" and "authors" tables. The story will then appear
on "Browse". If the admin deletes a story, deleted=TRUE and it will no longer appear on the "Admin" page (although it is not truly deleted).

/user serves as a dashboard for the users.
We first present users with stories that they have favorited. Using "if" conditional statements in dashboard.html, we display a table of their favorite
stories if they have favorited stories, or we display a statement saying that they have not favorite stories along with a button to browse our database
if they have not favorited any stories (i.e. they are a new user).
This feature is implemented by querying the database for the story title, title, and author of stories which the user have favorited.
/user also presents a table of recommendations. Our recommendation algorithm is described above.

/browse is accessible to all users and displays our entire collection.
We formatted browse using Bootstrap "cards". We pass a "rows" variable (which is the number of stories/3 + 1). This is important because we use nested for
loops to display rows with three cards per row. The exception is the last row. If the number of stories is not a multiple of three, then we only want one
or two stories in the last row. In order to account for this, we have an "else" statement in browse.html (lines 30-45 in browse.html).

/change is installed for users when they want to change their password.
This can only be accessed when the user is logged in. Once users have inputted their valid old password, new password, and the confirmation, it will
query the database to update the pass_hash column in the users table.

/display is used after a user has selected the story they want to view in browse.
We implemented a variety of formatting tags to make display.html as legible as possible. Using "white-space: pre-wrap;" we made it so that the text would
separate into paragraphs (which it initially didn't, making the text impossible to read!). There were also a few stories that looked better when they were
centered, vs. when they were left-aligned. We set the default to left-aligned, but hardcoded in a few stories (i.e. The Tale of Peter Rabbit) that looked
better when they were centered by putting them into a global list called "exceptions".
One thing that was difficult about display.html was the like button. We wanted the heart to become filled in when a user favorited a story and return to
just an outline if they un-favorited it. However, at the same time we wanted this action to trigger a change in the favorites table in our SQL database.
because we had to link this front-end change with back-end code, the process of the heart changing from filled to not (or vice versa) is slightly slower
than if we had implemented with JavaScript. However, we chose our solution because we needed to make a change in the SQL database.
Lastly, we did use JavaScript to implement a popover function. Essentially, if the user is not logged in, they cannot favorite a story. Thus, when they
click the heart, instead of turning solid, via a JavaScript function a popover is toggled notifying the user that they have to log in (see lines 8-12 on
display.html).
/display is very similar to /display_admin except for the difference in buttons.
You will notice that both /display and /display_admin only have POST methods. We decided to implement it this way because we needed to know which story
to display for both of these pages. The user decides which story in either /browse or /admin. Thus, it made sense to pass this information to display.html
directly in /browse or /admin. They both have POST methods because both pages have buttons that need to either change something in a SQL table or
redirect the user.

/login, /register, /logout
Once the user’s information is stored in the SQL database with /register, the user will be able to login, querying the database to see if the
username and password input of the user is existent in the database. Log out simply takes the user out of their session.



-HTML-
We extended layout.html in most of our HTML files to be able to include the navigation bar, the footer, and additional CSS features.
We are especially proud of welcome.html (which is accessed through /). We had a difficult time displaying images at first until we learned that
Flask requires us to access images through {{url_for('static', filename='logo.png')}}. We also really like the design of this page and were
inspired by a cover page on the Bootstraps website.



-CSS-
We used styes.css which is extended to every HTML to have a coherent style.
We installed google fonts so that the entire web page will have a different font from the original bootstrap setting (we were going
for something that looked a bit like Times New Roman).
Another noteworthy installment is .preview. This allowed the story text in /browse to have three lines and end with “…” instead of
displaying the entirety of the story or essay.



-Javascript-
Javascript is used mainly in display.html and contact.html. For contact.html, the Javascript allows for validation in the contact form
and if an item is missing, it will prompt the user to type in all the necessary information. This was implemented from Bootstrap and the
validation ids, labels, and divs are there to make sure that every item has been inputted. After the user has submitted their work, they
are taken to a page where the user can see a countdown that occurs and after ten seconds, they are redirected to the browse page.
