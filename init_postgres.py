from app import create_app, db
from app.models import User, Post, Category, Tag, Comment

def init_database():
    app = create_app()
    
    with app.app_context():
        # Eliminar y recrear todas las tablas
        db.drop_all()
        db.create_all()
        
        # Crear usuario admin
        admin = User(
            username='admin',
            email='admin@blog.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Crear categorías por defecto
        categories = [
            Category(name='Tecnología', slug='tecnologia', description='Artículos sobre tecnología'),
            Category(name='Programación', slug='programacion', description='Tutoriales de programación'),
            Category(name='Base de Datos', slug='base-de-datos', description='Contenido sobre bases de datos')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print("✅ Base de datos inicializada correctamente en PostgreSQL!")

if __name__ == '__main__':
    init_database()