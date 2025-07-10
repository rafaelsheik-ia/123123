# Arquivo: src/routes/services.py (Versão Final Corrigida)

from flask import Blueprint, jsonify
from src.models.user import Service, db
from src.routes.user import login_required, admin_required

# Importa nossa nova função de configuração e a classe da API
from src.config import get_config
from src.services.barato_social import BaratoSocialAPI

services_bp = Blueprint('services', __name__)

@services_bp.route('/services', methods=['GET'])
@login_required
def get_services():
    """
    Lista os serviços disponíveis do banco de dados.
    Se o banco estiver vazio, tenta sincronizar com a API primeiro.
    """
    # USA A NOVA FUNÇÃO get_config para a margem de lucro
    profit_margin = float(get_config('profit_margin') or 0)
    
    services = Service.query.filter_by(is_active=True).all()
    
    # Se não há serviços no nosso banco, tenta uma sincronização automática
    if not services:
        # USA A NOVA FUNÇÃO get_config para a chave da API
        api_key = get_config('barato_api_key')
        if api_key:
            try:
                api = BaratoSocialAPI(api_key)
                services_data = api.services()
                if services_data and isinstance(services_data, list):
                    for service_data in services_data:
                        # Evita adicionar serviços duplicados
                        exists = Service.query.filter_by(service_id=service_data['service']).first()
                        if not exists:
                            new_service = Service(
                                service_id=service_data['service'],
                                name=service_data['name'],
                                type=service_data['type'],
                                rate=float(service_data['rate']),
                                min=int(service_data['min']),
                                max=int(service_data['max']),
                                category=service_data.get('category', ''),
                                description=service_data.get('description', '')
                            )
                            db.session.add(new_service)
                    db.session.commit()
                    # Recarrega os serviços do banco após a sincronização
                    services = Service.query.filter_by(is_active=True).all()
            except Exception as e:
                print(f"Falha na sincronização automática de serviços: {e}")
                return jsonify({"error": "Não foi possível carregar os serviços do fornecedor."}), 500

    # Retorna a lista de serviços com o preço final calculado
    return jsonify([service.to_dict(profit_margin) for service in services])

@services_bp.route('/services/categories', methods=['GET'])
@login_required
def get_categories():
    """Lista todas as categorias de serviços distintas."""
    categories = db.session.query(Service.category).filter(
        Service.is_active == True,
        Service.category != None,
        Service.category != ''
    ).distinct().order_by(Service.category).all()
    
    return jsonify([cat[0] for cat in categories])

# A rota de sincronização já estava no admin.py, que é o lugar mais correto para ela.
# Se você quiser mantê-la aqui também, lembre-se de usar o get_config.
# Por padrão, centralizar ações de admin no admin_bp é uma boa prática.

@services_bp.route('/services/<int:service_id>', methods=['GET'])
@login_required
def get_service_details(service_id):
    """Obtém detalhes de um serviço específico."""
    service = Service.query.get_or_404(service_id)
    profit_margin = float(get_config('profit_margin') or 0)
    return jsonify(service.to_dict(profit_margin))

@services_bp.route('/services/<int:service_id>/toggle', methods=['POST'])
@admin_required
def toggle_service_status(service_id):
    """Ativa ou desativa um serviço para os clientes."""
    service = Service.query.get_or_404(service_id)
    service.is_active = not service.is_active
    db.session.commit()
    
    profit_margin = float(get_config('profit_margin') or 0)
    return jsonify({
        'message': f'Serviço {"ativado" if service.is_active else "desativado"} com sucesso.',
        'service': service.to_dict(profit_margin)
    })
