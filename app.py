from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_required, current_user
from datetime import datetime
import os
import sqlite3
from config import Config
from auth import auth as auth_blueprint
from utils import (
    generate_pdf_report, generate_excel_report, format_currency, create_upload_folder,
    generate_pdf_students_report, generate_excel_students_report
)
from db import get_db, init_db, init_app, close_db
from models import User
from forms import BusForm, SchoolForm

app = Flask(__name__)
app.config.from_object(Config)

# Inicialização do banco de dados
if not os.path.exists(app.config['DATABASE']):
    with app.app_context():
        init_db(app)

# Inicialização do gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Registro dos blueprints
app.register_blueprint(auth_blueprint)

# Criação da pasta de uploads
UPLOAD_FOLDER = create_upload_folder()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicialização do banco de dados
init_app(app)

# Registrar função para fechar conexão com o banco
app.teardown_appcontext(close_db)

@app.route('/')
@login_required
def index():
    db = get_db()
    buses = db.execute('SELECT * FROM bus').fetchall()
    routes = db.execute('''
        SELECT r.*, b.plate as bus_plate, b.model as bus_model 
        FROM route r 
        LEFT JOIN bus b ON r.bus_id = b.id
    ''').fetchall()
    return render_template('index.html', buses=buses, routes=routes)

@app.route('/buses')
@login_required
def buses():
    db = get_db()
    buses = db.execute('''
        SELECT b.*, d.name as driver_name, m.name as monitor_name 
        FROM bus b 
        LEFT JOIN driver d ON b.id = d.bus_id 
        LEFT JOIN monitor m ON b.id = m.bus_id 
        WHERE b.company_id = ?
        ORDER BY b.plate
    ''', (current_user.company_id,)).fetchall()
    return render_template('buses.html', buses=buses)

@app.route('/buses/add', methods=['GET', 'POST'])
@login_required
def add_bus():
    if request.method == 'POST':
        plate = request.form.get('plate')
        model = request.form.get('model')
        fuel_efficiency = request.form.get('fuel_efficiency')
        
        if not all([plate, model, fuel_efficiency]):
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('add_bus'))
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO bus (plate, model, fuel_efficiency, company_id, created_at) VALUES (?, ?, ?, ?, ?)',
                (plate, model, fuel_efficiency, current_user.company_id, datetime.now())
            )
            db.commit()
            flash('Ônibus adicionado com sucesso!', 'success')
            return redirect(url_for('buses'))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar ônibus. Placa já existe.', 'error')
            return redirect(url_for('add_bus'))
    
    return render_template('buses_form.html', title='Adicionar Ônibus')

@app.route('/buses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bus(id):
    db = get_db()
    bus = db.execute('SELECT * FROM bus WHERE id = ? AND company_id = ?', 
                    (id, current_user.company_id)).fetchone()
    
    if bus is None:
        flash('Ônibus não encontrado.', 'error')
        return redirect(url_for('buses'))
    
    if request.method == 'POST':
        plate = request.form.get('plate')
        model = request.form.get('model')
        fuel_efficiency = request.form.get('fuel_efficiency')
        
        if not all([plate, model, fuel_efficiency]):
            flash('Todos os campos são obrigatórios.', 'error')
            return redirect(url_for('edit_bus', id=id))
        
        try:
            db.execute(
                'UPDATE bus SET plate = ?, model = ?, fuel_efficiency = ? WHERE id = ? AND company_id = ?',
                (plate, model, fuel_efficiency, id, current_user.company_id)
            )
            db.commit()
            flash('Ônibus atualizado com sucesso!', 'success')
            return redirect(url_for('buses'))
        except sqlite3.IntegrityError:
            flash('Erro ao atualizar ônibus. Placa já existe.', 'error')
            return redirect(url_for('edit_bus', id=id))
    
    return render_template('buses_form.html', bus=bus, title='Editar Ônibus')

@app.route('/buses/delete/<int:id>', methods=['POST'])
@login_required
def delete_bus(id):
    db = get_db()
    try:
        # Primeiro, verificar se o ônibus existe e pertence à empresa
        bus = db.execute('SELECT * FROM bus WHERE id = ? AND company_id = ?', 
                        (id, current_user.company_id)).fetchone()
        
        if not bus:
            flash('Ônibus não encontrado.', 'error')
            return redirect(url_for('buses'))
            
        # Verificar se o ônibus está associado a alguma rota
        routes = db.execute('SELECT COUNT(*) as count FROM route WHERE bus_id = ?', (id,)).fetchone()
        if routes['count'] > 0:
            flash('Não é possível remover o ônibus pois ele está associado a uma ou mais rotas.', 'error')
            return redirect(url_for('buses'))
            
        # Se não houver rotas associadas, deletar o ônibus
        db.execute('DELETE FROM bus WHERE id = ? AND company_id = ?', (id, current_user.company_id))
        db.commit()
        flash('Ônibus removido com sucesso!', 'success')
        return redirect(url_for('buses'))
    except Exception as e:
        db.rollback()
        flash(f'Erro ao remover ônibus: {str(e)}', 'error')
        return redirect(url_for('buses'))

@app.route('/routes')
@login_required
def routes():
    db = get_db()
    routes = db.execute('''
        SELECT r.*, b.plate as bus_plate, b.model as bus_model,
               (SELECT COUNT(*) FROM stop s WHERE s.route_id = r.id) as stops_count
        FROM route r 
        JOIN bus b ON r.bus_id = b.id 
        WHERE r.company_id = ?
        ORDER BY r.name
    ''', (current_user.company_id,)).fetchall()
    return render_template('routes.html', routes=routes)

@app.route('/routes/add', methods=['GET', 'POST'])
@login_required
def add_route():
    db = get_db()
    buses = db.execute('''
        SELECT id, plate, model 
        FROM bus 
        WHERE company_id = ? 
        AND id NOT IN (SELECT bus_id FROM route WHERE company_id = ?)
    ''', (current_user.company_id, current_user.company_id)).fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        distance = request.form['distance']
        bus_id = request.form['bus_id']
        
        try:
            db.execute(
                'INSERT INTO route (name, distance, bus_id, company_id, created_at) VALUES (?, ?, ?, ?, ?)',
                (name, distance, bus_id, current_user.company_id, datetime.now())
            )
            db.commit()
            flash('Rota adicionada com sucesso!', 'success')
            return redirect(url_for('routes'))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar rota.', 'error')
    
    return render_template('routes_form.html', buses=buses, title='Adicionar Rota')

@app.route('/routes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_route(id):
    db = get_db()
    route = db.execute('SELECT * FROM route WHERE id = ? AND company_id = ?', 
                      (id, current_user.company_id)).fetchone()
    
    if route is None:
        flash('Rota não encontrada.', 'error')
        return redirect(url_for('routes'))
    
    buses = db.execute('SELECT id, plate FROM bus WHERE company_id = ?', 
                      (current_user.company_id,)).fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        distance = request.form['distance']
        bus_id = request.form['bus_id']
        
        try:
            db.execute(
                'UPDATE route SET name = ?, distance = ?, bus_id = ? WHERE id = ?',
                (name, distance, bus_id, id)
            )
            db.commit()
            flash('Rota atualizada com sucesso!', 'success')
            return redirect(url_for('routes'))
        except sqlite3.IntegrityError:
            flash('Erro ao atualizar rota.', 'error')
    
    return render_template('routes_form.html', route=route, buses=buses, title='Editar Rota')

@app.route('/routes/delete/<int:id>', methods=['POST'])
@login_required
def delete_route(id):
    db = get_db()
    try:
        # Primeiro, verificar se a rota existe e pertence à empresa
        route = db.execute('SELECT * FROM route WHERE id = ? AND company_id = ?', 
                         (id, current_user.company_id)).fetchone()
        
        if not route:
            flash('Rota não encontrada.', 'error')
            return redirect(url_for('routes'))
            
        # Verificar se existem alunos associados
        students = db.execute('SELECT COUNT(*) as count FROM student WHERE route_id = ?', (id,)).fetchone()
        if students['count'] > 0:
            flash('Não é possível remover a rota pois existem alunos associados a ela.', 'error')
            return redirect(url_for('routes'))
            
        # Se não houver alunos associados, deletar a rota
        db.execute('DELETE FROM route WHERE id = ?', (id,))
        db.commit()
        flash('Rota removida com sucesso!', 'success')
        return redirect(url_for('routes'))
    except Exception as e:
        flash(f'Erro ao remover rota: {str(e)}', 'error')
        return redirect(url_for('routes'))

@app.route('/stops')
@login_required
def stops():
    db = get_db()
    route_id = request.args.get('route_id', type=int)
    
    if not route_id:
        flash('Rota não especificada.', 'error')
        return redirect(url_for('routes'))
    
    route = db.execute('SELECT * FROM route WHERE id = ? AND company_id = ?', 
                      (route_id, current_user.company_id)).fetchone()
    
    if not route:
        flash('Rota não encontrada.', 'error')
        return redirect(url_for('routes'))
    
    stops = db.execute('''
        SELECT s.*, r.name as route_name 
        FROM stop s 
        JOIN route r ON s.route_id = r.id 
        WHERE s.route_id = ? AND r.company_id = ?
    ''', (route_id, current_user.company_id)).fetchall()
    
    return render_template('stops.html', stops=stops, route=route)

@app.route('/stops/add', methods=['GET', 'POST'])
@login_required
def add_stop():
    route_id = request.args.get('route_id', type=int)
    
    if not route_id:
        flash('Rota não especificada.', 'error')
        return redirect(url_for('routes'))
    
    db = get_db()
    route = db.execute('''
        SELECT r.*, b.plate as bus_plate, b.model as bus_model 
        FROM route r 
        JOIN bus b ON r.bus_id = b.id 
        WHERE r.id = ? AND r.company_id = ?
    ''', (route_id, current_user.company_id)).fetchone()
    
    if not route:
        flash('Rota não encontrada.', 'error')
        return redirect(url_for('routes'))
    
    if request.method == 'POST':
        name = request.form['name']
        
        try:
            db.execute(
                'INSERT INTO stop (name, route_id, company_id, created_at) VALUES (?, ?, ?, ?)',
                (name, route_id, current_user.company_id, datetime.now())
            )
            db.commit()
            flash('Ponto de parada adicionado com sucesso!', 'success')
            return redirect(url_for('stops', route_id=route_id))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar ponto de parada.', 'error')
    
    return render_template('stops_form.html', route=route, title='Adicionar Ponto de Parada')

@app.route('/stops/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stop(id):
    db = get_db()
    stop = db.execute('''
        SELECT s.*, r.id as route_id, r.name as route_name, b.plate as bus_plate, b.model as bus_model 
        FROM stop s 
        JOIN route r ON s.route_id = r.id 
        JOIN bus b ON r.bus_id = b.id
        WHERE s.id = ? AND r.company_id = ?
    ''', (id, current_user.company_id)).fetchone()
    
    if stop is None:
        flash('Ponto de parada não encontrado.', 'error')
        return redirect(url_for('routes'))
    
    if request.method == 'POST':
        name = request.form['name']
        
        try:
            db.execute(
                'UPDATE stop SET name = ? WHERE id = ?',
                (name, id)
            )
            db.commit()
            flash('Ponto de parada atualizado com sucesso!', 'success')
            return redirect(url_for('stops', route_id=stop['route_id']))
        except sqlite3.IntegrityError:
            flash('Erro ao atualizar ponto de parada.', 'error')
    
    return render_template('stops_form.html', stop=stop, route=stop, title='Editar Ponto de Parada')

@app.route('/stops/delete/<int:id>', methods=['POST'])
@login_required
def delete_stop(id):
    db = get_db()
    try:
        # Primeiro, obter o route_id antes de deletar
        stop = db.execute('''
            SELECT s.*, r.id as route_id 
            FROM stop s 
            JOIN route r ON s.route_id = r.id 
            WHERE s.id = ? AND r.company_id = ?
        ''', (id, current_user.company_id)).fetchone()
        
        if not stop:
            flash('Ponto de parada não encontrado.', 'error')
            return redirect(url_for('routes'))
            
        # Verificar se existem alunos associados
        students = db.execute('SELECT COUNT(*) as count FROM student WHERE stop_id = ?', (id,)).fetchone()
        if students['count'] > 0:
            flash('Não é possível remover o ponto de parada pois existem alunos associados a ele.', 'error')
            return redirect(url_for('stops', route_id=stop['route_id']))
            
        # Se não houver alunos associados, deletar o ponto de parada
        db.execute('DELETE FROM stop WHERE id = ?', (id,))
        db.commit()
        flash('Ponto de parada removido com sucesso!', 'success')
        return redirect(url_for('stops', route_id=stop['route_id']))
    except Exception as e:
        flash(f'Erro ao remover ponto de parada: {str(e)}', 'error')
        return redirect(url_for('routes'))

@app.route('/financial')
@login_required
def financial():
    db = get_db()
    operations = db.execute('''
        SELECT o.*, b.plate as bus_plate, b.model as bus_model 
        FROM daily_operation o 
        JOIN bus b ON o.bus_id = b.id 
        WHERE o.company_id = ?
        ORDER BY o.date DESC
    ''', (current_user.company_id,)).fetchall()
    return render_template('financial.html', operations=operations)

@app.route('/financial/calculate', methods=['GET', 'POST'])
@login_required
def calculate_daily_cost():
    db = get_db()
    buses = db.execute('SELECT id, plate, fuel_efficiency FROM bus WHERE company_id = ?', 
                      (current_user.company_id,)).fetchall()
    
    if request.method == 'POST':
        try:
            bus_id = request.form['bus_id']
            date = request.form['date']
            distance = float(request.form['distance'])
            fuel_price = float(request.form['fuel_price'])
            fuel_cost = float(request.form['fuel_cost'])
            driver_salary = float(request.form['driver_salary'])
            monitor_salary = float(request.form['monitor_salary'])
            
            # Validar se o ônibus pertence à empresa do usuário
            bus = db.execute('SELECT id, fuel_efficiency FROM bus WHERE id = ? AND company_id = ?',
                           (bus_id, current_user.company_id)).fetchone()
            if not bus:
                flash('Ônibus inválido.', 'error')
                return render_template('financial_form.html', buses=buses)
            
            # Validar o cálculo do custo do combustível
            expected_fuel_cost = (distance / bus['fuel_efficiency']) * fuel_price
            if abs(fuel_cost - expected_fuel_cost) > 0.01:  # Permitir pequena diferença por causa de arredondamento
                flash('Erro no cálculo do custo do combustível.', 'error')
                return render_template('financial_form.html', buses=buses)
            
            total_cost = fuel_cost + driver_salary + monitor_salary
            
            db.execute(
                '''INSERT INTO daily_operation 
                   (date, bus_id, distance, fuel_price, fuel_cost, driver_salary, monitor_salary, total_cost, company_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (date, bus_id, distance, fuel_price, fuel_cost, driver_salary, monitor_salary, total_cost, current_user.company_id)
            )
            db.commit()
            flash('Custo diário registrado com sucesso!', 'success')
            return redirect(url_for('financial'))
        except ValueError:
            flash('Por favor, insira valores numéricos válidos.', 'error')
        except sqlite3.IntegrityError as e:
            flash(f'Erro ao registrar custo diário: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')
    
    return render_template('financial_form.html', buses=buses, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/financial/report/<format>')
@login_required
def generate_report(format):
    db = get_db()
    operations = db.execute('''
        SELECT o.*, b.plate as bus_plate 
        FROM daily_operation o 
        JOIN bus b ON o.bus_id = b.id 
        WHERE b.company_id = ?
    ''', (current_user.company_id,)).fetchall()
    
    if format == 'pdf':
        buffer = generate_pdf_report(operations)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    elif format == 'excel':
        buffer = generate_excel_report(operations)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    else:
        flash('Formato de relatório inválido.', 'error')
        return redirect(url_for('financial'))

@app.route('/students')
@login_required
def students():
    db = get_db()
    route_id = request.args.get('route_id', type=int)
    
    if not route_id:
        flash('Rota não especificada.', 'error')
        return redirect(url_for('routes'))
    
    route = db.execute('''
        SELECT r.*, b.plate as bus_plate, b.model as bus_model 
        FROM route r 
        JOIN bus b ON r.bus_id = b.id 
        WHERE r.id = ? AND r.company_id = ?
    ''', (route_id, current_user.company_id)).fetchone()
    
    if not route:
        flash('Rota não encontrada.', 'error')
        return redirect(url_for('routes'))
    
    students = db.execute('''
        SELECT s.*, sc.name as school_name, st.name as stop_name 
        FROM student s 
        JOIN school sc ON s.school_id = sc.id 
        JOIN stop st ON s.stop_id = st.id 
        WHERE st.route_id = ? AND sc.company_id = ?
        ORDER BY s.name
    ''', (route_id, current_user.company_id)).fetchall()
    
    return render_template('students.html', students=students, route=route)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    db = get_db()
    route_id = request.args.get('route_id', type=int)
    
    if not route_id:
        flash('Rota não especificada.', 'error')
        return redirect(url_for('routes'))
    
    route = db.execute('SELECT * FROM route WHERE id = ? AND company_id = ?', 
                      (route_id, current_user.company_id)).fetchone()
    
    if not route:
        flash('Rota não encontrada.', 'error')
        return redirect(url_for('routes'))
    
    schools = db.execute('SELECT * FROM school WHERE company_id = ?', 
                        (current_user.company_id,)).fetchall()
    stops = db.execute('SELECT * FROM stop WHERE route_id = ?', (route_id,)).fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        school_id = request.form.get('school_id')
        stop_id = request.form.get('stop_id')
        
        if not all([name, school_id, stop_id]):
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('students_form.html', 
                                schools=schools, 
                                stops=stops, 
                                route_id=route_id,
                                title='Adicionar Aluno')
        
        try:
            db.execute(
                'INSERT INTO student (name, school_id, stop_id, company_id, created_at) VALUES (?, ?, ?, ?, ?)',
                (name, school_id, stop_id, current_user.company_id, datetime.now())
            )
            db.commit()
            flash('Aluno adicionado com sucesso!', 'success')
            return redirect(url_for('students', route_id=route_id))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar aluno.', 'error')
    
    return render_template('students_form.html', 
                         schools=schools, 
                         stops=stops, 
                         route_id=route_id,
                         title='Adicionar Aluno')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    db = get_db()
    student = db.execute('''
        SELECT s.*, st.route_id 
        FROM student s 
        JOIN stop st ON s.stop_id = st.id 
        WHERE s.id = ? AND s.company_id = ?
    ''', (id, current_user.company_id)).fetchone()
    
    if student is None:
        flash('Aluno não encontrado.', 'error')
        return redirect(url_for('routes'))
    
    schools = db.execute('SELECT * FROM school WHERE company_id = ?', 
                        (current_user.company_id,)).fetchall()
    routes = db.execute('''
        SELECT r.*, b.plate as bus_plate 
        FROM route r 
        JOIN bus b ON r.bus_id = b.id 
        WHERE r.company_id = ?
    ''', (current_user.company_id,)).fetchall()
    stops = db.execute('SELECT * FROM stop WHERE route_id = ?', 
                      (student['route_id'],)).fetchall()
    
    if request.method == 'POST':
        name = request.form['name']
        school_id = request.form['school_id']
        stop_id = request.form['stop_id']
        
        try:
            db.execute(
                'UPDATE student SET name = ?, school_id = ?, stop_id = ? WHERE id = ? AND company_id = ?',
                (name, school_id, stop_id, id, current_user.company_id)
            )
            db.commit()
            flash('Aluno atualizado com sucesso!', 'success')
            return redirect(url_for('students', route_id=student['route_id']))
        except sqlite3.IntegrityError:
            flash('Erro ao atualizar aluno.', 'error')
    
    return render_template('students_form.html', 
                         student=student,
                         schools=schools, 
                         routes=routes, 
                         stops=stops,
                         route_id=student['route_id'],
                         title='Editar Aluno')

@app.route('/students/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    db = get_db()
    try:
        # Primeiro, obter o route_id antes de deletar
        student = db.execute('''
            SELECT s.*, r.id as route_id 
            FROM student s 
            JOIN stop st ON s.stop_id = st.id 
            JOIN route r ON st.route_id = r.id 
            WHERE s.id = ? AND r.company_id = ?
        ''', (id, current_user.company_id)).fetchone()
        
        if not student:
            flash('Aluno não encontrado.', 'error')
            return redirect(url_for('routes'))
            
        db.execute('DELETE FROM student WHERE id = ?', (id,))
        db.commit()
        flash('Aluno removido com sucesso!', 'success')
        return redirect(url_for('students', route_id=student['route_id']))
    except sqlite3.Error as e:
        flash(f'Erro ao remover aluno: {str(e)}', 'error')
        if student:
            return redirect(url_for('students', route_id=student['route_id']))
    return redirect(url_for('routes'))

@app.route('/api/stops/<int:route_id>')
@login_required
def get_stops(route_id):
    db = get_db()
    stops = db.execute('SELECT * FROM stop WHERE route_id = ?', (route_id,)).fetchall()
    return jsonify([dict(stop) for stop in stops])

@app.route('/schools')
@login_required
def schools():
    db = get_db()
    schools = db.execute('''
        SELECT s.*, 
               (SELECT COUNT(*) FROM student st WHERE st.school_id = s.id) as students_count
        FROM school s 
        WHERE s.company_id = ?
        ORDER BY s.name
    ''', (current_user.company_id,)).fetchall()
    return render_template('schools.html', schools=schools)

@app.route('/schools/add', methods=['GET', 'POST'])
@login_required
def add_school():
    form = SchoolForm()
    if form.validate_on_submit():
        db = get_db()
        try:
            db.execute(
                '''INSERT INTO school (name, address, phone, email, company_id, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (form.name.data, form.address.data, form.phone.data, form.email.data, 
                 current_user.company_id, datetime.now())
            )
            db.commit()
            flash('Escola adicionada com sucesso!', 'success')
            return redirect(url_for('schools'))
        except sqlite3.IntegrityError:
            flash('Erro ao adicionar escola.', 'error')
    
    return render_template('schools_form.html', form=form, title='Adicionar Escola')

@app.route('/schools/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_school(id):
    db = get_db()
    school = db.execute('SELECT * FROM school WHERE id = ? AND company_id = ?', 
                       (id, current_user.company_id)).fetchone()
    
    if school is None:
        flash('Escola não encontrada.', 'error')
        return redirect(url_for('schools'))
    
    form = SchoolForm()
    if form.validate_on_submit():
        try:
            db.execute(
                '''UPDATE school 
                   SET name = ?, address = ?, phone = ?, email = ? 
                   WHERE id = ? AND company_id = ?''',
                (form.name.data, form.address.data, form.phone.data, form.email.data, 
                 id, current_user.company_id)
            )
            db.commit()
            flash('Escola atualizada com sucesso!', 'success')
            return redirect(url_for('schools'))
        except sqlite3.IntegrityError:
            flash('Erro ao atualizar escola.', 'error')
    elif request.method == 'GET':
        form.name.data = school['name']
        form.address.data = school['address']
        form.phone.data = school['phone']
        form.email.data = school['email']
    
    return render_template('schools_form.html', form=form, school=school, title='Editar Escola')

@app.route('/schools/delete/<int:id>', methods=['POST'])
@login_required
def delete_school(id):
    db = get_db()
    try:
        # Primeiro, verificar se a escola existe e pertence à empresa
        school = db.execute('SELECT * FROM school WHERE id = ? AND company_id = ?', 
                          (id, current_user.company_id)).fetchone()
        
        if not school:
            flash('Escola não encontrada.', 'error')
            return redirect(url_for('schools'))
            
        # Verificar se existem alunos associados
        students = db.execute('SELECT COUNT(*) as count FROM student WHERE school_id = ?', (id,)).fetchone()
        if students['count'] > 0:
            flash('Não é possível remover a escola pois existem alunos associados a ela.', 'error')
            return redirect(url_for('schools'))
            
        # Se não houver alunos associados, deletar a escola
        db.execute('DELETE FROM school WHERE id = ? AND company_id = ?', (id, current_user.company_id))
        db.commit()
        flash('Escola removida com sucesso!', 'success')
        return redirect(url_for('schools'))
    except Exception as e:
        db.rollback()
        flash(f'Erro ao remover escola: {str(e)}', 'error')
        return redirect(url_for('schools'))

@app.route('/students/report/<format>')
@login_required
def generate_students_report(format):
    db = get_db()
    route_id = request.args.get('route_id', type=int)
    
    if not route_id:
        flash('Rota não especificada.', 'error')
        return redirect(url_for('routes'))
    
    students = db.execute('''
        SELECT s.*, sc.name as school_name, st.name as stop_name, r.name as route_name, b.plate as bus_plate
        FROM student s 
        JOIN school sc ON s.school_id = sc.id 
        JOIN stop st ON s.stop_id = st.id 
        JOIN route r ON st.route_id = r.id
        JOIN bus b ON r.bus_id = b.id
        WHERE st.route_id = ? AND s.company_id = ?
        ORDER BY s.name
    ''', (route_id, current_user.company_id)).fetchall()
    
    if format == 'pdf':
        buffer = generate_pdf_students_report(students)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    elif format == 'excel':
        buffer = generate_excel_students_report(students)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_alunos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    else:
        flash('Formato de relatório inválido.', 'error')
        return redirect(url_for('students', route_id=route_id))

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        init_db(app)
    app.run(debug=True) 