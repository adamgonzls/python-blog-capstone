from flask import Flask, render_template, request
import requests
from blog import Blog
import smtplib
import os

app = Flask(__name__)
BLOG_API = "https://api.npoint.io/b58e4135e9c76d950b95"
SMTP_ADDRESS = "smtp.gmail.com"
SENDING_EMAIL = "adamgonzalestest@gmail.com"
SEND_TO_EMAIL = "adamgonzales1@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
MAIL_SUBMISSION_PORT = 587

res = requests.get(url=BLOG_API).json()
print(res)
blog_objects = []
for blog in res:
    blog_object = Blog(blog['id'], blog['image'], blog['imageAltText'], blog['title'], blog['subtitle'], blog['body'])
    blog_objects.append(blog_object)


@app.route("/")
def home():
    return render_template("index.html", blog_objects=blog_objects)


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
    for blog in blog_objects:
        if blog.id == id:
            return render_template("post-details.html", blog_object=blog)


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
