from flask import Blueprint, render_template, redirect, url_for , request
from app.services.translation_service import TranslationService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    translation_service = TranslationService()
    dashboard_data = translation_service.get_dashboard_data(request.cookies)
    print(dashboard_data.get('data').get('completedProjects'))
    if dashboard_data:
        if (dashboard_data.get('success' , False)):
            return render_template('dashboard/dashboard.html',
                                   context={
                                       'dashboard_data': dashboard_data.get('data'),
                                       'is_authenticated': True,
                                       'operation_types': translation_service.get_operation_types()
                                   })
        else:
            print(dashboard_data.get('message'))
            return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.login'))