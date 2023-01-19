from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email

# Formulario para validaçao do usuario


class RegisterForm(FlaskForm):
    username = StringField(label='Username:', validators=[Length(min=4, max=30), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])  # validação da senha
    email = StringField(label='E-mail Address:', validators=[Email(), DataRequired()])
    submit = SubmitField(label='Register')  # Botão submit

