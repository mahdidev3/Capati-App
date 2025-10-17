from flask import Blueprint, request, jsonify, make_response, redirect, url_for
from app.services.auth_service import AuthService
from app.services.translation_service import TranslationService
from app.services.payment_service import PaymentService

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Authentication endpoints
@api_bp.route('/login', methods=['POST'])
def api_login():
    auth_service = AuthService()
    return auth_service.login(request.json)

@api_bp.route('/login-otp', methods=['POST'])
def api_login_otp():
    auth_service = AuthService()
    return auth_service.request_otp(request.json)

@api_bp.route('/login-otp-verify', methods=['POST'])
def api_login_otp_verify():
    auth_service = AuthService()
    return auth_service.verify_otp(request.json)

@api_bp.route('/signup-otp', methods=['POST'])
def api_signup_otp():
    auth_service = AuthService()
    return auth_service.signup_request_otp(request.json)

@api_bp.route('/signup-complete', methods=['POST'])
def api_signup_complete():
    auth_service = AuthService()
    return auth_service.signup_complete(request.json)

@api_bp.route('/logout', methods=['POST'])
def api_logout():
    auth_service = AuthService()
    return auth_service.logout()

# Account endpoints
@api_bp.route('/account', methods=['GET'])
def api_account():
    auth_service = AuthService()
    return auth_service.get_account(request.cookies)

@api_bp.route('/account/profile', methods=['PUT'])
def api_update_profile():
    auth_service = AuthService()
    return auth_service.update_profile(request.json, request.cookies)

@api_bp.route('/account/password', methods=['PUT'])
def api_change_password():
    auth_service = AuthService()
    return auth_service.change_password(request.json, request.cookies)

@api_bp.route('/account/mobile-change-otp', methods=['POST'])
def api_mobile_change_otp():
    auth_service = AuthService()
    return auth_service.request_mobile_change_otp(request.json, request.cookies)

@api_bp.route('/account/mobile', methods=['PUT'])
def api_change_mobile():
    auth_service = AuthService()
    return auth_service.change_mobile(request.json, request.cookies)

# Dashboard endpoints
@api_bp.route('/dashboard', methods=['GET'])
def api_dashboard():
    translation_service = TranslationService()
    return translation_service.get_dashboard_data(request.cookies)

# Wallet endpoints
@api_bp.route('/wallet', methods=['GET'])
def api_wallet():
    payment_service = PaymentService()
    return payment_service.get_wallet(request.cookies)

@api_bp.route('/wallet/payment', methods=['POST'])
def api_initiate_payment():
    payment_service = PaymentService()
    return payment_service.initiate_payment(request.json, request.cookies)

# Translation endpoints
@api_bp.route('/translate/options', methods=['POST'])
def api_translate_options():
    translation_service = TranslationService()
    return translation_service.get_options(request.cookies)

@api_bp.route('/translate/start', methods=['POST'])
def api_translate_start():
    translation_service = TranslationService()
    return translation_service.start_translation(request.json, request.cookies)

@api_bp.route('/translate/status/<project_id>', methods=['GET'])
def api_translate_status(project_id):
    translation_service = TranslationService()
    return translation_service.get_status(project_id, request.cookies)

@api_bp.route('/translate/download/<project_id>', methods=['GET'])
def api_translate_download(project_id):
    translation_service = TranslationService()
    return translation_service.get_download_url(project_id, request.cookies)

@api_bp.route('/translate/download/<project_id>/file', methods=['GET'])
def api_translate_download_file(project_id):
    translation_service = TranslationService()
    return translation_service.download_file(project_id, request.args.get('token'), request.cookies)