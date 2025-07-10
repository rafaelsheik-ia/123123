# Arquivo: src/routes/admin.py (Versão Final Corrigida)

from flask import Blueprint, jsonify, request
from src.models.user import AdminConfig, User, Payment, Service, db
from src.routes.user import admin_required
from datetime import datetime, timedelta
from sqlalchemy import func

# Importa nossa nova função de configuração
from src.config import get_config

# Importa as classes de serviço que se comunicam com as APIs externas
from src.services.barato_social import BaratoSocialAPI
from src.services.mercado_pago import MercadoPagoAPI

admin_bp = Blueprint('admin', __name__)

# --- ROTAS DE CONFIGURAÇÃO ---
@admin_bp.route('/config', methods=['GET'])
@admin_required
def get_all_config():
    configs = AdminConfig.query.all()
    config_dict = {config.key: config.value for config in configs}
    return jsonify(config_dict)

@admin_bp.route('/config', methods=['POST'])
@admin_required
def update_config():
    data = request.json
    for key, value in data.items():
        config = AdminConfig.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = AdminConfig(key=key, value=value)
            db.session.add(config)
    db.session.commit()
    return jsonify({'message': 'Configurações atualizadas com sucesso'})

# --- ROTAS DE TESTE DE API ---
@admin_bp.route('/test-barato-api', methods=['POST'])
@admin_required
def test_barato_api():
    # USA A NOVA FUNÇÃO get_config
    api_key = get_config('barato_api_key')
    if not api_key:
        return jsonify({'success': False, 'message': 'Chave API BaratoSocial não configurada'}), 400
    
    try:
        api = BaratoSocialAPI(api_key)
        balance_info = api.balance()
        if 'balance' in balance_info:
            return jsonify({'success': True, 'balance': balance_info['balance']})
        else:
            return jsonify({'success': False, 'message': balance_info.get('error', 'Resposta inesperada da API')}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao conectar: {str(e)}'}), 500

@admin_bp.route('/test-mercado-pago', methods=['POST'])
@admin_required
def test_mercado_pago():
    # USA A NOVA FUNÇÃO get_config
    access_token = get_config('mp_access_token')
    if not access_token:
        return jsonify({'success': False, 'message': 'Access Token do Mercado Pago não configurado'}), 400
    
    try:
        mp_api = MercadoPagoAPI(access_token)
        payment_methods = mp_api.get_payment_methods()
        return jsonify({'success': True, 'payment_methods_count': len(payment_methods)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao conectar: {str(e)}'}), 500

# --- ROTA DE SINCRONIZAÇÃO DE SERVIÇOS ---
@admin_bp.route('/sync-services', methods=['POST'])
@admin_required
def sync_services():
    # USA A NOVA FUNÇÃO get_config
    api_key = get_config('barato_api_key')
    if not api_key:
        return jsonify({'error': 'Chave API do BaratoSocial não configurada'}), 400
    
    try:
        api = BaratoSocialAPI(api_key)
        services_data = api.services()
        if not services_data or isinstance(services_data, dict):
             return jsonify({'error': 'Erro ao obter serviços da API', 'response': services_data}), 500
        
        updated_count, new_count = 0, 0
        for service_data in services_data:
            existing_service = Service.query.filter_by(service_id=service_data['service']).first()
            if existing_service:
                existing_service.name = service_data['name']
                existing_service.type = service_data['type']
                existing_service.rate = float(service_data['rate'])
                existing_service.min = int(service_data['min'])
                existing_service.max = int(service_data['max'])
                existing_service.category = service_data.get('category', '')
                updated_count += 1
            else:
                new_service = Service(service_id=service_data['service'], name=service_data['name'], type=service_data['type'], rate=float(service_data['rate']), min=int(service_data['min']), max=int(service_data['max']), category=service_data.get('category', ''))
                db.session.add(new_service)
                new_count += 1
        
        db.session.commit()
        return jsonify({'message': 'Serviços sincronizados com sucesso', 'new_services': new_count, 'updated_services': updated_count})
    except Exception as e:
        return jsonify({'error': f'Erro ao sincronizar serviços: {str(e)}'}), 500

# --- ROTAS DE DASHBOARD E ESTATÍSTICAS ---
@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    total_users = User.query.count()
    total_orders = db.session.query(func.count(Service.id)).scalar() or 0
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.status == 'approved').scalar() or 0
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.status == 'approved', Payment.created_at >= current_month).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'total_orders': total_orders, # Note: Isso conta serviços, não pedidos. Ajustar se tiver tabela Order.
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
    })

# Mantenha as outras rotas de admin que você precisa aqui...
# (get_all_payments, approve_payment, etc.)
