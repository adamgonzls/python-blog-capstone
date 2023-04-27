from flask import Flask, render_template, request
import requests
from blog import Blog

app = Flask(__name__)
BLOG_API = "https://api.npoint.io/b58e4135e9c76d950b95"

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
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        message = request.form['message']
        print(name, phone, email, message)
        return render_template("contact.html", message_sent=True)
    return render_template("contact.html", message_sent=False)


# @app.route("/form-entry", methods=["POST"])
# def receive_data():
#     name = request.form['name']
#     phone = request.form['phone']
#     email = request.form['email']
#     message = request.form['message']
#     print(name, phone, email, message)
#     return render_template("contact.html", confirmation="Successfully sent message")


@app.route("/post/<int:id>")
def get_post(id):
    for blog in blog_objects:
        if blog.id == id:
            return render_template("post-details.html", blog_object=blog)


if __name__ == "__main__":
    app.run(debug=True)
