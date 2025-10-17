from kavenegar import KavenegarAPI, APIException, HTTPException
from app.core.config import settings
from app.core.logger import logger

"""
doc for templates :

params = {
            'receptor': phone_number,
            'template': 'processend',  # Process completion template
            'token': phone_number,  # Using phone number as token
            'type': 'sms'
        }
        
params = {
            'receptor': phone_number,
            'template': 'payment',  # Payment template
            'token': phone_number,  # User's phone number
            'token2': str(payment_amount_rials),  # Payment amount in Rials
            'token3': str(balance_rials),  # Wallet balance in Rials
            'type': 'sms'
        }
        
        
params = {
            'receptor': phone_number,
            'template': 'verify',  # This template should be configured in Kavenegar panel
            'token': token,
            'type': 'sms'
        }

"""

class KavenegarService:
    def __init__(self):
        self.api_key = settings.KAVENEGAR_API_KEY
        if not self.api_key:
            logger.error("Kavenegar API key is not configured")
            self.api = None
        else:
            self.api = KavenegarAPI(self.api_key)
        self.sender_number = settings.SENDER_NUMBER
        if not self.sender_number:
            logger.error("Sender number is not configured")


        self.available_templates = {"verify": True , "processend" : True , "payment" : True }

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send a simple text SMS message via Kavenegar."""
        if not self.api:
            return False

        try:
            params = {
                "sender": self.sender_number,  # Kavenegar sender number
                "receptor": phone_number,
                "message": message,
            }
            response = self.api.sms_send(params)
            return True
        except (APIException, HTTPException) as e:
            return False
        except Exception as e:
            return False

    def send_otp(self, receptor: str, code: str, template: str = "verify") -> bool:
        if not self.api:
            return False
        if template not in self.available_templates:
            return False
        try:
            params = {
                "receptor": receptor,
                "template": template,  # Template name in Kavenegar dashboard
                "token": f"{code}",
                "type": "sms",
            }
            response = self.api.verify_lookup(params)
            return True
        except (APIException, HTTPException) as e:
            # Fallback: regular SMS
            fallback_message = f"کد تایید شما: {code}"
            return self.send_sms(receptor, fallback_message)
        except Exception as e:
            return False


kavenegar_service = KavenegarService()

def send_sms(phone_number: str, message: str) -> bool:
    return kavenegar_service.send_sms(phone_number, message)

def send_login_otp_sms(mobile: str, otp_code: str) -> bool:
    """Send login OTP, return False on any failure."""
    message = f"کد ورود شما به کاپاتی: {otp_code}"
    return kavenegar_service.send_otp(mobile, otp_code, template="verify")


def send_signup_otp_sms(mobile: str, otp_code: str) -> bool:
    """Send signup OTP, return False on any failure."""
    message = f"کد ثبت‌نام شما در کاپاتی: {otp_code}"
    return kavenegar_service.send_otp(mobile, otp_code, template="verify")


def send_change_mobile_otp_sms(mobile: str, otp_code: str) -> bool:
    message = f"کد تایید تغییر شماره موبایل شما: {otp_code}"
    return kavenegar_service.send_otp(mobile, otp_code, template="verify")