from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, DateField


class NewBlogPostForm(FlaskForm):
    title = StringField(label="Blog post title:")
    subtitle = StringField(label="Blog post subtitle:")
    image = StringField(label="Image file name:")
    image_alt_text = StringField(label="Image alt text:")
    body = CKEditorField('Body:')
    submit = SubmitField(label="Add Blog Post")


class RegisterForm(FlaskForm):
    full_name = StringField(label="Full Name:")
    email = StringField(label="Email Address:")
    password = StringField(label="Password:")
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = StringField(label="Email Address:")
    password = StringField(label="Password:")
    submit = SubmitField(label="Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment:")
    submit = SubmitField(label="Submit Comment")
