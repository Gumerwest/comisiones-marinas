from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

# Tabla de asociación para membresías de comisiones
class MembresiaComision(db.Model):
    __tablename__ = 'membresia_comision'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    comision_id = db.Column(db.Integer, db.ForeignKey('comision.id'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente_aprobacion')  # pendiente_aprobacion, aprobado, rechazado
    rol = db.Column(db.String(20), default='miembro')  # miembro, coordinador, lider
    
    usuario = db.relationship('Usuario', back_populates='membresias')
    comision = db.relationship('Comision', back_populates='membresias')

# Tabla de asociación para votos de temas
class Voto(db.Model):
    __tablename__ = 'voto'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', back_populates='votos')
    tema = db.relationship('Tema', back_populates='votos')

# Tabla de asociación para lecturas de comentarios
class LecturaComentario(db.Model):
    __tablename__ = 'lectura_comentario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    comentario_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=False)
    fecha_lectura = db.Column(db.DateTime, default=datetime.utcnow)
    
    usuario = db.relationship('Usuario', back_populates='lecturas')
    comentario = db.relationship('Comentario', back_populates='lecturas')

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    nombre = db.Column(db.String(64), nullable=False)
    apellidos = db.Column(db.String(64), nullable=False)
    telefono = db.Column(db.String(20))
    razon_social = db.Column(db.String(100))
    nombre_comercial = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=False)
    rol = db.Column(db.String(20), default='usuario')  # usuario, admin
    
    # Relaciones
    membresias = db.relationship('MembresiaComision', back_populates='usuario', lazy='dynamic')
    temas_creados = db.relationship('Tema', back_populates='creador', lazy='dynamic')
    temas_liderados = db.relationship('Tema', foreign_keys='Tema.lider_id', back_populates='lider', lazy='dynamic')
    comentarios = db.relationship('Comentario', back_populates='usuario', lazy='dynamic')
    documentos = db.relationship('Documento', back_populates='usuario', lazy='dynamic')
    documentos_comision = db.relationship('DocumentoComision', back_populates='usuario', lazy='dynamic')
    reuniones_creadas = db.relationship('Reunion', back_populates='creador', lazy='dynamic')
    votos = db.relationship('Voto', back_populates='usuario', lazy='dynamic')
    lecturas = db.relationship('LecturaComentario', back_populates='usuario', lazy='dynamic')
    mensajes_chat = db.relationship('MensajeChat', back_populates='usuario', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def es_miembro_de(self, comision_id):
        return self.membresias.filter_by(
            comision_id=comision_id, 
            estado='aprobado'
        ).first() is not None
    
    def es_coordinador_de(self, comision_id):
        membresia = self.membresias.filter_by(
            comision_id=comision_id, 
            estado='aprobado'
        ).first()
        return membresia is not None and membresia.rol == 'coordinador'
    
    def es_lider_de(self, comision_id):
        membresia = self.membresias.filter_by(
            comision_id=comision_id, 
            estado='aprobado'
        ).first()
        return membresia is not None and membresia.rol == 'lider'
    
    def ha_votado(self, tema_id):
        return self.votos.filter_by(tema_id=tema_id).first() is not None
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

@login.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

class Comision(db.Model):
    __tablename__ = 'comision'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    imagen_path = db.Column(db.String(200))
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    membresias = db.relationship('MembresiaComision', back_populates='comision', lazy='dynamic')
    temas = db.relationship('Tema', back_populates='comision', lazy='dynamic')
    documentos = db.relationship('DocumentoComision', back_populates='comision', lazy='dynamic')
    mensajes_chat = db.relationship('MensajeChat', back_populates='comision', lazy='dynamic')
    
    def __repr__(self):
        return f'<Comision {self.nombre}>'

class Tema(db.Model):
    __tablename__ = 'tema'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    resumen = db.Column(db.Text, nullable=False)
    situacion_actual = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente_aprobacion')  # pendiente_aprobacion, aprobado, rechazado, cerrado
    comision_id = db.Column(db.Integer, db.ForeignKey('comision.id'), nullable=False)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    lider_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    
    # Información del patrocinador
    patrocinador = db.Column(db.String(100))
    logo_patrocinador_path = db.Column(db.String(200))
    enlace_patrocinador = db.Column(db.String(200))
    solucion_patrocinador = db.Column(db.Text)
    
    # Relaciones
    comision = db.relationship('Comision', back_populates='temas')
    creador = db.relationship('Usuario', foreign_keys=[creador_id], back_populates='temas_creados')
    lider = db.relationship('Usuario', foreign_keys=[lider_id], back_populates='temas_liderados')
    comentarios = db.relationship('Comentario', back_populates='tema', lazy='dynamic')
    documentos = db.relationship('Documento', back_populates='tema', lazy='dynamic')
    reuniones = db.relationship('Reunion', back_populates='tema', lazy='dynamic')
    votos = db.relationship('Voto', back_populates='tema', lazy='dynamic')
    mensajes_chat = db.relationship('MensajeChat', back_populates='tema', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tema {self.titulo}>'

class Comentario(db.Model):
    __tablename__ = 'comentario'
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    tema = db.relationship('Tema', back_populates='comentarios')
    usuario = db.relationship('Usuario', back_populates='comentarios')
    lecturas = db.relationship('LecturaComentario', back_populates='comentario', lazy='dynamic')
    
    def __repr__(self):
        return f'<Comentario {self.id} de {self.usuario.nombre}>'

class Documento(db.Model):
    __tablename__ = 'documento'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    path = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20))  # pdf, doc, xls, etc.
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    tema = db.relationship('Tema', back_populates='documentos')
    usuario = db.relationship('Usuario', back_populates='documentos')
    
    def __repr__(self):
        return f'<Documento {self.nombre}>'

class DocumentoComision(db.Model):
    __tablename__ = 'documento_comision'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    path = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    comision_id = db.Column(db.Integer, db.ForeignKey('comision.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    comision = db.relationship('Comision', back_populates='documentos')
    usuario = db.relationship('Usuario', back_populates='documentos_comision')
    
    def __repr__(self):
        return f'<DocumentoComision {self.nombre}>'

class Reunion(db.Model):
    __tablename__ = 'reunion'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False)
    duracion = db.Column(db.Integer)  # en minutos
    lugar = db.Column(db.String(200))
    enlace_virtual = db.Column(db.String(200))
    estado = db.Column(db.String(20), default='pendiente_aprobacion')  # pendiente_aprobacion, aprobada, rechazada, cancelada, finalizada
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    tema = db.relationship('Tema', back_populates='reuniones')
    creador = db.relationship('Usuario', back_populates='reuniones_creadas')
    
    def __repr__(self):
        return f'<Reunion {self.titulo}>'

class MensajeChat(db.Model):
    __tablename__ = 'mensaje_chat'
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    comision_id = db.Column(db.Integer, db.ForeignKey('comision.id'), nullable=True)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='mensajes_chat')
    comision = db.relationship('Comision', back_populates='mensajes_chat')
    tema = db.relationship('Tema', back_populates='mensajes_chat')
    
    def __repr__(self):
        return f'<MensajeChat {self.id} de {self.usuario.nombre}>'
