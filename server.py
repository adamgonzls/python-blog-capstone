from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
from blog import Blog
import smtplib
import os

db = SQLAlchemy()
app = Flask(__name__)
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


# new_post = BlogPost(
#     title="From Bluebonnets to Mexican Hats: A Year-Round Guide to El Paso's Beautiful Native Flowers",
#     subtitle="Explore the Vibrant Colors and Fragrances of El Paso's Native Flowers Throughout the Year",
#     image="blooming-cactus-1000.jpg",
#     image_alt_text="A prickly pear cactus",
#     body="El Paso, Texas is home to a variety of beautiful native flowers that bloom throughout the year. Here are a few examples: Bluebonnets: These lovely blue flowers bloom from March to May, typically in large patches along roadsides and in fields. Indian paintbrush: This vibrant red flower blooms from April to June and is a favorite of hummingbirds. Desert marigold: Blooming from March to October, these bright yellow flowers are a common sight in the desert landscape. Blackfoot daisy: These white flowers with yellow centers bloom from March to November and are drought-resistant. Mexican hat: This unique flower has a red center surrounded by yellow petals that droop downward, resembling a sombrero. It blooms from May to August. These are just a few examples of the beautiful native flowers that can be found in El Paso, Texas throughout the year. Taking a walk or a drive through the local countryside during the appropriate time of year can be a delightful experience for anyone who loves flowers and nature.",
#     publish_date="2023-05-22"
# )

with app.app_context():
    db.create_all()
    # db.session.add(new_post)
    # db.session.commit()


@app.route("/")
def home():
    blog_posts = db.session.execute(db.select(BlogPost)).scalars()
    return render_template("index.html", blog_posts=blog_posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        requestor_name = request.form['name']
        requestor_phone = request.form['phone']
        requestor_email = request.form['email']
        requestor_message = request.form['message']
        send_email(requestor_name, requestor_phone, requestor_email, requestor_message)
        return render_template("contact.html", message_sent=True)
    return render_template("contact.html", message_sent=False)


@app.route("/post/<int:id>")
def get_post(id):
    blog_post = db.get_or_404(BlogPost, id)
    return render_template("post-details.html", blog_post=blog_post)


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
