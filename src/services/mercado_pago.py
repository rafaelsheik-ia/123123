# Arquivo: src/services/mercado_pago.py (Versão com Idempotency-Key)

import requests
import uuid # <-- IMPORTA A BIBLIOTECA PARA GERAR IDs ÚNICOS
from datetime import datetime, timedelta

class MercadoPagoAPI:
    def __init__(self, access_token, public_key=None):
        if not access_token:
            raise ValueError("Access Token do Mercado Pago é obrigatório.")
        self.access_token = access_token
        self.public_key = public_key
        self.base_url = 'https://api.mercadopago.com'
        self.base_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, json_data=None, idempotency_key=None ):
        """Função auxiliar para fazer requisições e tratar erros de forma centralizada."""
        url = f"{self.base_url}{endpoint}"
        
        # Copia os cabeçalhos base e adiciona a chave de idempotência se ela existir
        headers = self.base_headers.copy()
        if idempotency_key:
            headers['X-Idempotency-Key'] = idempotency_key

        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=json_data, timeout=10)
            else: # GET
                response = requests.get(url, headers=headers, timeout=10)

            response_json = response.json()
            if not response.ok:
                print(f"Erro da API Mercado Pago: {response.status_code} - {response.text}")
            return response_json

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API Mercado Pago: {e}")
            return {'error': 'Erro de conexão com o gateway de pagamento.'}
        except ValueError:
            print(f"Resposta inválida (não-JSON) da API Mercado Pago: {response.text}")
            return {'error': 'Resposta inválida do gateway de pagamento.'}

    def create_payment(self, amount, description, payer_info, external_reference=None):
        """Criar pagamento via PIX."""
        expiration_date = datetime.utcnow() + timedelta(minutes=30)
        payment_data = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": payer_info,
            "date_of_expiration": expiration_date.isoformat(timespec='milliseconds') + "Z"
        }
        if external_reference:
            payment_data["external_reference"] = str(external_reference)
        
        # Gera uma chave de idempotência única para esta transação
        idempotency_key = str(uuid.uuid4())
        
        return self._make_request('POST', '/v1/payments', json_data=payment_data, idempotency_key=idempotency_key)

    # ... (o resto das funções get_payment, create_preference, etc. continuam iguais) ...
    def get_payment(self, payment_id):
        return self._make_request('GET', f'/v1/payments/{payment_id}')

    def create_preference(self, items, back_urls=None, external_reference=None):
        preference_data = {"items": items, "payment_methods": {"installments": 1}, "auto_return": "approved"}
        if back_urls:
            preference_data["back_urls"] = back_urls
        if external_reference:
            preference_data["external_reference"] = str(external_reference)
        return self._make_request('POST', '/checkout/preferences', json_data=preference_data, idempotency_key=str(uuid.uuid4()))

    def get_payment_methods(self):
        return self._make_request('GET', '/v1/payment_methods')
