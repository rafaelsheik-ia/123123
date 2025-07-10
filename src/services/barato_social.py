# Versão Minimalista
import requests
from urllib.parse import urlencode

class BaratoSocialAPI:
    def __init__(self, api_key):
        self.api_url = 'https://baratosocial.com/api/v2'
        self.api_key = api_key

    def _make_request(self, post_data ):
        post_data['key'] = self.api_key
        try:
            # Sem cabeçalhos customizados, deixando a requests fazer tudo.
            response = requests.post(self.api_url, data=post_data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return {'error': f"Erro na requisição: {e}"}
    
    # ... (resto das funções) ...
    def services(self):
        post_data = {'action': 'services'}
        return self._make_request(post_data)
    def balance(self):
        post_data = {'action': 'balance'}
        return self._make_request(post_data)
