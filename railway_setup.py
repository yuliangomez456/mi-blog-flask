import os
import time
from app import create_app, db
from app.models import User

def setup_railway_production():
    '''Inicializa la aplicación en Railway'''
    print('🚀 Iniciando configuración de Railway...')
    
    app = create_app()
    
    with app.app_context():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f'📦 Intentando conectar a la base de datos (intento {attempt + 1})...')
                
                # Crear todas las tablas
                db.create_all()
                print('✅ Tablas creadas exitosamente')
                
                # Verificar/crear usuario admin
                admin = User.query.filter_by(username='admin').first()
                if not admin:
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
                    print('✅ Usuario admin creado')
                else:
                    print('✅ Usuario admin ya existe')
                
                print('🎉 ¡Configuración completada! La aplicación está lista.')
                return True
                
            except Exception as e:
                print(f'❌ Error en intento {attempt + 1}: {e}')
                if attempt < max_retries - 1:
                    print('⏳ Reintentando en 5 segundos...')
                    time.sleep(5)
                else:
                    print('💥 Todos los intentos fallaron')
                    return False

if __name__ == '__main__':
    setup_railway_production()
