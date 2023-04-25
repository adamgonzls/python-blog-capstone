from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<p>Hello, World!</p>"

print("hello from python")

if __name__ == "__main__":
    app.run(debug=True)