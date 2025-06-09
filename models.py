from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Company:
    def __init__(self, name, cnpj, address=None, phone=None, email=None):
        self.name = name
        self.cnpj = cnpj
        self.address = address
        self.phone = phone
        self.email = email
        self.created_at = datetime.now()

class User(UserMixin):
    def __init__(self, id, email, password, name, role, company_id, created_at):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.role = role
        self.company_id = company_id
        self.created_at = created_at

    @staticmethod
    def get(user_id):
        from db import get_db
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(
                id=user['id'],
                email=user['email'],
                password=user['password'],
                name=user['name'],
                role=user['role'],
                company_id=user['company_id'],
                created_at=user['created_at']
            )
        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Subscription:
    def __init__(self, company_id, plan_type, start_date, end_date, status='active'):
        self.company_id = company_id
        self.plan_type = plan_type
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.created_at = datetime.now()

    def is_active(self):
        return self.status == 'active' and datetime.now().date() <= self.end_date

class Bus:
    def __init__(self, plate, model, fuel_efficiency, company_id):
        self.plate = plate
        self.model = model
        self.fuel_efficiency = fuel_efficiency
        self.company_id = company_id
        self.created_at = datetime.now()

class Route:
    def __init__(self, name, distance, bus_id, company_id):
        self.name = name
        self.distance = distance
        self.bus_id = bus_id
        self.company_id = company_id
        self.created_at = datetime.now()

class Stop:
    def __init__(self, name, route_id, company_id):
        self.name = name
        self.route_id = route_id
        self.company_id = company_id
        self.created_at = datetime.now()

class Student:
    def __init__(self, name, school_id, stop_id, company_id):
        self.name = name
        self.school_id = school_id
        self.stop_id = stop_id
        self.company_id = company_id
        self.created_at = datetime.now()

class Driver:
    def __init__(self, name, salary, bus_id, company_id):
        self.name = name
        self.salary = salary
        self.bus_id = bus_id
        self.company_id = company_id
        self.created_at = datetime.now()

class Monitor:
    def __init__(self, name, salary, bus_id, company_id):
        self.name = name
        self.salary = salary
        self.bus_id = bus_id
        self.company_id = company_id
        self.created_at = datetime.now()

class DailyOperation:
    def __init__(self, date, bus_id, fuel_cost, driver_salary, monitor_salary, total_cost, company_id):
        self.date = date
        self.bus_id = bus_id
        self.fuel_cost = fuel_cost
        self.driver_salary = driver_salary
        self.monitor_salary = monitor_salary
        self.total_cost = total_cost
        self.company_id = company_id
        self.created_at = datetime.now() 