from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError, Optional
from flaskMoviesApp.models import User
from flask_login import current_user
from datetime import datetime as dt


current_year = dt.now().year



def maxImageSize(max_size=2):
    max_bytes = max_size * 1024 * 1024
    def _check_file_size(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f'Το μέγεθος της εικόνας δε μπορεί να υπεβαίνει τα {max_size} MB')
    return _check_file_size

def validate_email(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('Αυτό το email υπάρχει ήδη!')



class SignupForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email"), 
                                       validate_email])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])
    
    password2 = StringField(label="Επιβεβαίωση password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       EqualTo('password', message='Τα δύο πεδία password πρέπει να είναι τα ίδια')])
    
    submit = SubmitField('Εγγραφή')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Αυτό το username υπάρχει ήδη!')



class AccountUpdateForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    image = FileField(label='Εικόνα Προφίλ', 
                      validators=[Optional(strip_whitespace=True),
                                  FileAllowed([ 'jpg', 'jpeg', 'png' ], message='Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                  maxImageSize()])
   
    submit = SubmitField('Αποστολή')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user: raise ValidationError('Αυτό το username υπάρχει ήδη!')


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()

            if user: raise ValidationError('Αυτό το email υπάρχει ήδη!')



class LoginForm(FlaskForm):
    email = StringField(label="email",
                        validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                    Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό.")])
    
    remember_me = BooleanField(label="Remember me")

    submit = SubmitField('Είσοδος')



class NewMovieForm(FlaskForm):
    title = StringField(label="Τίτλος Ταινίας",
                        validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                    Length(min=3, max=50, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 50 χαρακτήρες")])

    plot = TextAreaField(label="Υπόθεση Ταινίας",
                         validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                     Length(min=5, message="Το κείμενο του άρθρου πρέπει να έχει τουλάχιστον 5 χαρακτήρες")])
    
    image = FileField(label='Εικόνα Ταινίας', 
                      validators=[Optional(strip_whitespace=True),
                                  FileAllowed([ 'jpg', 'jpeg', 'png' ], message='Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                  maxImageSize()])

    release_year = IntegerField(label='Έτος πρώτης προβολής της Ταινίας',
                                validators=[Optional(strip_whitespace=True),
                                            NumberRange(min=1888, max=current_year, message=f'Παρακαλώ δώστε μια επιτρεπτή χρονολογία στο διάστημα 1888 έως {current_year}.')])

    rating =  IntegerField(label='Βαθμολογία Ταινίας',
                           validators=[Optional(strip_whitespace=True),
                                       NumberRange(min=1, max=100, message='Παρακαλώ δώστε έναν ακέραιο αριθμό στο διάστημα 1 έως 100.')])

    submit = SubmitField(label='Αποστολή')

