import os
from datetime import timedelta

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bus_monitoring.db')
    
    # Configurações de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configurações de planos
    SUBSCRIPTION_PLANS = {
        'basic': {
            'name': 'Básico',
            'price': 99.90,
            'max_buses': 5,
            'features': [
                'Gestão de ônibus',
                'Gestão de rotas',
                'Gestão de motoristas',
                'Gestão de monitores',
                'Relatórios básicos'
            ]
        },
        'professional': {
            'name': 'Profissional',
            'price': 199.90,
            'max_buses': 15,
            'features': [
                'Todas as features do plano Básico',
                'Gestão de alunos',
                'Gestão de escolas',
                'Relatórios avançados',
                'Suporte prioritário'
            ]
        },
        'enterprise': {
            'name': 'Empresarial',
            'price': 499.90,
            'max_buses': 50,
            'features': [
                'Todas as features do plano Profissional',
                'API de integração',
                'Personalização de relatórios',
                'Suporte 24/7',
                'Treinamento da equipe'
            ]
        }
    } 