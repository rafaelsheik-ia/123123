# Arquivo: src/services/barato_social.py (Versão Final que Imita o Exemplo PHP)

import requests
from urllib.parse import urlencode

class BaratoSocialAPI:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key do BaratoSocial é obrigatória.")
        self.api_url = 'https://baratosocial.com/api/v2'
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0 )'
        }

    def _make_request(self, post_data):
        post_data['key'] = self.api_key
        
        try:
            # ====================================================================
            # MUDANÇA CRÍTICA FINAL:
            # Enviamos como dados de formulário (data=...) e, crucialmente,
            # desabilitamos a verificação do certificado SSL (verify=False),
            # imitando o comportamento exato do código de exemplo em PHP.
            # ====================================================================
            response = requests.post(
                self.api_url, 
                data=post_data, 
                headers=self.headers, 
                timeout=30, 
                verify=False # Isto é o equivalente a CURLOPT_SSL_VERIFYPEER = 0
            )

            # Desabilitar avisos de segurança que não são úteis em produção
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

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

    # O resto das funções não precisa mudar
    def services(self):
        post_data = {'action': 'services'}
        return self._make_request(post_data)

    def balance(self):
        post_data = {'action': 'balance'}
        return self._make_request(post_data)
    
    def order(self, data):
        post_data = {'action': 'add', **data}
        return self._make_request(post_data)
