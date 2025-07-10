# Arquivo: src/routes/orders.py (Versão Final Corrigida)

from flask import Blueprint, jsonify, request, session
from src.models.user import User, Order, Service, db
from src.routes.user import login_required

# Importa nossa nova função de configuração e a classe da API
from src.config import get_config
from src.services.barato_social import BaratoSocialAPI

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Criar novo pedido"""
    data = request.json
    user = User.query.get(session['user_id'])
    
    required_fields = ['service_id', 'link', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos service_id, link e quantity são obrigatórios'}), 400
    
    service = Service.query.filter_by(service_id=data['service_id'], is_active=True).first()
    if not service:
        return jsonify({'error': 'Serviço não encontrado ou inativo'}), 404
    
    quantity = int(data['quantity'])
    if not (service.min <= quantity <= service.max):
        return jsonify({'error': f'Quantidade deve estar entre {service.min} e {service.max}'}), 400
    
    # USA A NOVA FUNÇÃO get_config
    profit_margin = float(get_config('profit_margin') or 0)
    final_rate = service.get_final_price(profit_margin)
    total_charge = (final_rate * quantity) / 1000
    
    if user.balance < total_charge:
        return jsonify({'error': 'Saldo insuficiente'}), 400
    
    # USA A NOVA FUNÇÃO get_config
    api_key = get_config('barato_api_key')
    if not api_key:
        return jsonify({'error': 'API BaratoSocial não configurada'}), 500
    
    try:
        api = BaratoSocialAPI(api_key)
        order_data = {'service': service.service_id, 'link': data['link'], 'quantity': quantity}
        if data.get('comments'):
            order_data['comments'] = data['comments']
        
        api_response = api.order(order_data)
        
        if 'error' in api_response:
            return jsonify({'error': api_response['error']}), 500
        
        user.balance -= total_charge
        
        new_order = Order(
            user_id=user.id,
            service_id=service.service_id,
            service_name=service.name,
            link=data['link'],
            quantity=quantity,
            charge=total_charge,
            barato_order_id=api_response.get('order'),
            status='Pending'
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({'message': 'Pedido criado com sucesso', 'order': new_order.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': f'Erro ao criar pedido: {str(e)}'}), 500

@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Listar pedidos do usuário"""
    user = User.query.get(session['user_id'])
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [order.to_dict() for order in orders]})

# ... (Mantenha as outras rotas como get_order, update_order_status, etc.,
# mas certifique-se de que qualquer chamada à API BaratoSocial use a mesma lógica:
# api_key = get_config('barato_api_key')
# api = BaratoSocialAPI(api_key)
# ...
