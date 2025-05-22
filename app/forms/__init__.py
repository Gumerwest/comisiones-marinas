from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FileField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, ValidationError
from app.models import Usuario

# Importar todos los formularios para facilitar su uso
from app.forms.auth import LoginForm, RegistroForm
from app.forms.comisiones import ComisionForm, SolicitudMembresiaForm
from app.forms.temas import TemaForm, PatrocinadorForm, ComentarioForm, DocumentoForm, ReunionForm
