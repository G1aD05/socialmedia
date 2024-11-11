import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Load data from JSON files
def save_data():
    with open("posts.json", "w") as f:
        json.dump(posts, f, indent=4)

    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)


def load_data():
    global posts, users
    with open("posts.json", "r") as f:
        posts = json.load(f)
    with open("users.json", "r") as f:
        users = json.load(f)


# Load data at startup
load_data()


@app.route("/")
def home():
    if "username" in session:
        return render_template("home.html", username=session["username"], posts=posts)
    flash("Please log in to view the feed.", "warning")
    return redirect(url_for("login"))


@app.route("/profile/<username>")
def profile(username):
    user = users.get(username)
    if user:
        return render_template("profile.html", user=user, posts=user["posts"])
    return "User not found", 404


@app.route("/post", methods=["GET", "POST"])
def post():
    if "username" not in session:
        flash("You need to be logged in to create a post.", "danger")
        return redirect(url_for("login"))

    author = session["username"]

    if author not in users:
        flash("Invalid session detected. Please log in again.", "danger")
        return redirect(url_for("logout"))

    if request.method == "POST":
        content = request.form.get("content")

        if not content:
            flash("Post content cannot be empty!", "danger")
            return redirect(url_for("post"))

        # Add new post
        new_post = {"author": author, "content": content, "likes": 0}
        posts.append(new_post)
        users[author]["posts"].append(content)

        save_data()  # Save changes to JSON

        flash("Post created successfully!", "success")
        return redirect(url_for("home"))

    return render_template("post.html")


@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    if "username" not in session:
        flash("You need to be logged in to like posts.", "danger")
        return redirect(url_for("login"))

    username = session["username"]

    if 0 <= post_id < len(posts):
        post = posts[post_id]

        if username in post.get("liked_by", []):
            flash("You have already liked this post.", "warning")
        else:
            post["likes"] += 1
            post.setdefault("liked_by", []).append(username)
            save_data()  # Save changes to JSON
            flash("You liked the post!", "success")
    else:
        flash("Post not found.", "danger")

    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("Username already exists. Please choose another.", "warning")
        else:
            users[username] = {"password": password, "name": username.capitalize(), "posts": []}
            save_data()  # Save new user to JSON
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
