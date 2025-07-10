# Arquivo: main.py (Versão Final, Corrigida e Robusta para Produção)

import os
from flask import Flask
from flask_cors import CORS

# --- Passo 1: Inicialização Básica ---
# Primeiro, criamos a aplicação Flask.
app = Flask(__name__)

# --- Passo 2: Carregamento de Configurações ---
# Carregamos as configurações essenciais, como a chave secreta e a URL do banco de dados.
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Lógica inteligente para o banco de dados: usa PostgreSQL no Render, SQLite no seu PC.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Estamos no Render (produção)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Estamos no computador local (desenvolvimento)
    database_dir = os.path.join(os.path.dirname(__file__), 'src', 'database')
    os.makedirs(database_dir, exist_ok=True)
    database_path = os.path.join(database_dir, 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"

# --- Passo 3: Inicialização das Extensões ---
# Agora que as configurações estão carregadas, inicializamos as extensões.
CORS(app, supports_credentials=True)
from src.models.user import db
db.init_app(app)

# --- Passo 4: Importação e Registro das Rotas (Blueprints) ---
# Com a aplicação e o DB configurados, podemos importar e registrar nossas rotas.
from src.routes.user import user_bp
from src.routes.services import services_bp
from src.routes.orders import orders_bp
from src.routes.admin import admin_bp
from src.routes.payments import payments_bp

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(services_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# --- Passo 5: Definição de Rotas Simples e Comandos ---
# Rota de verificação de saúde para o Render saber que o app está vivo.
@app.route('/api/health')
def health_check():
    return {"status": "ok"}, 200

# Comando para inicializar o banco de dados pela primeira vez.
# Você pode rodar isso via Shell do Render se precisar recriar o banco.
@app.cli.command("init-db")
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas."""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")
        # Lógica para criar configurações padrão, se não existirem.
        from src.models.user import AdminConfig
        default_configs = {
            'profit_margin': '20',
            'barato_api_key': '',
            'mp_access_token': '',
            'mp_public_key': '',
            'mp_client_id': '',
            'mp_client_secret': ''
        }
        for key, default_value in default_configs.items():
            if not AdminConfig.query.filter_by(key=key).first():
                db.session.add(AdminConfig(key=key, value=default_value))
        db.session.commit()
        print("Configurações padrão criadas.")

# Rota raiz para confirmar que o backend está no ar.
@app.route('/')
def index():
    return "Servidor do Painel INFLUENCIANDO está no ar."
