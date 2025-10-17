import requests
from flask import make_response, jsonify, redirect, url_for
from app.config import Config

class AuthService:
    def __init__(self):
        self.backend_url = Config.BACKEND_URL
    
    def login(self, credentials):
        mobile = credentials.get('mobile')
        password = credentials.get('password')
        print(f"{self.backend_url}/auth/login-password")
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login-password",
                json={"mobile": mobile, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    resp = make_response(jsonify({"success": True, "message": "Login successful"}))
                    
                    token = data.get('token')
                    if token:
                        resp.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
                    
                    return resp
                else:
                    return jsonify({"success": False, "message": data.get('message', 'Login failed')})
            else:
                return jsonify({"success": False, "message": "Login failed"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def request_otp(self, data):
        mobile = data.get('mobile')
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login-otp",
                json={"mobile": mobile}
            )
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({"success": False, "message": "Failed to send OTP"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def verify_otp(self, data):
        mobile = data.get('mobile')
        otp = data.get('otp')
        otp_id = data.get('otpId')
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login-otp-verify",
                json={"mobile": mobile, "otp": otp, "otpId": otp_id}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    resp = make_response(jsonify({"success": True, "message": "Login successful"}))
                    
                    token = response_data.get('token')
                    if token:
                        resp.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
                    
                    return resp
                else:
                    return jsonify({"success": False, "message": response_data.get('message', 'Login failed')})
            else:
                return jsonify({"success": False, "message": "Login failed"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def signup_request_otp(self, data):
        mobile = data.get('mobile')

        try:
            response = requests.post(
                f"{self.backend_url}/auth/signup-otp",
                json={"mobile": mobile}
            )

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    return jsonify({
                        "success": True,
                        "message": response_data.get('message', 'OTP sent successfully'),
                        "otpId": response_data.get('otpId')
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": response_data.get('message', 'Failed to send OTP')
                    }), response.status_code
            else:
                return jsonify({
                    "success": False,
                    "message": "Failed to send OTP"
                }), response.status_code
        except requests.exceptions.RequestException:
            return jsonify({
                "success": False,
                "message": "Server error"
            }), 500
    
    def signup_complete(self, data):
        mobile = data.get('mobile')
        otp = data.get('otp')
        otp_id = data.get('otpId')
        password = data.get('password')

        try:
            response = requests.post(
                f"{self.backend_url}/auth/signup-complete",
                json={
                    "mobile": mobile,
                    "otp": otp,
                    "otpId": otp_id,
                    "password": password
                }
            )

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    resp = make_response(jsonify({
                        "success": True,
                        "message": response_data.get('message', 'Signup successful'),
                        "user": response_data.get('user')
                    }))

                    token = response_data.get('token')
                    if token:
                        resp.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')

                    return resp
                else:
                    return jsonify({
                        "success": False,
                        "message": response_data.get('message', 'Signup failed')
                    }), response.status_code
            else:
                return jsonify({
                    "success": False,
                    "message": "Signup failed"
                }), response.status_code
        except requests.exceptions.RequestException:
            return jsonify({
                "success": False,
                "message": "Server error"
            }), 500
    
    def logout(self):
        try:
            response = requests.post(
                f"{self.backend_url}/auth/logout",
                cookies=request.cookies
            )
            
            resp = make_response(jsonify({"success": True, "message": "Logout successful"}))
            resp.set_cookie('auth_token', '', expires=0)
            
            return resp
        except requests.exceptions.RequestException:
            resp = make_response(jsonify({"success": True, "message": "Logout successful"}))
            resp.set_cookie('auth_token', '', expires=0)
            return resp
    
    def get_account(self, cookies):
        try:
            response = requests.get(
                f"{self.backend_url}/account",
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to get account info"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def update_profile(self, data, cookies):
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        
        try:
            response = requests.put(
                f"{self.backend_url}/account/profile",
                json={"firstName": first_name, "lastName": last_name},
                cookies=cookies
            )
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({"success": False, "message": "Failed to update profile"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def change_password(self, data, cookies):
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')

        try:
            response = requests.put(
                f"{self.backend_url}/account/password",
                json={"currentPassword": current_password, "newPassword": new_password},
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to change password"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def request_mobile_change_otp(self, data, cookies):
        new_mobile = data.get('newMobile')

        try:
            response = requests.post(
                f"{self.backend_url}/account/mobile-change-otp",
                json={"newMobile": new_mobile},
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to send OTP"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})
    
    def change_mobile(self, data, cookies):
        new_mobile = data.get('newMobile')
        otp = data.get('otp')
        otp_id = data.get('otpId')

        try:
            response = requests.put(
                f"{self.backend_url}/account/mobile",
                json={"newMobile": new_mobile, "otp": otp, "otpId": otp_id},
                cookies=cookies
            )

            if response.status_code == 200:
                return jsonify(response.json())
            elif response.status_code == 401:
                return redirect(url_for('auth.login'))
            else:
                return jsonify({"success": False, "message": "Failed to change phone number"})
        except requests.exceptions.RequestException:
            return jsonify({"success": False, "message": "Server error"})