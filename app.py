
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

users = {}
posts = []
comments = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "Tên người dùng đã tồn tại"
        users[username] = generate_password_hash(password)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed = users.get(username)
        if hashed and check_password_hash(hashed, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "Sai tên người dùng hoặc mật khẩu"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", user=session["user"])

@app.route("/forum", methods=["GET", "POST"])
def forum():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        post_id = len(posts)
        posts.append({
            "id": post_id,
            "title": title,
            "content": content,
            "author": session["user"]
        })
        comments[post_id] = []
        return redirect(url_for("forum"))
    return render_template("forum.html", posts=posts, user=session["user"])

@app.route("/forum/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return "Bài viết không tồn tại"
    if request.method == "POST" and "user" in session:
        comment = request.form["comment"]
        comments[post_id].append({"author": session["user"], "content": comment})
        return redirect(url_for("post_detail", post_id=post_id))
    return render_template("post_detail.html", post=post, user=session.get("user"), post_id=post_id)

if __name__ == "__main__":
    app.run(debug=True)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hàm kiểm tra đuôi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Lưu đường dẫn avatar theo user
avatars = {}  # {username: filename}
