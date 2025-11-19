# Crear la aplicación
app = create_app()

# Importar modelos y rutas después de crear la app para evitar importaciones circulares
from app import models
from app.routes import main, auth, admin, posts

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
