// Authentication specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Login with password form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    mobile: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert(data.message || 'خطا در ورود');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('خطا در ارتباط با سرور');
            });
        });
    }
    
    // OTP login modal
    const loginWithOtpBtn = document.getElementById('loginWithOtpBtn');
    const otpLoginModal = document.getElementById('otpLoginModal');
    const otpRequestForm = document.getElementById('otpRequestForm');
    const otpVerifyForm = document.getElementById('otpVerifyForm');
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const resendOtpBtn = document.getElementById('resendOtpBtn');
    
    if (loginWithOtpBtn) {
        loginWithOtpBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(otpLoginModal);
            modal.show();
        });
    }
    
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener('click', function() {
            const mobile = document.getElementById('otpMobile').value;
            
            if (!mobile) {
                alert('لطفاً شماره موبایل را وارد کنید');
                return;
            }
            
            fetch('/api/login-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mobile: mobile
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('otpMobileDisplay').textContent = mobile;
                    document.getElementById('otpId').value = data.otpId;
                    otpRequestForm.style.display = 'none';
                    otpVerifyForm.style.display = 'block';
                } else {
                    alert(data.message || 'خطا در ارسال کد تایید');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('خطا در ارتباط با سرور');
            });
        });
    }
    
    if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener('click', function() {
            const mobile = document.getElementById('otpMobileDisplay').textContent;
            const otp = document.getElementById('otpCode').value;
            const otpId = document.getElementById('otpId').value;
            
            if (!otp) {
                alert('لطفاً کد تایید را وارد کنید');
                return;
            }
            
            fetch('/api/login-otp-verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    mobile: mobile,
                    otp: otp,
                    otpId: otpId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert(data.message || 'خطا در تایید کد');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('خطا در ارتباط با سرور');
            });
        });
    }
    
    if (resendOtpBtn) {
        resendOtpBtn.addEventListener('click', function() {
            const mobile = document.getElementById('otpMobileDisplay').textContent;
            
            fetch('/api/login-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mobile: mobile
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('otpId').value = data.otpId;
                    alert('کد تایید مجدداً ارسال شد');
                } else {
                    alert(data.message || 'خطا در ارسال کد تایید');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('خطا در ارتباط با سرور');
            });
        });
    }
    
    // Registration form
    const signupOtpForm = document.getElementById('signup-otp-form');
    const signupCompleteForm = document.getElementById('signup-complete-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const formTitle = document.getElementById('form-title');
    let otpId = null;
    let mobile = null;

    // Handle OTP request
    if (signupOtpForm) {
        signupOtpForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            mobile = document.getElementById('phone_number').value;

            try {
                const response = await fetch('/api/signup-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mobile })
                });

                const data = await response.json();

                if (data.success) {
                    otpId = data.otpId;
                    signupOtpForm.style.display = 'none';
                    signupCompleteForm.style.display = 'block';
                    formTitle.textContent = 'تایید کد و تکمیل ثبت نام';
                    successMessage.textContent = data.message;
                    successMessage.style.display = 'block';
                    errorMessage.style.display = 'none';
                } else {
                    errorMessage.textContent = data.message;
                    errorMessage.style.display = 'block';
                    successMessage.style.display = 'none';
                }
            } catch (err) {
                errorMessage.textContent = 'خطای سرور رخ داد';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
            }
        });
    }

    // Handle signup completion
    if (signupCompleteForm) {
        signupCompleteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const otp = document.getElementById('otp').value;
            const password = document.getElementById('password').value;
            const referralCode = document.getElementById('referral_code').value;

            try {
                const response = await fetch('/api/signup-complete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        mobile,
                        otp,
                        otpId,
                        password,
                        referralCode: referralCode || undefined
                    })
                });

                const data = await response.json();

                if (data.success) {
                    successMessage.textContent = data.message;
                    successMessage.style.display = 'block';
                    errorMessage.style.display = 'none';
                    // Redirect to dashboard or home after a short delay
                    setTimeout(() => {
                        window.location.href = '/'; // Adjust the redirect URL as needed
                    }, 2000);
                } else {
                    errorMessage.textContent = data.message;
                    errorMessage.style.display = 'block';
                    successMessage.style.display = 'none';
                }
            } catch (err) {
                errorMessage.textContent = 'خطای سرور رخ داد';
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
            }
        });
    }
});