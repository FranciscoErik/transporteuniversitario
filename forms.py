from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, IntegerField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='O email é obrigatório'),
        Email(message='Digite um email válido')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='A senha é obrigatória')
    ])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Nome da Empresa', validators=[DataRequired(), Length(min=3, max=100)])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)])
    phone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Endereço', validators=[DataRequired(), Length(min=10, max=200)])

class BusForm(FlaskForm):
    plate = StringField('Placa', validators=[DataRequired(), Length(min=7, max=8)])
    model = StringField('Modelo', validators=[DataRequired(), Length(min=3, max=50)])
    fuel_efficiency = FloatField('Eficiência de Combustível (km/l)', 
                               validators=[DataRequired(), NumberRange(min=0.1, max=50.0)])

class RouteForm(FlaskForm):
    name = StringField('Nome da Rota', validators=[DataRequired(), Length(min=3, max=100)])
    distance = FloatField('Distância (km)', validators=[DataRequired(), NumberRange(min=0.1)])
    bus_id = SelectField('Ônibus', coerce=int, validators=[DataRequired()])

class StopForm(FlaskForm):
    name = StringField('Nome do Ponto', validators=[DataRequired(), Length(min=3, max=100)])
    route_id = SelectField('Rota', coerce=int, validators=[DataRequired()])

class StudentForm(FlaskForm):
    name = StringField('Nome do Aluno', validators=[DataRequired(), Length(min=3, max=100)])
    school_id = SelectField('Escola', coerce=int, validators=[DataRequired()])
    stop_id = SelectField('Ponto de Parada', coerce=int, validators=[DataRequired()])

class DriverForm(FlaskForm):
    name = StringField('Nome do Motorista', validators=[DataRequired(), Length(min=3, max=100)])
    salary = FloatField('Salário', validators=[DataRequired(), NumberRange(min=0.0)])
    bus_id = SelectField('Ônibus', coerce=int, validators=[Optional()])

class MonitorForm(FlaskForm):
    name = StringField('Nome do Monitor', validators=[DataRequired(), Length(min=3, max=100)])
    salary = FloatField('Salário', validators=[DataRequired(), NumberRange(min=0.0)])
    bus_id = SelectField('Ônibus', coerce=int, validators=[Optional()])

class DailyOperationForm(FlaskForm):
    date = DateField('Data', validators=[DataRequired()], default=datetime.now)
    bus_id = SelectField('Ônibus', coerce=int, validators=[DataRequired()])
    fuel_price = FloatField('Preço do Combustível (R$/l)', 
                          validators=[DataRequired(), NumberRange(min=0.1)])

class CompanyForm(FlaskForm):
    name = StringField('Nome da Empresa', validators=[DataRequired(), Length(min=3, max=100)])
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)])
    phone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Endereço', validators=[DataRequired(), Length(min=10, max=200)])

class SubscriptionForm(FlaskForm):
    plan_type = SelectField('Plano', 
                          choices=[('basic', 'Básico'), 
                                 ('professional', 'Profissional'),
                                 ('enterprise', 'Empresarial')],
                          validators=[DataRequired()])
    start_date = DateField('Data de Início', validators=[DataRequired()], default=datetime.now)
    payment_method = SelectField('Método de Pagamento',
                               choices=[('credit_card', 'Cartão de Crédito'),
                                      ('bank_transfer', 'Transferência Bancária'),
                                      ('pix', 'PIX')],
                               validators=[DataRequired()])

class ProfileForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nova Senha', 
                                   validators=[EqualTo('new_password', message='As senhas devem ser iguais')])

class SchoolForm(FlaskForm):
    name = StringField('Nome da Escola', validators=[DataRequired(), Length(min=3, max=100)])
    address = TextAreaField('Endereço', validators=[DataRequired(), Length(min=10, max=200)])
    phone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()]) 