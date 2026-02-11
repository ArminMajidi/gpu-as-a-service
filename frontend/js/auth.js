// auth.js - Fixed version

const API_BASE_URL = '/api/v1';

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const loginBtn = document.getElementById("login-btn");
  const errorDiv = document.getElementById("error-message");

  // Validation
  if (!email || !password) {
    showError("لطفاً همه فیلدها را پر کنید");
    return;
  }

  // Disable button and show loading
  loginBtn.disabled = true;
  loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>در حال ورود...';

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/x-www-form-urlencoded" 
      },
      body: new URLSearchParams({ 
        username: email,  // Backend expects 'username' field
        password: password 
      })
    });

    if (!res.ok) {
      const errorData = await res.json();
      showError(errorData.detail || "ایمیل یا رمز عبور اشتباه است");
      return;
    }

    const data = await res.json();
    
    // Save token
    localStorage.setItem("token", data.access_token);
    
    // Get user info to check role
    const userRes = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { 
        "Authorization": `Bearer ${data.access_token}` 
      }
    });
    
    if (userRes.ok) {
      const userData = await userRes.json();
      
      // Redirect based on role
      if (userData.is_admin) {
        window.location.href = "admin.html";
      } else {
        window.location.href = "dashboard.html";
      }
    } else {
      // Default to dashboard if can't get user info
      window.location.href = "dashboard.html";
    }

  } catch (error) {
    console.error("Login error:", error);
    showError("خطا در برقراری ارتباط با سرور");
  } finally {
    // Re-enable button
    loginBtn.disabled = false;
    loginBtn.innerHTML = 'ورود';
  }
}

function showError(message) {
  const errorDiv = document.getElementById("error-message");
  errorDiv.textContent = message;
  errorDiv.classList.remove("d-none");
  
  // Auto hide after 5 seconds
  setTimeout(() => {
    errorDiv.classList.add("d-none");
  }, 5000);
}

// Allow login with Enter key
document.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        login();
      }
    });
  });
});
