from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SearchField, RadioField, DateField, DecimalField, TextAreaField, IntegerField, HiddenField, SelectField, SelectMultipleField, widgets
from wtforms.validators import Length, EqualTo, Email, DataRequired, NumberRange, URL, Optional

class RegisterForm(FlaskForm):
    user_type = RadioField(label="User Type", choices=[('1', 'Influencer'), ('2', 'Sponsor')], default='1', validators=[DataRequired()])
    fullname = StringField(label="Full Name : ", validators=[Length(min=1, max=30), DataRequired()])
    email = StringField(label="Email Address : ", validators=[Email(), DataRequired()])
    username = StringField(label="Username : ", validators=[Length(min=1, max=30), DataRequired()])
    password1 = PasswordField(label="Password : ", validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label="Confirm Password : ", validators=[EqualTo('password1'), DataRequired()])
    profile_picture = FileField(label='Profile Picture')
    submit = SubmitField(label="Submit")

class LoginForm(FlaskForm):
    username = StringField(label="Username : ", validators=[DataRequired()])
    password = PasswordField(label="Password : ", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class CampaignForm(FlaskForm):
    name = StringField(label="Campaign Name", validators=[DataRequired()])
    description = TextAreaField(label="Campaign Description : ", validators=[DataRequired()])
    start_date = DateField(label="Campaign Start Date : ", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField(label="Campaign End Date : ", format='%Y-%m-%d', validators=[DataRequired()])
    visibility = RadioField(label="Visibility : ", choices=[('0', 'Public'), ('1', 'Private')], default='0', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class AdRequest(FlaskForm):
    payment = IntegerField(label="Payment : ", validators=[DataRequired()])
    send_to = SelectField(label="Send To : ", coerce=int, validators=[DataRequired()])
    campaign_id = IntegerField(label="Campaign Id : ", validators=[DataRequired()])
    sent_by = IntegerField(label='Sent By', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class UpdateInfluencerProfile(FlaskForm):
    fullname = StringField (
        label="Full Name : ",
        validators=[Length(min=1, max=30), DataRequired()]
    )
    email = StringField(
        label="Email Address : ",
        validators=[Email(), DataRequired()]
    )
    profile_picture = FileField(
        label='Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()]
    )
    category = StringField (
        label="Category : ",
        validators=[Length(min=1, max=30), Optional()]
    )
    niche = StringField (
        label="Niche : ",
        validators=[Length(min=1, max=30), Optional()]
    )
    ig_link = StringField(
        label="Instagram Profile Link : ",
        validators=[URL(message="Invalid URL"), Optional()]
    )
    ig_follower = IntegerField(
        label="Number of Instagram Followers :",
        validators=[NumberRange(min=0, message="Followers must be a positive number"), Optional()]
    )
    fb_link = StringField(
        label="Facebook Profile Link : ",
        validators=[URL(message="Invalid URL"), Optional()]
    )
    fb_follower = IntegerField(
        label="Number of Facebook Followers :",
        validators=[NumberRange(min=0, message="Followers must be a positive number"), Optional()]
    )
    yt_link = StringField(
        label="YouTube Profile Link : ",
        validators=[URL(message="Invalid URL"), Optional()]
    )
    yt_follower = IntegerField(
        label="Number of YouTube Followers :",
        validators=[NumberRange(min=0, message="Followers must be a positive number"), Optional()]
    )
    x_link = StringField(
        label="X Profile Link : ",
        validators=[URL(message="Invalid URL"), Optional()]
    )
    x_follower = IntegerField(
        label="Number of X Followers :",
        validators=[NumberRange(min=0, message="Followers must be a positive number"), Optional()]
    )
    lin_link = StringField(
        label="LinkedIn Profile Link : ",
        validators=[URL(message="Invalid URL"), Optional()]
    )
    lin_follower = IntegerField(
        label="Number of LinkedIn Followers :",
        validators=[NumberRange(min=0, message="Followers must be a positive number"), Optional()]
    )
    submit = SubmitField(label="Submit")

class UpdateSponsorsProfile(FlaskForm):
    fullname = StringField (
        label="Full Name : ",
        validators=[Length(min=1, max=30), DataRequired()]
    )
    email = StringField(
        label="Email Address : ",
        validators=[Email(), DataRequired()]
    )
    profile_picture = FileField(
        label='Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')]
    )
    industry = StringField (
        label="Industry : ",
        validators=[Length(min=1, max=30)]
    )
    submit = SubmitField(label="Submit")

class Negotiate(FlaskForm):
    payment = IntegerField(label="Payment : ", validators=[DataRequired()])
    send_to = IntegerField(label="Send To : ", validators=[DataRequired()])
    campaign_id = IntegerField(label="Campaign Id : ", validators=[DataRequired()])
    sent_by = IntegerField(label='Sent By', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class searchForm(FlaskForm):
    search = SearchField(label="Search : ")
    search_by = SelectField(label="Search by : ", coerce=int, validators=[DataRequired()])
    submit = SubmitField(label="Search")

class SearchCampaignForm(FlaskForm):
    search = SearchField(label="Search Campaign Name : ", validators=[Optional()])
    creator = SelectField(label="Creator : ", coerce=int, validators=[Optional()])
    start_date = DateField(label="Start Date : ", format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField(label="End Date : ", format='%Y-%m-%d', validators=[Optional()])
    status = SelectMultipleField(
        label="Status : ",
        choices=[('0', 'Open'), ('1', 'In-Progress'), ('2', 'Closed')],
        option_widget=widgets.CheckboxInput(),
        coerce=int,
        default=['0', '1', '2'],
        validators=[Optional()]
    )
    submit = SubmitField(label="Search")

class SearchAdRequestForm(FlaskForm):
    sender = SelectField(label="Sender : ", coerce=int, validators=[Optional()])
    reciver = SelectField(label="Reciver : ", coerce=int, validators=[Optional()])
    campaign = SelectField(label="Campaign : ", coerce=int, validators=[Optional()])
    submit = SubmitField(label="Search")