import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
from db import get_db

def create_test_data():
    db = get_db()
    
    # Criar empresa de teste
    db.execute(
        '''INSERT INTO company (name, cnpj, address, phone, email, created_at) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        ('Empresa Teste', '12345678901234', 'Rua Teste, 123', '(11) 1234-5678', 'contato@empresateste.com', datetime.now())
    )
    db.commit()
    
    company_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Criar usuário de teste
    db.execute(
        '''INSERT INTO user (email, password, name, role, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        ('admin@teste.com', generate_password_hash('123456'), 'Administrador', 'admin', company_id, datetime.now())
    )
    db.commit()
    
    # Criar ônibus de teste
    db.execute(
        '''INSERT INTO bus (plate, model, fuel_efficiency, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?)''',
        ('ABC1234', 'Mercedes-Benz O500', 3.5, company_id, datetime.now())
    )
    db.commit()
    
    # Criar escola de teste
    db.execute(
        '''INSERT INTO school (name, address, phone, email, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        ('Escola Teste', 'Rua da Escola, 456', '(11) 9876-5432', 'contato@escolateste.com', company_id, datetime.now())
    )
    db.commit()
    
    # Criar rota de teste
    bus_id = db.execute('SELECT id FROM bus WHERE company_id = ?', (company_id,)).fetchone()[0]
    db.execute(
        '''INSERT INTO route (name, distance, bus_id, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?)''',
        ('Rota Teste', 50.0, bus_id, company_id, datetime.now())
    )
    db.commit()
    
    # Criar parada de teste
    route_id = db.execute('SELECT id FROM route WHERE company_id = ?', (company_id,)).fetchone()[0]
    db.execute(
        '''INSERT INTO stop (name, route_id, company_id, created_at) 
           VALUES (?, ?, ?, ?)''',
        ('Parada Teste', route_id, company_id, datetime.now())
    )
    db.commit()
    
    # Criar aluno de teste
    school_id = db.execute('SELECT id FROM school WHERE company_id = ?', (company_id,)).fetchone()[0]
    stop_id = db.execute('SELECT id FROM stop WHERE route_id = ?', (route_id,)).fetchone()[0]
    db.execute(
        '''INSERT INTO student (name, school_id, stop_id, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?)''',
        ('Aluno Teste', school_id, stop_id, company_id, datetime.now())
    )
    db.commit()
    
    # Criar motorista de teste
    db.execute(
        '''INSERT INTO driver (name, salary, bus_id, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?)''',
        ('Motorista Teste', 2500.00, bus_id, company_id, datetime.now())
    )
    db.commit()
    
    # Criar monitor de teste
    db.execute(
        '''INSERT INTO monitor (name, salary, bus_id, company_id, created_at) 
           VALUES (?, ?, ?, ?, ?)''',
        ('Monitor Teste', 1500.00, bus_id, company_id, datetime.now())
    )
    db.commit()

if __name__ == '__main__':
    create_test_data()
    print("Dados de teste criados com sucesso!") 