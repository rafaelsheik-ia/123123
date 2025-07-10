# Arquivo: src/config.py

import os
from .models.user import AdminConfig

def get_config(key):
    """
    Busca uma configuração de forma inteligente.
    1. Primeiro, tenta pegar da variável de ambiente (mais confiável no Render).
    2. Se não encontrar, busca no banco de dados.
    """
    # Prioridade 1: Variáveis de Ambiente
    value = os.environ.get(key.upper()) # Ex: 'barato_api_key' -> 'BARATO_API_KEY'
    if value:
        return value

    # Prioridade 2: Banco de Dados (como fallback)
    config_entry = AdminConfig.query.filter_by(key=key).first()
    if config_entry:
        return config_entry.value
        
    return None
