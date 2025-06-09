from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import get_db
from models import User
from forms import LoginForm, RegistrationForm, ProfileForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember_me.data

        db = get_db()
        user_data = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if not user_data:
            flash('Por favor, verifique suas credenciais e tente novamente.', 'error')
            return redirect(url_for('auth.login'))

        user = User(
            id=user_data['id'],
            email=user_data['email'],
            password=user_data['password'],
            name=user_data['name'],
            role=user_data['role'],
            company_id=user_data['company_id'],
            created_at=user_data['created_at']
        )

        if not user.check_password(password):
            flash('Por favor, verifique suas credenciais e tente novamente.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        company_name = form.company_name.data
        company_cnpj = form.cnpj.data
        phone = form.phone.data
        address = form.address.data

        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user:
            flash('Email já registrado.', 'error')
            return redirect(url_for('auth.register'))

        try:
            # Criar empresa
            db.execute(
                '''INSERT INTO company (name, cnpj, phone, address, created_at) 
                   VALUES (?, ?, ?, ?, ?)''',
                (company_name, company_cnpj, phone, address, datetime.now())
            )
            db.commit()
            
            company_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            # Criar usuário
            db.execute(
                '''INSERT INTO user (email, password, name, role, company_id, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (email, generate_password_hash(password), name, 'admin', company_id, datetime.now())
            )
            db.commit()
            
            flash('Registro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.rollback()
            flash('Erro ao registrar. Por favor, tente novamente.', 'error')
            return redirect(url_for('auth.register'))

    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?', (current_user.id,)).fetchone()

        if not check_password_hash(user['password'], form.current_password.data):
            flash('Senha atual incorreta.', 'error')
            return redirect(url_for('auth.profile'))

        try:
            if form.new_password.data:
                db.execute(
                    'UPDATE user SET name = ?, password = ? WHERE id = ?',
                    (form.name.data, generate_password_hash(form.new_password.data), current_user.id)
                )
            else:
                db.execute(
                    'UPDATE user SET name = ? WHERE id = ?',
                    (form.name.data, current_user.id)
                )
            db.commit()
            flash('Perfil atualizado com sucesso!', 'success')
        except Exception as e:
            db.rollback()
            flash('Erro ao atualizar perfil.', 'error')

        return redirect(url_for('auth.profile'))
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template('profile.html', form=form) 