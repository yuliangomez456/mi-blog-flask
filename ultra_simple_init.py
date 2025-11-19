from app import create_app, db
from app.models import User

def ultra_simple_init():
    app = create_app()
    
    with app.app_context():
        print("🚀 INICIANDO BASE DE DATOS ULTRA SIMPLE...")
        
        # Solo crear las tablas básicas
        print("🗃️ Creando tablas básicas...")
        db.create_all()
        
        # Verificar si ya existe el usuario admin
        if not User.query.filter_by(email='admin@blog.com').first():
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
            print("✅ Usuario admin creado!")
        else:
            print("✅ Usuario admin ya existe")
        
        print("🎉 BASE DE DATOS LISTA!")
        print("📍 Acceso: admin@blog.com / admin123")

if __name__ == '__main__':
    ultra_simple_init()