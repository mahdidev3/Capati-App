from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/contact')
def contact():
    return render_template('pages/contact.html', context={'dashboard_data': {}, 'is_authenticated': False})