from app import app
from db import init_db
from test_data import create_test_data

with app.app_context():
    init_db(app)
    create_test_data()
    print("Banco de dados inicializado e dados de teste criados com sucesso!") 