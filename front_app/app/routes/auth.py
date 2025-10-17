from flask import Blueprint, render_template, redirect, url_for, session, request
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html', context={'dashboard_data': {}, 'is_authenticated': False})

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html', context={'dashboard_data': {}, 'is_authenticated': False})

@auth_bp.route('/logout')
def logout():
    auth_service = AuthService()
    auth_service.logout()
    return redirect(url_for('auth.login'))