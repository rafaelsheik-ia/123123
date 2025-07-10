import os
from flask import Flask
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.services import services_bp
from src.routes.orders import orders_bp
from src.routes.admin import admin_bp
from src.routes.payments import payments_bp

# Cria a instância da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilita CORS para permitir requisições do seu frontend no Netlify
CORS(app, supports_credentials=True)

# Registra todas as suas rotas (blueprints)
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(services_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# Rota de Health Check para o Render saber que a aplicação está viva
@app.route('/api/health')
def health_check():
    return {"status": "ok"}, 200

# --- Configuração do Banco de Dados (PostgreSQL em Produção, SQLite para testes) ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Fallback para um banco de dados local se não estiver no Render
    database_dir = os.path.join(os.path.dirname(__file__), 'src', 'database')
    os.makedirs(database_dir, exist_ok=True)
    database_path = os.path.join(database_dir, 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Inicialização do Banco de Dados e Configurações ---
with app.app_context():
    # Cria todas as tabelas do banco de dados se elas não existirem
    db.create_all()
    
    from src.models.user import AdminConfig
    
    # Mapeia as variáveis de ambiente que vamos configurar no Render
    # para as chaves correspondentes no banco de dados.
    env_configs = {
        'barato_api_key': os.environ.get('BARATO_API_KEY'),
        'mp_access_token': os.environ.get('MP_ACCESS_TOKEN'),
        'mp_public_key': os.environ.get('MP_PUBLIC_KEY'),
        'mp_client_id': os.environ.get('MP_CLIENT_ID'),
        'mp_client_secret': os.environ.get('MP_CLIENT_SECRET'),
        'profit_margin': os.environ.get('PROFIT_MARGIN', '20') # Usa '20' se a variável não for definida
    }
    
    # Este loop garante que as configurações do Render sejam salvas no banco de dados
    for key, value in env_configs.items():
        # Só faz algo se a variável de ambiente tiver um valor
        if value:
            existing_config = AdminConfig.query.filter_by(key=key).first()
            if existing_config:
                # Se a configuração já existe, atualiza o valor
                existing_config.value = value
            else:
                # Se não existe, cria uma nova
                new_config = AdminConfig(key=key, value=value)
                db.session.add(new_config)
    
    # Salva todas as alterações no banco de dados
    db.session.commit()

# Rota genérica que não será usada em produção, mas é boa para testes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    return "Backend do Painel está rodando. Acesse o frontend pelo Netlify."

