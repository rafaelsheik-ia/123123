# Arquivo: src/services/barato_social.py (Versão Final com Requisição Manual )

import requests
from urllib.parse import urlencode # Biblioteca para formatar dados de formulário

class BaratoSocialAPI:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key do BaratoSocial é obrigatória.")
        self.api_url = 'https://baratosocial.com/api/v2'
        self.api_key = api_key
        # Cabeçalho explícito para dados de formulário
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

    def _make_request(self, post_data ):
        post_data['key'] = self.api_key
        
        # ====================================================================
        # MUDANÇA CRÍTICA: Construção Manual da Requisição
        # Convertemos nosso dicionário em uma string de formulário (ex: 'key=123&action=add')
        # Isso garante que o formato seja exatamente o que um navegador enviaria.
        # ====================================================================
        encoded_data = urlencode(post_data)
        
        try:
            # Enviamos a string de dados já formatada
            response = requests.post(self.api_url, data=encoded_data, headers=self.headers, timeout=30)

            response_json = response.json()
            if not response.ok:
                print(f"Erro da API BaratoSocial: {response.status_code} - {response.text}")
            return response_json

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API BaratoSocial: {e}")
            return {'error': 'Erro de conexão com o fornecedor de serviços.'}
        except ValueError:
            print(f"Resposta inválida (não-JSON) da API BaratoSocial: {response.text}")
            return {'error': 'O fornecedor de serviços retornou uma resposta vazia ou inválida.'}

    # O resto das funções (order, status, services, balance) não precisa mudar,
    # pois todas dependem da _make_request que acabamos de corrigir.
    def order(self, data):
        post_data = {'action': 'add', **data}
        return self._make_request(post_data)

    def status(self, order_id):
        post_data = {'action': 'status', 'order': order_id}
        return self._make_request(post_data)

    def services(self):
        post_data = {'action': 'services'}
        return self._make_request(post_data)

    def balance(self):
        post_data = {'action': 'balance'}
        return self._make_request(post_data)
