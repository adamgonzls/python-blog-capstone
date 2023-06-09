from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, DateField


class NewBlogPostForm(FlaskForm):
    title = StringField(label="Blog post title:", render_kw={"placeholder":"The wonderful life of..."})
    subtitle = StringField(label="Blog post subtitle:", render_kw={"placeholder":"The nourishing desert"})
    image = StringField(label="Image file name:", render_kw={"placeholder":"/image.jpg"})
    image_alt_text = StringField(label="Image alt text:", render_kw={"placeholder":"Description of image"})
    body = CKEditorField('Body:')
    field1 = StringField(label="field1", render_kw={"placeholder": "Do not fill this out", "tabindex": -1, "autocomplete": "off", "class": "field1-input"})
    submit = SubmitField(label="Add Blog Post")


class RegisterForm(FlaskForm):
    full_name = StringField(label="Full Name:", render_kw={"placeholder":"FirstName LastName"})
    email = StringField(label="Email Address:", render_kw={"placeholder":"user@domain.com"})
    password = StringField(label="Password:")
    field1 = StringField(label="field1", render_kw={"placeholder": "Do not fill this out", "tabindex": -1, "autocomplete": "off", "class": "field1-input"})
    submit = SubmitField(label="Register")


class UserUpdateForm(FlaskForm):
    full_name = StringField(label="Full Name:", render_kw={"placeholder":"FirstName LastName"})
    submit = SubmitField(label="Register")


class LoginForm(FlaskForm):
    email = StringField(label="Email Address:", render_kw={"placeholder":"user@domain.com"})
    password = StringField(label="Password:")
    field1 = StringField(label="field1", render_kw={"placeholder": "Do not fill this out", "tabindex": -1, "autocomplete": "off", "class": "field1-input"})
    submit = SubmitField(label="Login")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comment:")
    field1 = StringField(label="field1", render_kw={"placeholder": "Do not fill this out", "tabindex": -1, "autocomplete": "off", "class": "field1-input"})
    submit = SubmitField(label="Submit Comment")
