import requests
from flask import jsonify, redirect, url_for
from app.config import Config

class PaymentService:
    def __init__(self):
        self.backend_url = Config.BACKEND_URL
    
    def get_wallet(self, cookies):
        try:
            response = requests.get(
                f"{self.backend_url}/wallet",
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get wallet info"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def initiate_payment(self, data, cookies):
        amount = data.get('amount')

        try:
            response = requests.post(
                f"{self.backend_url}/wallet/payment",
                json={"amount": amount},
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to initiate payment"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})