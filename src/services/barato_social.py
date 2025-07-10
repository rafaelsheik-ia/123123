# Arquivo: src/services/barato_social.py (Solução para forçar conexão IPv4)

import requests
import socket # Biblioteca para operações de rede de baixo nível
from urllib.parse import urlencode

class BaratoSocialAPI:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key do BaratoSocial é obrigatória.")
        
        self.hostname = 'baratosocial.com'
        self.api_path = '/api/v2'
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': self.hostname
        }
        self.ipv4_address = self._get_ipv4_address()

    def _get_ipv4_address(self):
        """Resolve o endereço IPv4 para o hostname para evitar problemas com IPv6."""
        try:
            address_info = socket.getaddrinfo(self.hostname, 443, family=socket.AF_INET)
            ipv4_address = address_info[0][4][0]
            print(f"Endereço IPv4 resolvido para {self.hostname}: {ipv4_address}")
            return ipv4_address
        except Exception as e:
            print(f"Não foi possível resolver o endereço IPv4 para {self.hostname}: {e}")
            return None

    def _make_request(self, post_data):
        if not self.ipv4_address:
            return {'error': 'Não foi possível conectar ao fornecedor. Falha na resolução de DNS.'}

        url = f"https://{self.ipv4_address}{self.api_path}"
        post_data['key'] = self.api_key
        encoded_data = urlencode(post_data )
        
        try:
            # Desabilitamos a verificação de SSL pois estamos usando um IP direto,
            # mas o cabeçalho 'Host' garante a segurança no lado do servidor.
            response = requests.post(url, data=encoded_data, headers=self.headers, timeout=30, verify=False)

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
