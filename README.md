If you are running in CS50 IDE, no installations required. If you are not running in CS50 IDE, then install CS50 files.

How to Compile:
Make sure you are in ~/project/agathas/ and type in "flask run" into the terminal. Click the link that is produced.

The first screen you will be taken to is the cover page. This is created by our file "welcome.html" and this webpage is only accessible if you are not logged in.
On welcome.html, you are able to click the three buttons toward the bottom of the screen in order to either register, log in, or continue without logging in.
If you would like to register an account, please do so. If you would like to try out an admin account that we have already created, use the username: "admin" and
password "Admin123!". First name is "Admin", last name "Istrator", birthday "04, 14, 1997".



If you choose to "continue without logging in":

At this point you will be brought to a page rendered by browse.html. You can click on any of the stories here, which will lead you to a page rendered by
"display.html". The page will display the title, author, and text of a story. At the top right of the page is an empty red heart, which allows a user to
"favorite" a story. However, as you are not yet logged in, instead we used Bootstrap's popovers to have a message toggled, notifying the user that they must log
in in order to favorite a story.

The other pages that are accessible to a user that has not logged in is "About", "Search", and "Contact". "About" just displays text introducing ourselves and
the concept of our project. "Search" allows the user to type in phrases to search for a story. The search function we implemented looks through all of the authors
and titles of our collection, but not the actual text itself. For instance, if you type in "ayana" you will see my two essays that I uploaded come up. If you
type in "peter", "pete", or "The Tale of Peter Rabbit", your result will be Beatrix Potter's "The Tale of Peter Rabbit". Finally, the "Contact" page allows for
anybody to submit a short story to be potentially added to our collection. The form asks for the submittor's name, email, the title of their work, and the text
of their work. All of this information is then collected in our SQL table called "submissions". If you fail to input any of the fields, we used JavaScript to
ensure that the user will not be able to complete this submission, and will instead get an error message. (Below, under 'If you choose to "log in" with our
provided username:' we walk through how you can test the "Contact" page further.)
Finally, one key difference between using our website as a logged in member versus as a visitor is what happens when you click "Agatha's Library" at the top left
of our website. When you are not logged in, clicking the logo will redirect you to the cover page (which displays the large logo and is rendered by
"welcome.html"). When you are logged in, clicking the logo will redirect you "Browse".



If you choose to "register" as a new user:

Once you are logged in, you are brought to the "Dashboard" page. As a new user, you will have no favorited stories so the dashboard page will prompt you to
explore the website's collection by going to "Browse". (Note: the log in that we provide has already favorited a story, so its dashboard page looks different).
If you go to "Browse", this page will be essentially the same as if you were not logged in, except that at the top left the page will say "Welcome, " followed
by the first name you input when registering. If you click on a story to read it, the page will look similar to the page that appears for a user that is not
logged in. However, if you click the empty heart at the top right of the page, it will fill in meaning that you successfully favorited this story. Returning to
"Dashboard", this story will appear in a table of your favorited stories. In addition, you will likely have a table underneath this for recommended stories
based on the story that you liked. The recommendation system looks for stories that other users who have liked one of the stories in your "favorites", and
returns a list of these other stories. The idea behind this is that if one user liked Story A and Story B, then another user who liked Story A will most likely
also like Story B and so the website will recommend Story B to the second user. If you like more than one story, every time you refresh "Dashboard", the
website will generate recommendations based on a randomly selected story from your "favorites" table. If you have no recommendations, this means that you are the
first user to "favorite" a particular story so no recommendations could be generated based on that story. (If you have multiple "favorite" stories, then one
time you open "Dashboard" you may have recommendations because the website is generating recommendations based on a story that others have previously favorited.
Another time you may not have any recommendations because the website is generating recommendations based on a story that you are the first to favorite.)
The "About", "Search", and "Contact" pages are the same pages as when you are not logged in.



If you choose to "log in" with our provided username:

The username we provided is an "admin" account. If you go to aglib.db, our database for this project, and to the "users" table, you will see that there is a
column called "admin" which is NULL by default. We have manually set "admin" to "True" for the "admin" username account (as well as for the username "a" and
"cana", corresponding to Ayana's and Cana's accounts). This administrator account is different from normal user accounts primarily because the admin has access
to an exclusive tab called "Admin" to the right of the "Contact" tab. If you click on this tab, you will be directed to a page that displays all of the
submissions that the website received via the "Contact" page. If there are no submissions, then the page will display the message: "No new submissions." If
there are new submissions, then the "Admin" page will display a table with the ID for the submission, the name of the author, the email of the author,
the title of the submission, a preview of the submitted story, and a timestamp of the submission.

If you would like to test out this page, please go to "Contact". We have created a file called "antandgrasshopper.txt" in the folder "agathas" in our CS50 IDE.
You can paste the text in this text file into the appropriate text fields on the "Contact" page. (Alternatively, you can fill in the text fields with
random/nonsense text). Then, when you return to the "Admin" page, you will see that there is a new row. The title of this story is a button, and if you click
on it you will be directed to a page rendered by "display_admin.html". This is different from the normal display page, because it also shows administrator
accounts the email and timestamp associated with the story. At the bottom of the page there are three options: return, approve, and delete. If you click "return"
you will be returned to the "Admin" page with no changes made to the status of the submission. If you click "approve", the story will be removed from the table
on the "Admin" page and added to the publically accessible database under the "Browse" page. Finally, if you click "delete", the story will be removed from the
table on the "Admin" page, but will also not be added to the publically accessible database page. Note: the story is not actually deleted from the SQL database,
but the column "deleted" is updated to "TRUE".



Navigation right:

Once you move past the cover page, you will also have options on the right side of the navigation bar. If you are logged in, this will show "Change Password"
and "Log Out". If you are not logged in, this will show "Register" and "Log In".

"Register":
Prompts you for a unique username (you will get an error if the username is already taken), your first and last name, your birthday, and a password. The password
has a complexity requirement detailed on the page. Once you have registered, you are taken to the "Log In" page.

"Log In":
Prompts you for your username and password. There is also a link you can follow if you forgot your password. We use the user's first and last name as well as
their birthday to authenticate the user. If they input this information correctly, then the user is allowed to change their password. Once you have successfully
logged in, you are directed to "Dashboard".

"Change Password":
Prompts you for your old password and a new password. If your old password is correct and your new password and its confirmation match, then you are redirected
to the "Dashboard".

"Log Out":
Redirects you to the cover page.