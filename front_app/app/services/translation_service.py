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
            "english_subtitle": "زیرنویس انگلیسی",
            "persian_subtitle": "زیرنویس پارسی",
            "persian_dubbing": "دوبله پارسی",
            "persian_dubbing_english_subtitle": "دوبله پارسی با زیرنویس انگلیسی",
            "persian_dubbing_persian_subtitle": "دوبله پارسی با زیرنویس پارسی"
        }

    def get_prices(self,data , cookies):
        try:
            response = requests.post(
                f"{self.backend_url}/translate/prices",
                json = {
                    data.get('duration'),
                    data.get('resolution')
                },
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
            response_data = response.json()
            if response.status_code == 200 and response_data.get('success'):
                return self.download_file(response_data.get('data').get('downloadUrl') , cookies=cookies)
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get download URL"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def download_file(self, download_url, cookies):
        try:
            response = requests.get(
                download_url,
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