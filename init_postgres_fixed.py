from app import create_app, db
from app.models import User, Post, Category, Tag, Comment
from datetime import datetime

def init_database():
    app = create_app()
    
    with app.app_context():
        print("🚀 INICIANDO BASE DE DATOS POSTGRESQL...")
        print("==================================================")
        
        # Eliminar y recrear todas las tablas
        print("🗃️ Creando todas las tablas desde cero...")
        db.drop_all()
        db.create_all()
        print("✅ Todas las tablas creadas correctamente")
        
        # Crear usuario admin con password_hash más corto para prueba
        print("👤 Creando usuarios...")
        
        admin = User(
            username='admin',
            email='admin@blog.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        # Usar una contraseña simple para prueba
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Usuario normal
        user = User(
            username='usuario_test',
            email='usuario@test.com',
            first_name='Usuario',
            last_name='Test',
            is_admin=False
        )
        user.set_password('test123')
        db.session.add(user)
        
        db.session.commit()
        print("✅ Usuarios creados correctamente")
        
        # Crear categorías
        print("📂 Creando categorías...")
        categories = [
            Category(name='Tecnología', slug='tecnologia', description='Artículos sobre tecnología y programación'),
            Category(name='Desarrollo Web', slug='desarrollo-web', description='Tutoriales y recursos de desarrollo web'),
            Category(name='Base de Datos', slug='base-de-datos', description='Contenido sobre bases de datos y SQL')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        print("✅ Categorías creadas correctamente")
        
        # Crear etiquetas
        print("🏷️ Creando etiquetas...")
        tags = [
            Tag(name='Python', slug='python'),
            Tag(name='Flask', slug='flask'),
            Tag(name='PostgreSQL', slug='postgresql'),
            Tag(name='Docker', slug='docker'),
            Tag(name='Bootstrap', slug='bootstrap')
        ]
        
        for tag in tags:
            db.session.add(tag)
        
        db.session.commit()
        print("✅ Etiquetas creadas correctamente")
        
        print("🎉 BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
        print("📍 Puedes acceder con:")
        print("   👤 Admin: admin@blog.com / admin123")
        print("   👤 Usuario: usuario@test.com / test123")

if __name__ == '__main__':
    init_database()
    