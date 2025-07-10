# Arquivo: src/routes/payments.py (Versão Final Corrigida)

from flask import Blueprint, jsonify, request, session
from src.models.user import User, Payment, db
from src.routes.user import login_required

# Importa nossa nova função de configuração e a classe da API
from src.config import get_config
from src.services.mercado_pago import MercadoPagoAPI

payments_bp = Blueprint('payments', __name__)

def get_mp_api_instance():
    """
    Cria uma instância da API do Mercado Pago usando as configurações do ambiente.
    Retorna a instância da API ou None se as credenciais não estiverem configuradas.
    """
    access_token = get_config('mp_access_token')
    public_key = get_config('mp_public_key') # Opcional, mas bom ter

    if not access_token:
        return None
    
    return MercadoPagoAPI(access_token, public_key)

@payments_bp.route('/create-payment', methods=['POST'])
@login_required
def create_payment():
    """Criar pagamento PIX"""
    data = request.json
    user = User.query.get(session['user_id'])
    
    amount = data.get('amount')
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'error': 'Valor inválido'}), 400
    if amount < 1:
        return jsonify({'error': 'Valor mínimo é R$ 1,00'}), 400
    
    mp_api = get_mp_api_instance()
    if not mp_api:
        return jsonify({'error': 'Mercado Pago não configurado no servidor'}), 500
    
    try:
        payment = Payment(user_id=user.id, amount=amount, status='pending')
        db.session.add(payment)
        db.session.commit()
        
        mp_payment_data = mp_api.create_payment(
            amount=amount,
            description=f'Recarga de saldo - {user.username} - ID: {payment.id}',
            payer_email=user.email,
            external_reference=str(payment.id)
        )
        
        if not mp_payment_data or 'id' not in mp_payment_data:
            db.session.delete(payment)
            db.session.commit()
            error_message = mp_payment_data.get('message', 'Erro ao criar pagamento no Mercado Pago')
            return jsonify({'error': error_message}), 500
            
        payment.payment_id = str(mp_payment_data['id'])
        db.session.commit()
        
        pix_info = {}
        if 'point_of_interaction' in mp_payment_data:
            transaction_data = mp_payment_data['point_of_interaction'].get('transaction_data', {})
            pix_info = {
                'qr_code': transaction_data.get('qr_code', ''),
                'qr_code_base64': transaction_data.get('qr_code_base64', ''),
            }
        
        return jsonify({
            'payment_id': payment.id,
            'mp_payment_id': mp_payment_data['id'],
            'amount': amount,
            'status': mp_payment_data.get('status', 'pending'),
            'pix_info': pix_info,
        })
            
    except Exception as e:
        return jsonify({'error': f'Erro inesperado ao criar pagamento: {str(e)}'}), 500

@payments_bp.route('/check-payment/<int:payment_id>', methods=['GET'])
@login_required
def check_payment(payment_id):
    """Verificar status do pagamento"""
    payment = Payment.query.filter_by(id=payment_id, user_id=session['user_id']).first_or_404()
    
    if not payment.payment_id:
        return jsonify({'error': 'Pagamento não possui ID do Mercado Pago'}), 400
    
    mp_api = get_mp_api_instance()
    if not mp_api:
        return jsonify({'error': 'Mercado Pago não configurado'}), 500
    
    try:
        mp_payment = mp_api.get_payment(payment.payment_id)
        if not mp_payment:
            return jsonify({'error': 'Erro ao consultar pagamento no Mercado Pago'}), 500

        old_status = payment.status
        new_status = mp_payment.get('status', 'pending')
        
        status_mapping = {'approved': 'approved', 'pending': 'pending', 'in_process': 'pending', 'rejected': 'rejected', 'cancelled': 'cancelled', 'refunded': 'refunded'}
        mapped_status = status_mapping.get(new_status, 'pending')
        
        if old_status != 'approved' and mapped_status == 'approved':
            user = User.query.get(payment.user_id)
            user.balance += payment.amount
            payment.status = 'approved'
            db.session.commit()
        elif payment.status != mapped_status:
            payment.status = mapped_status
            db.session.commit()

        return jsonify({'status': payment.status})
            
    except Exception as e:
        return jsonify({'error': f'Erro ao verificar pagamento: {str(e)}'}), 500

# Mantenha as outras rotas (webhook, etc.) como estão,
# mas garanta que elas também usem get_mp_api_instance() em vez da função antiga.
# O código que você forneceu já parece usar a função auxiliar, então está correto.
