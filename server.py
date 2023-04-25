from flask import Flask, render_template
import requests
from blog import Blog

app = Flask(__name__)
BLOG_API = "https://api.npoint.io/b58e4135e9c76d950b95"

res = requests.get(url=BLOG_API).json()
# print(res)
blog_objects = []
for blog in res:
    blog_object = Blog(blog['id'], blog['title'], blog['subtitle'], blog['body'])
    blog_objects.append(blog_object)
    print(blog_objects)


@app.route("/")
def home():
    return render_template("index.html", blog_objects=blog_objects)

print("hello from python")

if __name__ == "__main__":
    app.run(debug=True)