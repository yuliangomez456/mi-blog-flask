from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, PasswordField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User, Category, Tag

class PostForm(FlaskForm):
    title = StringField('Título', validators=[
        DataRequired(message='El título es obligatorio'),
        Length(min=5, max=200, message='El título debe tener entre 5 y 200 caracteres')
    ])
    excerpt = StringField('Resumen', validators=[
        Length(max=300, message='El resumen no puede exceder 300 caracteres')
    ])
    content = TextAreaField('Contenido', validators=[
        DataRequired(message='El contenido es obligatorio'),
        Length(min=10, message='El contenido debe tener al menos 10 caracteres')
    ])
    category = SelectField('Categoría', coerce=int)
    tags = SelectMultipleField('Etiquetas', coerce=int)
    published = BooleanField('Publicado')
    submit = SubmitField('Guardar Post')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Llenar las opciones de categorías y etiquetas
        self.category.choices = [(0, 'Sin categoría')] + [(c.id, c.name) for c in Category.query.order_by('name')]
        self.tags.choices = [(t.id, t.name) for t in Tag.query.order_by('name')]

class CategoryForm(FlaskForm):
    name = StringField('Nombre de la categoría', validators=[
        DataRequired(),
        Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')
    ])
    description = StringField('Descripción', validators=[
        Length(max=200, message='La descripción no puede exceder 200 caracteres')
    ])
    submit = SubmitField('Crear Categoría')

class TagForm(FlaskForm):
    name = StringField('Nombre de la etiqueta', validators=[
        DataRequired(),
        Length(min=2, max=30, message='El nombre debe tener entre 2 y 30 caracteres')
    ])
    submit = SubmitField('Crear Etiqueta')

class CommentForm(FlaskForm):
    content = TextAreaField('Comentario', validators=[
        DataRequired(message='El comentario no puede estar vacío'),
        Length(min=2, max=1000, message='El comentario debe tener entre 2 y 1000 caracteres')
    ])
    submit = SubmitField('Publicar Comentario')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')  # ✅ AGREGAR ESTA LÍNEA
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(),
        Length(min=3, max=64, message='El usuario debe tener entre 3 y 64 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Length(min=6, message='Ingresa un email válido')
    ])
    first_name = StringField('Nombre', validators=[  # ✅ AGREGAR
        DataRequired(),
        Length(max=100, message='El nombre no puede exceder 100 caracteres')
    ])
    last_name = StringField('Apellido', validators=[  # ✅ AGREGAR
        DataRequired(), 
        Length(max=100, message='El apellido no puede exceder 100 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está registrado.')