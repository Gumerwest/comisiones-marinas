from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional

class ComisionForm(FlaskForm):
    nombre = StringField('Nombre de la Comisión', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    imagen = FileField('Imagen (opcional)')
    submit = SubmitField('Guardar')

class SolicitudMembresiaForm(FlaskForm):
    motivo = TextAreaField('Motivo de la solicitud', validators=[Optional()])
    submit = SubmitField('Solicitar Membresía')
