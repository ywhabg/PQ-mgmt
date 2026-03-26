from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DateField,
    SubmitField,
    PasswordField
)
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PQForm(FlaskForm):
    pq_reference_no = StringField("PQ Reference No", validators=[DataRequired(), Length(max=100)])
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[DataRequired()])
    ministry_or_agency = StringField("Ministry / Agency", validators=[DataRequired(), Length(max=150)])
    submitted_by = StringField("Submitted By", validators=[DataRequired(), Length(max=150)])

    assigned_to_user_id = SelectField("Assign To", coerce=int, validators=[Optional()])

    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Urgent", "Urgent")],
        validators=[DataRequired()]
    )

    status = SelectField(
        "Status",
        choices=[
            ("New", "New"),
            ("Under Review", "Under Review"),
            ("Assigned", "Assigned"),
            ("In Progress", "In Progress"),
            ("Pending Clarification", "Pending Clarification"),
            ("Submitted", "Submitted"),
            ("Closed", "Closed"),
        ],
        validators=[DataRequired()]
    )

    due_date = DateField("Due Date", validators=[Optional()])
    date_received = DateField("Date Received", validators=[Optional()])

    submit = SubmitField("Save PQ")


class PQUpdateForm(FlaskForm):
    update_text = TextAreaField("Update / Comment", validators=[DataRequired()])
    update_type = SelectField(
        "Update Type",
        choices=[
            ("General", "General"),
            ("Status Change", "Status Change"),
            ("Assignment", "Assignment"),
            ("Clarification", "Clarification"),
            ("Submission", "Submission"),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Add Update")
