from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class NewBlogPostForm(FlaskForm):
    title = StringField(label="Blog post title:")
    subtitle = StringField(label="Blog post subtitle:")
    image = StringField(label="Image file name:")
    image_alt_text = StringField(label="Image alt text:")
    body = StringField(label="Body:")
    publish_date = StringField(label="Publish date:")
    submit = SubmitField(label="Add Blog Post")
