from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarme')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está registrado.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está registrado.')

class ReportForm(FlaskForm):
    reporter_name = StringField('Nombre del Reportante', validators=[DataRequired()])
    project = StringField('Proyecto', validators=[DataRequired()])
    description = TextAreaField('Descripción de la Condición Insegura', validators=[DataRequired()])
    location = StringField('Ubicación')
    submit = SubmitField('Enviar Reporte')

class UpdateReportStatusForm(FlaskForm):
    status = SelectField('Estado', choices=[
        ('Pendiente', 'Pendiente'),
        ('En revisión', 'En revisión'),
        ('Resuelto', 'Resuelto'),
        ('Rechazado', 'Rechazado')
    ], validators=[DataRequired()])
    submit = SubmitField('Actualizar Estado')