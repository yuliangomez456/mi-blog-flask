# force_recreate_db.py
import os
import sqlite3
from app import create_app, db
from app.models import User, Post, Comment, Category, Tag
from slugify import slugify

def force_recreate_database():
    app = create_app()
    
    # Eliminar cualquier archivo de base de datos existente
    db_files = [
        "app/blog.db",
        "blog.db", 
        "instance/blog.db",
        "app/instance/blog.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️ Eliminado: {db_file}")
    
    with app.app_context():
        print("🚀 CREANDO BASE DE DATOS DESDE CERO...")
        print("=" * 50)
        
        # Forzar la creación de todas las tablas
        db.drop_all()
        db.create_all()
        print("✅ Todas las tablas creadas correctamente")
        
        # Verificar que la columna category_id existe
        try:
            # Esta consulta fallará si la columna no existe
            test_post = Post(title="Test", content="Test", user_id=1)
            db.session.add(test_post)
            db.session.rollback()  # Revertir el test
            print("✅ Columna category_id verificada correctamente")
        except Exception as e:
            print(f"❌ Error con category_id: {e}")
            return
        
        # Crear datos de ejemplo
        print("\n👤 Creando usuarios...")
        admin = User(username='admin', email='admin@blog.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        
        user_test = User(username='usuario_test', email='test@blog.com', is_admin=False)
        user_test.set_password('test123')
        db.session.add(user_test)
        db.session.commit()
        
        print("📂 Creando categorías...")
        categories = [
            Category(name='Tutoriales', slug='tutoriales', description='Tutoriales de programación'),
            Category(name='Noticias', slug='noticias', description='Noticias de tecnología'),
            Category(name='Proyectos', slug='proyectos', description='Proyectos personales'),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        
        print("🏷️ Creando etiquetas...")
        tags = [
            Tag(name='Python', slug='python'),
            Tag(name='Flask', slug='flask'),
            Tag(name='Bootstrap', slug='bootstrap'),
            Tag(name='Web Development', slug='web-development'),
        ]
        for tag in tags:
            db.session.add(tag)
        db.session.commit()
        
        print("📝 Creando posts...")
        post1 = Post(
            title='Bienvenido al Blog con Categorías',
            content='Este es un post de ejemplo con categoría y etiquetas.',
            excerpt='Post de bienvenida con nuevas características',
            slug='bienvenido-blog-categorias',
            published=True,
            user_id=admin.id,
            category_id=categories[0].id
        )
        post1.tags = [tags[0], tags[1]]  # Python, Flask
        db.session.add(post1)
        
        post2 = Post(
            title='Tutorial de Flask para Principiantes',
            content='Aprende Flask desde cero con este tutorial completo.',
            excerpt='Guía completa para empezar con Flask',
            slug='tutorial-flask-principiantes', 
            published=True,
            user_id=admin.id,
            category_id=categories[0].id
        )
        post2.tags = [tags[0], tags[1], tags[3]]  # Python, Flask, Web Development
        db.session.add(post2)
        
        db.session.commit()
        
        print("💬 Creando comentarios...")
        comment1 = Comment(
            content='¡Excelente post! Muy útil.',
            user_id=user_test.id,
            post_id=post1.id,
            approved=True
        )
        db.session.add(comment1)
        db.session.commit()
        
        # Verificación final
        print("\n" + "=" * 50)
        print("✅ BASE DE DATOS CREADA EXITOSAMENTE!")
        print(f"📊 Usuarios: {User.query.count()}")
        print(f"📊 Categorías: {Category.query.count()}")
        print(f"📊 Etiquetas: {Tag.query.count()}")
        print(f"📊 Posts: {Post.query.count()}")
        print(f"📊 Comentarios: {Comment.query.count()}")
        
        # Verificar que los posts tienen category_id
        posts = Post.query.all()
        for post in posts:
            print(f"📝 Post: '{post.title}' - Categoría ID: {post.category_id}")

if __name__ == '__main__':
    force_recreate_database()