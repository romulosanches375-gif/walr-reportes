from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ ¡La aplicación está funcionando correctamente!"

@app.route('/test')
def test():
    return "✅ Servidor OK"

@app.route('/login')
def login():
    return "✅ Página de login - funcionando"

@app.route('/register')
def register():
    return "✅ Página de registro - funcionando"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f'🚀 Servidor ejecutándose en puerto {port}')
    app.run(debug=False, host='0.0.0.0', port=port)