import requests
from flask import jsonify, redirect, url_for
from app.config import Config

class TranslationService:
    def __init__(self):
        self.backend_url = Config.BACKEND_URL
    
    def get_dashboard_data(self, cookies=None):
        try:
            response = requests.get(
                f"{self.backend_url}/dashboard",
                cookies=cookies or {}
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return None
            else:
                return {"success": False, "message": "Failed to get dashboard data"}
        except requests.exceptions.RequestException:
            return {"success": False, "message": "Server error"}
    
    def get_operation_types(self):
        # This should be fetched from the backend in a real implementation
        return {
            "english_subtitle": "English Subtitle",
            "persian_subtitle": "Persian Subtitle",
            "persian_dubbing": "Persian Dubbing",
            "persian_dubbing_english_subtitle": "Persian Dubbing with English Subtitle",
            "persian_dubbing_persian_subtitle": "Persian Dubbing with Persian Subtitle"
        }
    
    def get_options(self, cookies):
        try:
            response = requests.post(
                f"{self.backend_url}/translate/options",
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get translation options"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def start_translation(self, data, cookies):
        video_size = data.get('videoSize')
        project_type = data.get('projectType')
        use_wallet_balance = data.get('useWalletBalance', True)

        try:
            response = requests.post(
                f"{self.backend_url}/translate/start",
                json={
                    "videoSize": video_size,
                    "projectType": project_type,
                    "useWalletBalance": use_wallet_balance
                },
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to start translation"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def get_status(self, project_id, cookies):
        try:
            response = requests.get(
                f"{self.backend_url}/translate/status/{project_id}",
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get translation status"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def get_download_url(self, project_id, cookies):
        try:
            response = requests.get(
                f"{self.backend_url}/translate/download/{project_id}",
                cookies=cookies
            )
            
            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get download URL"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def download_file(self, project_id, token, cookies):
        try:
            response = requests.get(
                f"{self.backend_url}/translate/download/{project_id}/file",
                params={"token": token},
                cookies=cookies
            )
            
            if response.status_code == 200:
                return response.content, response.status_code, dict(response.headers)
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to download file"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})