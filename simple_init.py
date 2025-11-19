from app import create_app, db
from app.models import User, Category, Tag

def simple_init():
    app = create_app()
    
    with app.app_context():
        print("🚀 INICIANDO BASE DE DATOS SIMPLIFICADA...")
        
        # Eliminar y recrear tablas
        print("🗃️ Creando tablas...")
        db.drop_all()
        db.create_all()
        
        # Solo crear usuario admin básico
        print("👤 Creando usuario admin...")
        admin = User(
            username='admin',
            email='admin@blog.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Base de datos inicializada!")
        print("📍 Acceso: admin@blog.com / admin123")

if __name__ == '__main__':
    simple_init()