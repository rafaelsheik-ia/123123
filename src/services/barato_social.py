# Arquivo: src/services/barato_social.py (Versão Final alinhada com a Documentação)

import requests

class BaratoSocialAPI:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key do BaratoSocial é obrigatória.")
        # URL correta, confirmada por você
        self.api_url = 'https://baratosocial.com/api/v2'
        self.api_key = api_key
        # Cabeçalho correto para dados de formulário
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def _make_request(self, post_data ):
        """Função auxiliar para fazer requisições e tratar erros de forma centralizada."""
        # Adiciona a chave da API a todos os pedidos
        post_data['key'] = self.api_key
        
        try:
            # ====================================================================
            # MUDANÇA CRÍTICA APLICADA AQUI
            # Voltamos a usar 'data=post_data' para enviar como formulário,
            # exatamente como a documentação deles espera.
            # ====================================================================
            response = requests.post(self.api_url, data=post_data, headers=self.headers, timeout=30)

            # Tenta decodificar a resposta como JSON, não importa o status
            response_json = response.json()

            if not response.ok:
                print(f"Erro da API BaratoSocial: {response.status_code} - {response.text}")
            
            return response_json

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API BaratoSocial: {e}")
            return {'error': 'Erro de conexão com o fornecedor de serviços.'}
        except ValueError: # Erro ao decodificar JSON (resposta vazia)
            print(f"Resposta inválida (não-JSON) da API BaratoSocial: {response.text}")
            return {'error': 'O fornecedor de serviços retornou uma resposta vazia ou inválida.'}

    def order(self, data):
        """Adicionar pedido"""
        post_data = {'action': 'add', **data}
        return self._make_request(post_data)

    def status(self, order_id):
        """Obter status do pedido"""
        post_data = {'action': 'status', 'order': order_id}
        return self._make_request(post_data)

    def services(self):
        """Obter lista de serviços"""
        post_data = {'action': 'services'}
        return self._make_request(post_data)

    def balance(self):
        """Obter saldo"""
        post_data = {'action': 'balance'}
        return self._make_request(post_data)

    # ... (as outras funções como refill, cancel, etc. funcionarão automaticamente com este método) ...
