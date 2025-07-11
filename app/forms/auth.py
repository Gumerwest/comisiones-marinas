from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import Usuario

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistroForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    razon_social = StringField('Razón Social', validators=[DataRequired()])
    nombre_comercial = StringField('Nombre Comercial', validators=[DataRequired()])
    cargo = StringField('Cargo', validators=[DataRequired()])
    submit = SubmitField('Registrarse')
    
    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Este email ya está registrado. Por favor, utilice otro.')

class EditarPerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    razon_social = StringField('Razón Social', validators=[DataRequired()])
    nombre_comercial = StringField('Nombre Comercial', validators=[DataRequired()])
    cargo = StringField('Cargo', validators=[DataRequired()])
    puerto_empresa = StringField('Puerto/Empresa', 
                                description='Especifica el puerto o empresa donde trabajas')
    foto_perfil = FileField('Foto de Perfil', 
                           validators=[FileAllowed(['jpg', 'jpeg', 'png'], 
                                     'Solo se permiten imágenes JPG, JPEG y PNG')])
    submit = SubmitField('Actualizar Perfil')
