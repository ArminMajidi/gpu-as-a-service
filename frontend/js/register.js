// register.js - Registration functionality

const API_BASE_URL = '/api/v1';

// Password strength checker
function checkPasswordStrength(password) {
  const strengthBar = document.getElementById('password-strength');
  
  if (password.length === 0) {
    strengthBar.classList.add('d-none');
    return;
  }
  
  strengthBar.classList.remove('d-none');
  
  let strength = 0;
  
  // Length check
  if (password.length >= 6) strength++;
  if (password.length >= 10) strength++;
  
  // Character variety checks
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^a-zA-Z0-9]/.test(password)) strength++;
  
  // Update strength bar
  strengthBar.className = 'password-strength';
  
  if (strength <= 2) {
    strengthBar.classList.add('strength-weak');
  } else if (strength <= 4) {
    strengthBar.classList.add('strength-medium');
  } else {
    strengthBar.classList.add('strength-strong');
  }
}

// Check if passwords match
function checkPasswordsMatch() {
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  const confirmInput = document.getElementById('confirm-password');
  const feedback = document.getElementById('confirm-password-feedback');
  
  if (confirmPassword.length === 0) {
    confirmInput.classList.remove('is-invalid', 'is-valid');
    return true;
  }
  
  if (password === confirmPassword) {
    confirmInput.classList.remove('is-invalid');
    confirmInput.classList.add('is-valid');
    feedback.textContent = '✓ رمزهای عبور مطابقت دارند';
    feedback.classList.remove('invalid-feedback');
    feedback.classList.add('valid-feedback');
    return true;
  } else {
    confirmInput.classList.remove('is-valid');
    confirmInput.classList.add('is-invalid');
    feedback.textContent = '✗ رمزهای عبور مطابقت ندارند';
    feedback.classList.remove('valid-feedback');
    feedback.classList.add('invalid-feedback');
    return false;
  }
}

// Validate email format
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Show alert message
function showAlert(message, type = 'danger') {
  const errorDiv = document.getElementById('error-message');
  const successDiv = document.getElementById('success-message');
  
  // Hide both first
  errorDiv.classList.add('d-none');
  successDiv.classList.add('d-none');
  
  if (type === 'danger') {
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    successDiv.textContent = message;
    successDiv.classList.remove('d-none');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Handle registration
async function handleRegister(event) {
  event.preventDefault();
  
  const form = document.getElementById('register-form');
  const registerBtn = document.getElementById('register-btn');
  
  // Validate form
  if (!form.checkValidity()) {
    event.stopPropagation();
    form.classList.add('was-validated');
    return;
  }
  
  // Get form values
  const fullName = document.getElementById('full-name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  const acceptTerms = document.getElementById('accept-terms').checked;
  
  // Validate email
  if (!validateEmail(email)) {
    showAlert('لطفاً یک ایمیل معتبر وارد کنید');
    return;
  }
  
  // Check password length
  if (password.length < 6) {
    showAlert('رمز عبور باید حداقل ۶ کاراکتر باشد');
    return;
  }
  
  // Check passwords match
  if (password !== confirmPassword) {
    showAlert('رمزهای عبور مطابقت ندارند');
    return;
  }
  
  // Check terms acceptance
  if (!acceptTerms) {
    showAlert('لطفاً قوانین و مقررات را بپذیرید');
    return;
  }
  
  // Disable button and show loading
  registerBtn.disabled = true;
  registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>در حال ثبت‌نام...';
  
  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        full_name: fullName,
        password: password
      })
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      // Handle errors
      if (res.status === 400 && data.detail === 'Email already registered') {
        showAlert('این ایمیل قبلاً ثبت شده است. لطفاً وارد شوید.');
      } else {
        showAlert(data.detail || 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.');
      }
      return;
    }
    
    // Success!
    showAlert('✅ ثبت‌نام با موفقیت انجام شد! در حال انتقال به صفحه ورود...', 'success');
    
    // Clear form
    form.reset();
    form.classList.remove('was-validated');
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      window.location.href = 'index.html';
    }, 2000);
    
  } catch (error) {
    console.error('Registration error:', error);
    showAlert('خطا در برقراری ارتباط با سرور. لطفاً دوباره تلاش کنید.');
  } finally {
    // Re-enable button
    registerBtn.disabled = false;
    registerBtn.innerHTML = 'ثبت‌نام';
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm-password');
  
  // Add form submit handler
  form.addEventListener('submit', handleRegister);
  
  // Add password strength checker
  passwordInput.addEventListener('input', (e) => {
    checkPasswordStrength(e.target.value);
    checkPasswordsMatch();
  });
  
  // Add password match checker
  confirmPasswordInput.addEventListener('input', checkPasswordsMatch);
  
  // Allow Enter key to submit
  form.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRegister(e);
    }
  });
  
  // Check if already logged in
  const token = localStorage.getItem('token');
  if (token) {
    // Verify token is valid
    fetch(`${API_BASE_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => {
      if (res.ok) {
        // Already logged in, redirect to dashboard
        window.location.href = 'dashboard.html';
      }
    })
    .catch(() => {
      // Invalid token, remove it
      localStorage.removeItem('token');
    });
  }
});
