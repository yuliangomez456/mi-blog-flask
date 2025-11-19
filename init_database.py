# init_database_complete.py
from app import create_app, db
from app.models import User, Post, Comment, Category, Tag
from slugify import slugify
from datetime import datetime

def init_database_complete():
    app = create_app()
    
    with app.app_context():
        print("🚀 INICIANDO BASE DE DATOS COMPLETA...")
        print("=" * 50)
        
        # Eliminar y crear todas las tablas
        print("🗃️ Creando todas las tablas desde cero...")
        db.drop_all()
        db.create_all()
        print("✅ Todas las tablas creadas correctamente")
        
        # Crear usuario admin
        print("\n👤 Creando usuarios...")
        admin_user = User(
            username='admin', 
            email='admin@blog.com', 
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Crear usuario de prueba normal
        test_user = User(
            username='usuario_test',
            email='usuario@test.com',
            is_admin=False
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        
        db.session.commit()
        print("✅ Usuario admin creado: admin / admin123")
        print("✅ Usuario de prueba creado: usuario_test / test123")
        
        # Crear categorías
        print("\n📂 Creando categorías...")
        categories_data = [
            {'name': 'Tutoriales', 'description': 'Tutoriales paso a paso sobre programación y desarrollo'},
            {'name': 'Noticias', 'description': 'Últimas noticias sobre tecnología y desarrollo web'},
            {'name': 'Proyectos', 'description': 'Proyectos personales y casos de estudio'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(
                name=cat_data['name'],
                slug=slugify(cat_data['name']),
                description=cat_data['description']
            )
            categories.append(category)
            db.session.add(category)
            print(f"   ✅ {cat_data['name']}")
        
        db.session.commit()
        
        # Crear etiquetas
        print("\n🏷️ Creando etiquetas...")
        tags_data = ['Python', 'Flask', 'Bootstrap', 'HTML', 'CSS', 'JavaScript']
        
        tags = []
        for tag_name in tags_data:
            tag = Tag(
                name=tag_name,
                slug=slugify(tag_name)
            )
            tags.append(tag)
            db.session.add(tag)
            print(f"   ✅ {tag_name}")
        
        db.session.commit()
        
        # Crear posts de ejemplo
        print("\n📝 Creando posts de ejemplo...")
        posts_data = [
            {
                'title': 'Bienvenido al Blog con Sistema de Likes',
                'excerpt': 'Un blog moderno con sistema de likes, favoritos y comentarios',
                'content': '''¡Hola! Bienvenido a mi blog completo con todas las funcionalidades.

## Características implementadas:
- ✅ Sistema de likes en posts y comentarios
- ✅ Favoritos para guardar posts
- ✅ Categorías y etiquetas
- ✅ Búsqueda avanzada
- ✅ Panel de administración completo
- ✅ Comentarios con moderación

¡Prueba todas las funcionalidades!''',
                'category': categories[0],
                'tags': [tags[0], tags[1], tags[2]],
                'published': True
            },
            {
                'title': 'Cómo Usar el Sistema de Likes y Favoritos',
                'excerpt': 'Aprende a usar todas las funciones de engagement del blog',
                'content': '''El sistema de likes y favoritos te permite interactuar con el contenido.

### Funcionalidades disponibles:

**❤️ Likes:**
- Dar like a posts
- Dar like a comentarios
- Ver contadores de likes

**⭐ Favoritos:**
- Marcar posts como favoritos
- Acceder a tus favoritos desde tu perfil
- Posts populares basados en likes

**🔍 Navegación:**
- Posts por categorías
- Posts por etiquetas
- Búsqueda avanzada''',
                'category': categories[0],
                'tags': [tags[0], tags[1]],
                'published': True
            },
            {
                'title': 'Tutorial de Flask - Creando un Blog Completo',
                'excerpt': 'Aprende a crear un blog desde cero con Flask',
                'content': '''En este tutorial aprenderás a crear un blog completo con Flask.

### Tecnologías utilizadas:
- Flask como framework web
- SQLAlchemy para la base de datos
- Bootstrap para el diseño
- Flask-Login para autenticación
- SQLite para desarrollo

### Características implementadas:
1. Sistema de usuarios y roles
2. CRUD completo de posts
3. Comentarios y moderación
4. Categorías y etiquetas
5. Sistema de likes y favoritos
6. Búsqueda y filtros''',
                'category': categories[0],
                'tags': [tags[0], tags[1], tags[3], tags[4]],
                'published': True
            }
        ]
        
        for i, post_data in enumerate(posts_data):
            base_slug = slugify(post_data['title'])
            slug = base_slug
            counter = 1
            while Post.query.filter_by(slug=slug).first() is not None:
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            post = Post(
                title=post_data['title'],
                excerpt=post_data['excerpt'],
                content=post_data['content'],
                slug=slug,
                published=post_data['published'],
                user_id=admin_user.id,
                category=post_data['category']
            )
            
            # Asignar etiquetas
            post.tags = post_data['tags']
            
            db.session.add(post)
            print(f"   ✅ {post_data['title']}")
        
        db.session.commit()
        
        # Crear comentarios de ejemplo
        print("\n💬 Creando comentarios de ejemplo...")
        posts = Post.query.all()
        
        comments_data = [
            {
                'content': '¡Excelente funcionalidad de likes! Me encanta poder interactuar con los posts.',
                'user': test_user,
                'post': posts[0]
            },
            {
                'content': 'Muy buen tutorial, justo lo que necesitaba para mi proyecto.',
                'user': test_user,
                'post': posts[2]
            },
            {
                'content': 'El sistema de favoritos es muy útil para guardar posts interesantes.',
                'user': admin_user, 
                'post': posts[1]
            }
        ]
        
        for comment_data in comments_data:
            comment = Comment(
                content=comment_data['content'],
                user_id=comment_data['user'].id,
                post_id=comment_data['post'].id,
                approved=True
            )
            db.session.add(comment)
            print(f"   ✅ Comentario de {comment_data['user'].username}")
        
        db.session.commit()
        
        # Añadir likes y favoritos de ejemplo
        print("\n❤️ Añadiendo likes y favoritos de ejemplo...")
        
        # Usuario test likea el primer post y comentario
        if posts[0] not in test_user.liked_posts:
            test_user.liked_posts.append(posts[0])
            print("   ✅ Usuario test likeó el primer post")
        
        # Usuario test marca como favorito el segundo post
        if len(posts) > 1 and posts[1] not in test_user.favorite_posts:
            test_user.favorite_posts.append(posts[1])
            print("   ✅ Usuario test marcó como favorito el segundo post")
        
        # Admin likea todos los posts y algunos comentarios
        for post in posts:
            if post not in admin_user.liked_posts:
                admin_user.liked_posts.append(post)
        print("   ✅ Admin likeó todos los posts")
        
        # Likes en comentarios
        comments = Comment.query.all()
        if comments:
            test_user.liked_comments.append(comments[0])
            admin_user.liked_comments.append(comments[1])
            print("   ✅ Likes añadidos a comentarios")
        
        db.session.commit()
        
        # Mostrar resumen final
        print("\n" + "=" * 50)
        print("🎉 BASE DE DATOS INICIALIZADA CORRECTAMENTE!")
        print("=" * 50)
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   👥 Usuarios: {User.query.count()}")
        print(f"   📂 Categorías: {Category.query.count()}")
        print(f"   🏷️ Etiquetas: {Tag.query.count()}")
        print(f"   📝 Posts: {Post.query.count()}")
        print(f"   💬 Comentarios: {Comment.query.count()}")
        
        # Estadísticas de engagement
        total_post_likes = sum(post.likes_count for post in Post.query.all())
        total_comment_likes = sum(comment.likes_count for comment in Comment.query.all())
        total_favorites = sum(post.favorites_count for post in Post.query.all())
        
        print(f"   ❤️  Likes en posts: {total_post_likes}")
        print(f"   💬 Likes en comentarios: {total_comment_likes}") 
        print(f"   ⭐ Favoritos: {total_favorites}")
        
        print(f"\n🔑 CREDENCIALES:")
        print(f"   Admin: admin / admin123")
        print(f"   Usuario normal: usuario_test / test123")
        
        print(f"\n🔗 ENLACES IMPORTANTES:")
        print(f"   http://localhost:5000/ - Página principal")
        print(f"   http://localhost:5000/user/favorites - Tus posts favoritos")
        print(f"   http://localhost:5000/popular - Posts populares")
        print(f"   http://localhost:5000/admin/posts - Panel de administración")
        
        print(f"\n🚀 ¡Listo para usar!")

if __name__ == '__main__':
    init_database_complete()