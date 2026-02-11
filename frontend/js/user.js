// user.js - Fixed version

const API_BASE_URL = '/api/v1';
const token = localStorage.getItem("token");

// Redirect if not logged in
if (!token) {
  window.location.href = "index.html";
}

// Load user info on page load
async function loadUserInfo() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { 
        "Authorization": `Bearer ${token}` 
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
        logout();
        return;
      }
      throw new Error('Failed to load user info');
    }

    const user = await res.json();
    document.getElementById("user-info").innerHTML = `
      <p class="mb-1"><strong>نام:</strong> ${user.full_name}</p>
      <p class="mb-0"><strong>ایمیل:</strong> ${user.email}</p>
    `;
  } catch (error) {
    console.error("Error loading user info:", error);
    document.getElementById("user-info").innerHTML = 
      '<span class="text-danger">خطا در بارگذاری اطلاعات کاربر</span>';
  }
}

// Load jobs list
async function loadJobs() {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
      headers: { 
        "Authorization": `Bearer ${token}` 
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
        logout();
        return;
      }
      throw new Error('Failed to load jobs');
    }

    const jobs = await res.json();
    const tbody = document.getElementById("jobs-body");

    if (jobs.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" class="text-center text-muted py-4">
            هنوز هیچ Job ای ایجاد نکرده‌اید
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = jobs.map(job => {
      const createdDate = new Date(job.created_at).toLocaleDateString('fa-IR');
      const statusClass = `status-${job.status.toLowerCase()}`;
      
      return `
        <tr>
          <td>${job.id}</td>
          <td>${job.name}</td>
          <td>${job.gpu_type}</td>
          <td>${job.num_gpus}</td>
          <td>${job.estimated_hours} ساعت</td>
          <td><span class="job-status ${statusClass}">${translateStatus(job.status)}</span></td>
          <td>${createdDate}</td>
        </tr>
      `;
    }).join('');

  } catch (error) {
    console.error("Error loading jobs:", error);
    document.getElementById("jobs-body").innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger">
          خطا در بارگذاری لیست Job ها
        </td>
      </tr>
    `;
  }
}

// Create new job
async function createJob(event) {
  event.preventDefault();
  
  const submitBtn = document.getElementById("submit-btn");
  const errorDiv = document.getElementById("form-error");
  const successDiv = document.getElementById("form-success");

  // Hide previous messages
  errorDiv.classList.add("d-none");
  successDiv.classList.add("d-none");

  // Get form values
  const jobData = {
    name: document.getElementById("job-name").value,
    gpu_type: document.getElementById("gpu-type").value,
    num_gpus: parseInt(document.getElementById("num-gpus").value),
    estimated_hours: parseFloat(document.getElementById("estimated-hours").value),
    command: document.getElementById("command").value,
    data_location: document.getElementById("data-location").value || null,
    is_sensitive: document.getElementById("is-sensitive").checked
  };

  // Disable submit button
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>در حال ایجاد...';

  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(jobData)
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Failed to create job');
    }

    const newJob = await res.json();
    
    // Show success message
    successDiv.textContent = `Job "${newJob.name}" با موفقیت ایجاد شد!`;
    successDiv.classList.remove("d-none");

    // Reset form
    document.getElementById("job-form").reset();

    // Reload jobs list
    await loadJobs();

    // Hide success message after 5 seconds
    setTimeout(() => {
      successDiv.classList.add("d-none");
    }, 5000);

  } catch (error) {
    console.error("Error creating job:", error);
    errorDiv.textContent = error.message || "خطا در ایجاد Job";
    errorDiv.classList.remove("d-none");
  } finally {
    // Re-enable submit button
    submitBtn.disabled = false;
    submitBtn.innerHTML = 'ایجاد Job';
  }
}

// Translate job status to Persian
function translateStatus(status) {
  const statusMap = {
    'pending': 'در انتظار',
    'approved': 'تایید شده',
    'running': 'در حال اجرا',
    'completed': 'تکمیل شده',
    'failed': 'ناموفق',
    'rejected': 'رد شده'
  };
  return statusMap[status.toLowerCase()] || status;
}

// Logout function
function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
  loadUserInfo();
  loadJobs();
  
  // Add form submit handler
  document.getElementById("job-form").addEventListener('submit', createJob);
  
  // Auto-refresh jobs every 30 seconds
  setInterval(loadJobs, 30000);
});
