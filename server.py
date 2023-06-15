from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from flask import abort
from flask_bootstrap import Bootstrap5
from forms import NewBlogPostForm, RegisterForm, UserUpdateForm, LoginForm, CommentForm
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from datetime import datetime
import random
import smtplib
import os

db = SQLAlchemy()
app = Flask(__name__)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.environ.get("APP_SECRET_KEY")
bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///explore_the_borderland.db")
db.init_app(app)
gravatar = Gravatar(
    app,
    size=50,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)

BLOG_API = "https://api.npoint.io/b58e4135e9c76d950b95"
SMTP_ADDRESS = os.environ.get("SMTP_ADDRESS")
SENDING_EMAIL = os.environ.get("SENDING_EMAIL")
SEND_TO_EMAIL = os.environ.get("SEND_TO_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
MAIL_SUBMISSION_PORT = os.environ.get("MAIL_SUBMISSION_PORT")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    full_name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250))
    password = db.Column(db.String(250))


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250))
    image = db.Column(db.String(250))
    image_alt_text = db.Column(db.String(250))
    body = db.Column(db.String)
    publish_date = db.Column(db.String(250))
    comments = relationship("Comment", back_populates="parent_post")


class Comment(UserMixin, db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")
    comment = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    parent_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    # db.drop_all()
    db.create_all()
    # db.session.add(new_user)
    # db.session.commit()


def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return function(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def get_random_blog_post():
    if BlogPost.query.all():
        return random.choice(BlogPost.query.all())


def check_honeypot(form):
    if form.field1.data:
        return True


# home page / read all posts
@app.route("/")
def home():
    blog_posts = db.session.execute(db.select(BlogPost)).scalars()
    blog_post = get_random_blog_post()
    return render_template("index.html", blog_posts=blog_posts, logged_in=current_user.is_authenticated, user=current_user, blog_post=blog_post)


# read individual post
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def get_post(post_id):
    comment_form = CommentForm()
    blog_post = db.get_or_404(BlogPost, post_id)
    post_comments = db.get_or_404(Comment, post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        comment = Comment(
            comment=comment_form.comment.data,
            comment_author=current_user,
            parent_post=blog_post
        )
        db.session.add(comment)
        db.session.commit()
        comment_form.comment.data = ""
    return render_template("post_details.html", blog_post=blog_post, logged_in=current_user.is_authenticated, user=current_user, form=comment_form, comments=post_comments)


# create post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_blog_post():
    new_blog_post_form = NewBlogPostForm()
    if new_blog_post_form.validate_on_submit():
        if not check_honeypot(new_blog_post_form):
            current_date = datetime.today()
            publish_date = current_date.strftime("%Y-%m-%d")
            blogpost = BlogPost(
                title=new_blog_post_form.title.data,
                subtitle=new_blog_post_form.subtitle.data,
                image=new_blog_post_form.image.data,
                image_alt_text=new_blog_post_form.image_alt_text.data,
                body=new_blog_post_form.body.data,
                author=current_user,
                publish_date=publish_date,
            )
            db.session.add(blogpost)
            db.session.commit()
            return redirect(url_for("get_post", post_id=blogpost.id))
        else:
            return redirect(url_for('home'))
    return render_template("new_post.html", form=new_blog_post_form, logged_in=current_user.is_authenticated)


# update post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    blog_post = db.get_or_404(BlogPost, post_id)
    current_date = datetime.today()
    publish_date = current_date.strftime("%Y-%m-%d")
    edit_form = NewBlogPostForm(
        title=blog_post.title,
        subtitle=blog_post.subtitle,
        image=blog_post.image,
        image_alt_text=blog_post.image_alt_text,
        body=blog_post.body,
    )
    edit_form.submit.label.text = "Update Blog Post"
    if edit_form.validate_on_submit():
        blog_post_to_update = db.session.get(BlogPost, post_id)
        blog_post_to_update.title = edit_form.title.data
        blog_post_to_update.subtitle = edit_form.subtitle.data
        blog_post_to_update.image = edit_form.image.data
        blog_post_to_update.image_alt_text = edit_form.subtitle.data
        blog_post_to_update.body = edit_form.body.data
        blog_post_to_update.publish_date = publish_date
        db.session.commit()
        return redirect(url_for("get_post", post_id=post_id))
    return render_template("new_post.html", form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)


# delete post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    blog_post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(blog_post_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


# add new user
@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if not check_honeypot(register_form):
            email = register_form.email.data
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                hashed_salted_password = generate_password_hash(register_form.password.data, method="pbkdf2:sha256", salt_length=8)
                new_user = User(
                    full_name=register_form.full_name.data,
                    email=email,
                    password=hashed_salted_password,
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("home"))
            else:
                flash('That email already exists, try logging on instead')
                return redirect(url_for('login'))
        else:
            return redirect(url_for('home'))
    return render_template("register.html", form=register_form, logged_in=current_user.is_authenticated)


@app.route("/edit-user", methods=["GET", "POST"])
@login_required
def edit_user():
    user = db.get_or_404(User, current_user.id)
    user_update_form = UserUpdateForm(
        full_name=user.full_name,
    )
    user_update_form.submit.label.text = "Update User"
    if user_update_form.validate_on_submit():
        user.full_name = user_update_form.full_name.data
        db.session.commit()
        flash('Your name has been updated')
    return render_template("register.html", form=user_update_form,
                           logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        if not check_honeypot(login_form):
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    flash('Invalid password, please try again')
            else:
                flash('That username doesn\'t exist, please try again!')
        else:
            return redirect(url_for('home'))
    return render_template("login.html", form=login_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    blog_post = get_random_blog_post()
    return render_template("about.html", logged_in=current_user.is_authenticated, blog_post=blog_post)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if not request.form['field1']:
            requestor_name = request.form['name']
            requestor_email = request.form['email']
            requestor_message = request.form['message']
            send_email(requestor_name, requestor_email, requestor_message)
            return render_template("contact.html", message_sent=True)
        else:
            return redirect(url_for('home'))
    return render_template("contact.html", message_sent=False, logged_in=current_user.is_authenticated)


@app.route("/styleguide")
def get_styleguide():
    return render_template("styleguide.html", logged_in=current_user.is_authenticated)


def send_email(requestor_name, requestor_email, requestor_message, ):
    email_message = f"subject: Contact form submitted by: {requestor_name}\n\nName: {requestor_name}\nEmail: {requestor_email}\nMessage: {requestor_message}\n"
    with smtplib.SMTP(SMTP_ADDRESS, MAIL_SUBMISSION_PORT) as connection:
        connection.starttls()
        connection.login(user=SENDING_EMAIL, password=GMAIL_APP_PASSWORD)
        connection.sendmail(
            from_addr=SENDING_EMAIL,
            to_addrs=SEND_TO_EMAIL,
            msg=email_message
        )


if __name__ == "__main__":
    app.run(debug=True)
