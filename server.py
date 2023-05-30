from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from Forms import NewBlogPostForm, RegisterForm, LoginForm
from datetime import datetime
import requests
from blog import Blog
import smtplib
import os

db = SQLAlchemy()
app = Flask(__name__)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "iwearmysunglassesatnight"
bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///explore_the_borderland.db"
db.init_app(app)

BLOG_API = "https://api.npoint.io/b58e4135e9c76d950b95"
SMTP_ADDRESS = "smtp.gmail.com"
SENDING_EMAIL = "adamgonzalestest@gmail.com"
SEND_TO_EMAIL = "adamgonzales1@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
MAIL_SUBMISSION_PORT = 587

# res = requests.get(url=BLOG_API).json()
# print(res)
# blog_objects = []
# for blog in res:
#     blog_object = Blog(blog['id'], blog['image'], blog['imageAltText'], blog['title'], blog['subtitle'], blog['body'])
#     blog_objects.append(blog_object)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250))
    image = db.Column(db.String(250))
    image_alt_text = db.Column(db.String(250))
    body = db.Column(db.String)
    publish_date = db.Column(db.String(250))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    full_name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250))
    password = db.Column(db.String(250))
# new_post = BlogPost(
#     title="From Bluebonnets to Mexican Hats: A Year-Round Guide to El Paso's Beautiful Native Flowers",
#     subtitle="Explore the Vibrant Colors and Fragrances of El Paso's Native Flowers Throughout the Year",
#     image="blooming-cactus-1000.jpg",
#     image_alt_text="A prickly pear cactus",
#     body="El Paso, Texas is home to a variety of beautiful native flowers that bloom throughout the year. Here are a few examples: Bluebonnets: These lovely blue flowers bloom from March to May, typically in large patches along roadsides and in fields. Indian paintbrush: This vibrant red flower blooms from April to June and is a favorite of hummingbirds. Desert marigold: Blooming from March to October, these bright yellow flowers are a common sight in the desert landscape. Blackfoot daisy: These white flowers with yellow centers bloom from March to November and are drought-resistant. Mexican hat: This unique flower has a red center surrounded by yellow petals that droop downward, resembling a sombrero. It blooms from May to August. These are just a few examples of the beautiful native flowers that can be found in El Paso, Texas throughout the year. Taking a walk or a drive through the local countryside during the appropriate time of year can be a delightful experience for anyone who loves flowers and nature.",
#     publish_date="2023-05-22"
# )

# new_user = User(
#     full_name='Adam Gon',
#     email="adamgonzales1@gmail.com",
#     password="Test123"
# )


with app.app_context():
    db.create_all()
    # db.session.add(new_user)
    # db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# home page / read all posts
@app.route("/")
def home():
    blog_posts = db.session.execute(db.select(BlogPost)).scalars()
    return render_template("index.html", blog_posts=blog_posts, logged_in=current_user.is_authenticated, user=current_user)


# read individual post
@app.route("/post/<int:post_id>")
def get_post(post_id):
    blog_post = db.get_or_404(BlogPost, post_id)
    return render_template("post_details.html", blog_post=blog_post, logged_in=current_user.is_authenticated, user=current_user)


# create post
@app.route("/new-post", methods=['GET', 'POST'])
def add_blog_post():
    new_blog_post_form = NewBlogPostForm()
    if new_blog_post_form.validate_on_submit():
        current_date = datetime.today()
        publish_date = current_date.strftime("%Y-%m-%d")
        blogpost = BlogPost(
            title=new_blog_post_form.title.data,
            subtitle=new_blog_post_form.subtitle.data,
            image=new_blog_post_form.image.data,
            image_alt_text=new_blog_post_form.image_alt_text.data,
            body=new_blog_post_form.body.data,
            publish_date=publish_date
        )
        db.session.add(blogpost)
        db.session.commit()
        return redirect(url_for("get_post", post_id=blogpost.id))
    return render_template("new_post.html", form=new_blog_post_form, logged_in=current_user.is_authenticated)


# update post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
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
        email = register_form.email.data
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            hashed_salted_password = generate_password_hash(register_form.password.data, method="pbkdf2:sha256", salt_length=8)
            user = User(
                full_name=register_form.full_name.data,
                email=email,
                password=hashed_salted_password
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash('That email already exists, try logging on instead')
            return redirect(url_for('login'))
    return render_template("register.html", form=register_form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
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
            flash('That username doesn\'t exist')
    return render_template("login.html", form=login_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
@login_required
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        requestor_name = request.form['name']
        requestor_phone = request.form['phone']
        requestor_email = request.form['email']
        requestor_message = request.form['message']
        send_email(requestor_name, requestor_phone, requestor_email, requestor_message)
        return render_template("contact.html", message_sent=True)
    return render_template("contact.html", message_sent=False, logged_in=current_user.is_authenticated)


@app.route("/styleguide")
def get_styleguide():
    return render_template("styleguide.html", logged_in=current_user.is_authenticated)


def send_email(requestor_name, requestor_phone, requestor_email, requestor_message):
    email_message = f"subject: Contact form submitted by: {requestor_name}\n\nName: {requestor_name}\nEmail: {requestor_email}\nPhone: {requestor_phone}\nMessage: {requestor_message}\n"
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
