# Arquivo: src/services/barato_social.py (Versão Final Aprimorada )

import requests

class BaratoSocialAPI:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key do BaratoSocial é obrigatória.")
        # CORREÇÃO: Removido o 's' extra de 'baratosociais'
        self.api_url = 'https://baratosocial.com/api/v2'
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _make_request(self, post_data):
        """Função auxiliar para fazer requisições e tratar erros de forma centralizada."""
        # Adiciona a chave da API a todos os pedidos
        post_data['key'] = self.api_key
        
        try:
            # Usamos 'data' para enviar como 'application/x-www-form-urlencoded'
            response = requests.post(self.api_url, data=post_data, headers=self.headers, timeout=30)

            # Tenta decodificar a resposta como JSON, não importa o status
            response_json = response.json()

            # Se a resposta não for OK, imprime o erro para depuração nos logs do Render
            if not response.ok:
                print(f"Erro da API BaratoSocial: {response.status_code} - {response.text}")
            
            return response_json

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API BaratoSocial: {e}")
            return {'error': 'Erro de conexão com o fornecedor de serviços.'}
        except ValueError: # Erro ao decodificar JSON
            print(f"Resposta inválida (não-JSON) da API BaratoSocial: {response.text}")
            return {'error': 'Resposta inválida do fornecedor de serviços.'}

    def order(self, data):
        """Adicionar pedido"""
        post_data = {'action': 'add', **data}
        return self._make_request(post_data)

    def status(self, order_id):
        """Obter status do pedido"""
        post_data = {'action': 'status', 'order': order_id}
        return self._make_request(post_data)

    def multi_status(self, order_ids):
        """Obter status de múltiplos pedidos"""
        post_data = {'action': 'status', 'orders': ','.join(map(str, order_ids))}
        return self._make_request(post_data)

    def services(self):
        """Obter lista de serviços"""
        post_data = {'action': 'services'}
        return self._make_request(post_data)

    def balance(self):
        """Obter saldo"""
        post_data = {'action': 'balance'}
        return self._make_request(post_data)

    # Mantenha as outras funções (refill, cancel, etc.) seguindo o mesmo padrão
    # Exemplo:
    def refill(self, order_id):
        """Refill de pedido"""
        post_data = {'action': 'refill', 'order': order_id}
        return self._make_request(post_data)

