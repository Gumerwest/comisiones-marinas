from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Optional, URL

class TemaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    resumen = TextAreaField('Resumen', validators=[DataRequired()])
    situacion_actual = TextAreaField('Situación Actual')
    submit = SubmitField('Proponer Tema')

class PatrocinadorForm(FlaskForm):
    patrocinador = StringField('Nombre del Patrocinador', validators=[DataRequired()])
    logo = FileField('Logo del Patrocinador')
    enlace = StringField('Enlace Web', validators=[Optional(), URL()])
    solucion_patrocinador = TextAreaField('Solución Propuesta', validators=[DataRequired()])
    submit = SubmitField('Guardar Patrocinador')

class ComentarioForm(FlaskForm):
    contenido = TextAreaField('Comentario', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class DocumentoForm(FlaskForm):
    nombre = StringField('Nombre del Documento', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    documento = FileField('Archivo', validators=[DataRequired()])
    submit = SubmitField('Subir')

class DocumentoComisionForm(FlaskForm):
    nombre = StringField('Nombre del Documento', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    documento = FileField('Archivo', validators=[DataRequired()])
    submit = SubmitField('Subir')

class ReunionForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    fecha = DateTimeField('Fecha y Hora', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    duracion = IntegerField('Duración (minutos)', validators=[Optional()])
    lugar = StringField('Lugar', validators=[Optional()])
    enlace_virtual = StringField('Enlace de Reunión Virtual', validators=[Optional(), URL()])
    submit = SubmitField('Proponer Reunión')
