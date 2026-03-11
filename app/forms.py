from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length, Regexp, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(message="Username is required."),
            Length(min=4, max=30, message="Username must be at least 4 characters."),
            Regexp(r'^\w{4,30}$', message="Only letters, numbers, and underscores allowed.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "autofocus": True,
            "placeholder": "Username",
        }
    )

    password = PasswordField(
        validators=[
            InputRequired(message="Password is required."),
            Length(min=8, max=30, message="Password must be at least 8 characters.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "placeholder": "Password"
        }
    )

    submit = SubmitField(
        "Login",
        render_kw={"class": "btn btn-primary"}
    )



class RegisterForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(message="Username is required."),
            Length(min=4, max=30, message="Username must be at least 4 characters."),
            Regexp(r'^\w{4,30}$', message="Only letters, numbers, and underscores allowed.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "autofocus": True,
            "placeholder": "Enter Username",
        }
    )

    password = PasswordField(
        validators=[
            InputRequired(message="Password is required."),
            Length(min=8, max=30, message="Password must be at least 8 characters.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "placeholder": "Enter Password"
        }
    )

    submit = SubmitField(
        "Register",
        render_kw={"class": "btn btn-primary"}
    )

    def validate_username(self, username):
        if username.data.strip().lower() == "admin":
            raise ValidationError(f"'{username.data}' is not available.")
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError(f"'{username.data}' already exist. Please choose another")
        


class VerifyForm(FlaskForm):

    username = StringField(
        validators=[
            InputRequired(message="Username is required."),
            Length(min=4, max=30, message="Username must be at least 4 characters."),
            Regexp(r'^\w{4,30}$', message="Only letters, numbers, and underscores allowed.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "autofocus": True,
            "placeholder": "Enter Username",
        }
    )

    submit = SubmitField(
        "Submit",
        render_kw={"class": "btn btn-primary"}
    )


class ResetForm(FlaskForm):

    new_password = PasswordField(
        validators=[
            InputRequired(message="Password is required."),
            Length(min=8, max=30, message="Password must be at least 8 characters.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "autofocus": True,
            "placeholder": "Enter Password"
        }
    )

    confirm_password = PasswordField(
        validators=[
            InputRequired(message="Password is required."),
            EqualTo("new_password", message="Passwords must match!"),
            Length(min=8, max=30, message="Password must be at least 8 characters.")
        ],
        render_kw={
            "class": "form-control",
            "autocomplete": "off",
            "autofocus": True,
            "placeholder": "Confirm Password"
        }
    )


    submit = SubmitField(
        "Submit",
        render_kw={"class": "btn btn-primary"}
    )