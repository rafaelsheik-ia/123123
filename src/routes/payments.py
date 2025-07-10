# Arquivo: src/routes/payments.py (Versão com a chamada de função CORRIGIDA)

from flask import Blueprint, jsonify, request, session
from src.models.user import User, Payment, db
from src.routes.user import login_required
from src.config import get_config
from src.services.mercado_pago import MercadoPagoAPI

payments_bp = Blueprint('payments', __name__)

def get_mp_api_instance():
    access_token = get_config('mp_access_token')
    if not access_token:
        return None
    return MercadoPagoAPI(access_token)

@payments_bp.route('/create-payment', methods=['POST'])
@login_required
def create_payment():
    data = request.json
    user = User.query.get(session['user_id'])
    
    amount = data.get('amount')
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'error': 'Valor inválido'}), 400
    
    mp_api = get_mp_api_instance()
    if not mp_api:
        return jsonify({'error': 'O sistema de pagamentos não está configurado.'}), 500
    
    payment = Payment(user_id=user.id, amount=amount, status='pending')
    db.session.add(payment)
    db.session.commit()
    
    try:
        # ====================================================================
        # CORREÇÃO APLICADA AQUI
        # ====================================================================
        # Montamos o dicionário 'payer_info' como a função agora espera
        payer_info = {
            "email": user.email,
            "first_name": user.username,
            "last_name": "User" # Placeholder
        }

        # Chamamos a função passando 'payer_info' em vez de 'payer_email'
        mp_payment_data = mp_api.create_payment(
            amount=amount,
            description=f'Recarga de saldo para {user.username}',
            payer_info=payer_info, # <-- AQUI ESTÁ A CORREÇÃO
            external_reference=str(payment.id)
        )
        # ====================================================================

        if 'error' in mp_payment_data:
            db.session.delete(payment)
            db.session.commit()
            error_message = mp_payment_data.get('message', 'Erro desconhecido do gateway de pagamento.')
            print(f"Erro do Mercado Pago ao criar pagamento: {error_message}")
            return jsonify({'error': error_message}), 400

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
            'pix_info': pix_info,
            'amount': amount
        })
            
    except Exception as e:
        db.session.delete(payment)
        db.session.commit()
        print(f"Erro inesperado ao processar pagamento: {e}")
        return jsonify({'error': f'Erro inesperado no servidor: {str(e)}'}), 500

# Mantenha as outras rotas como estão...
