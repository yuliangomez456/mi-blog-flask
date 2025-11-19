# update_database_categories.py
from app import create_app, db
from app.models import User, Post, Comment, Category, Tag
from slugify import slugify

def update_database():
    app = create_app()
    
    with app.app_context():
        print("🔄 Actualizando base de datos con categorías y etiquetas...")
        
        # Crear las nuevas tablas
        print("🗃️ Creando nuevas tablas...")
        db.create_all()
        print("✅ Tablas creadas/actualizadas correctamente")
        
        # Verificar si ya existe usuario admin
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin', 
                email='admin@blog.com', 
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Usuario admin creado: admin / admin123")
        else:
            print("ℹ️ Usuario admin ya existe")
        
        # Crear un usuario de prueba normal
        if not User.query.filter_by(username='usuario_test').first():
            test_user = User(
                username='usuario_test',
                email='usuario@test.com',
                is_admin=False
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print("✅ Usuario de prueba creado: usuario_test / test123")
        
        # Crear categorías de ejemplo
        if Category.query.count() == 0:
            categories_data = [
                {'name': 'Tutoriales', 'description': 'Tutoriales paso a paso sobre programación y desarrollo'},
                {'name': 'Noticias', 'description': 'Últimas noticias sobre tecnología y desarrollo web'},
                {'name': 'Proyectos', 'description': 'Proyectos personales y casos de estudio'},
                {'name': 'Consejos', 'description': 'Consejos y mejores prácticas para desarrolladores'}
            ]
            
            for cat_data in categories_data:
                category = Category(
                    name=cat_data['name'],
                    slug=slugify(cat_data['name']),
                    description=cat_data['description']
                )
                db.session.add(category)
            
            db.session.commit()
            print("✅ Categorías de ejemplo creadas")
        
        # Crear etiquetas de ejemplo
        if Tag.query.count() == 0:
            tags_data = ['Python', 'Flask', 'Bootstrap', 'HTML', 'CSS', 'JavaScript', 'Web Development', 'Backend', 'Frontend', 'Database']
            
            for tag_name in tags_data:
                tag = Tag(
                    name=tag_name,
                    slug=slugify(tag_name)
                )
                db.session.add(tag)
            
            db.session.commit()
            print("✅ Etiquetas de ejemplo creadas")
        
        # Verificar si hay posts existentes y añadir slugs si faltan
        posts = Post.query.all()
        if posts:
            print("🔄 Actualizando slugs de posts existentes...")
            for post in posts:
                if not post.slug:
                    base_slug = slugify(post.title)
                    slug = base_slug
                    counter = 1
                    while Post.query.filter_by(slug=slug).first() is not None:
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    post.slug = slug
                    print(f"   - '{post.title}' -> slug: '{slug}'")
            
            # Asignar categorías y etiquetas a posts existentes
            categories = Category.query.all()
            tags = Tag.query.all()
            
            if categories and tags:
                print("🔄 Asignando categorías y etiquetas a posts existentes...")
                
                for i, post in enumerate(posts):
                    # Asignar categoría (rotando entre las disponibles)
                    if categories:
                        post.category = categories[i % len(categories)]
                    
                    # Asignar algunas etiquetas aleatorias
                    if tags:
                        num_tags = min(3, len(tags))
                        post.tags = tags[i % len(tags):(i % len(tags)) + num_tags]
                        if len(post.tags) < num_tags:
                            post.tags.extend(tags[:num_tags - len(post.tags)])
                
                print("✅ Categorías y etiquetas asignadas a posts existentes")
            
            db.session.commit()
            print("✅ Slugs actualizados correctamente")
        
        # Crear algunos comentarios de ejemplo
        if Comment.query.count() == 0 and posts:
            test_user = User.query.filter_by(username='usuario_test').first()
            if test_user and posts:
                comments_data = [
                    {
                        'content': '¡Excelente post! Muy informativo y bien explicado.',
                        'post': posts[0]
                    },
                    {
                        'content': 'Me gustaría saber más sobre este tema. ¿Hay alguna documentación adicional?',
                        'post': posts[0]
                    },
                    {
                        'content': 'Muy buen tutorial para empezar. Gracias por compartir!',
                        'post': posts[1] if len(posts) > 1 else posts[0]
                    }
                ]
                
                for comment_data in comments_data:
                    comment = Comment(
                        content=comment_data['content'],
                        user_id=test_user.id,
                        post_id=comment_data['post'].id,
                        approved=True
                    )
                    db.session.add(comment)
                
                db.session.commit()
                print("✅ Comentarios de ejemplo creados")
        
        # Mostrar resumen
        print("\n📊 RESUMEN DE LA BASE DE DATOS:")
        print(f"   👥 Usuarios: {User.query.count()}")
        print(f"   📝 Posts: {Post.query.count()}")
        print(f"   📂 Categorías: {Category.query.count()}")
        print(f"   🏷️ Etiquetas: {Tag.query.count()}")
        print(f"   💬 Comentarios: {Comment.query.count()}")
        
        print("\n🎉 Base de datos actualizada correctamente!")
        print("\n🔑 CREDENCIALES DISPONIBLES:")
        print("   Admin: admin / admin123")
        print("   Usuario normal: usuario_test / test123")
        print("\n🔗 ENLACES DISPONIBLES:")
        print("   http://localhost:5000/admin/categories - Gestionar categorías")
        print("   http://localhost:5000/admin/tags - Gestionar etiquetas")
        print("   http://localhost:5000/category/tutoriales - Ver posts por categoría")
        print("   http://localhost:5000/tag/python - Ver posts por etiqueta")

if __name__ == '__main__':
    update_database()