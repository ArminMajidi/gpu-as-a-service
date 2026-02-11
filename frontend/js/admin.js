// admin.js - Complete Admin Panel

const API_BASE_URL = '/api/v1';
const token = localStorage.getItem("token");

// Redirect if not logged in
if (!token) {
  window.location.href = "index.html";
}

let allJobs = []; // Store all jobs for filtering

// Check if user is admin
async function checkAdminAccess() {
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
      throw new Error('Failed to verify admin access');
    }

    const user = await res.json();
    
    // Check if user is admin
    if (!user.is_admin) {
      showAlert('شما دسترسی ادمین ندارید!', 'danger');
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 2000);
      return;
    }

    // Display admin name
    document.getElementById("admin-name").textContent = user.full_name || user.email;
    
  } catch (error) {
    console.error("Error checking admin access:", error);
    showAlert('خطا در بررسی دسترسی', 'danger');
  }
}

// Load all jobs (admin can see all users' jobs)
async function loadAllJobs() {
  try {
    const filterStatus = document.getElementById("filter-status").value;
    let url = `${API_BASE_URL}/admin/jobs`;
    
    // Add status filter to URL if selected
    if (filterStatus) {
      url += `?status_filter=${filterStatus.toUpperCase()}`;
    }
    
    const res = await fetch(url, {
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

    allJobs = await res.json();
    
    displayJobs(allJobs);
    updateStats(allJobs);

  } catch (error) {
    console.error("Error loading jobs:", error);
    showAlert('خطا در بارگذاری لیست Job ها', 'danger');
  }
}

// Display jobs in table
function displayJobs(jobs) {
  const tbody = document.getElementById("jobs-body");

  if (jobs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="9" class="text-center text-muted py-4">
          هیچ Job ای یافت نشد
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
        <td>
          <strong>${job.name}</strong><br>
          <small class="text-muted">${job.command}</small>
        </td>
        <td>
          <small>${job.user_email || 'N/A'}</small>
        </td>
        <td>${job.gpu_type}</td>
        <td>${job.num_gpus}</td>
        <td>${job.estimated_hours}h</td>
        <td><span class="job-status ${statusClass}">${translateStatus(job.status)}</span></td>
        <td><small>${createdDate}</small></td>
        <td>
          ${getActionButtons(job)}
        </td>
      </tr>
    `;
  }).join('');
}

// Get action buttons based on job status
function getActionButtons(job) {
  const buttons = [];
  
  // View details button (always available)
  buttons.push(`
    <button class="btn btn-sm btn-info action-btn" onclick="viewJobDetails(${job.id})" title="جزئیات">
      👁️
    </button>
  `);
  
  switch(job.status.toLowerCase()) {
    case 'pending':
      buttons.push(`
        <button class="btn btn-sm btn-success action-btn" onclick="approveJob(${job.id})" title="تایید">
          ✅
        </button>
        <button class="btn btn-sm btn-danger action-btn" onclick="rejectJob(${job.id})" title="رد">
          ❌
        </button>
      `);
      break;
      
    case 'approved':
      buttons.push(`
        <button class="btn btn-sm btn-primary action-btn" onclick="startJob(${job.id})" title="شروع">
          ▶️
        </button>
      `);
      break;
      
    case 'running':
      buttons.push(`
        <button class="btn btn-sm btn-success action-btn" onclick="completeJob(${job.id})" title="اتمام موفق">
          ✔️
        </button>
        <button class="btn btn-sm btn-warning action-btn" onclick="failJob(${job.id})" title="شکست">
          ⚠️
        </button>
      `);
      break;
  }
  
  return buttons.join('');
}

// Admin Actions
async function approveJob(jobId) {
  if (!confirm('آیا مطمئن هستید که می‌خواهید این Job را تایید کنید؟')) return;
  
  await performAction(jobId, 'approve', 'Job با موفقیت تایید شد');
}

async function rejectJob(jobId) {
  if (!confirm('آیا مطمئن هستید که می‌خواهید این Job را رد کنید؟')) return;
  
  await performAction(jobId, 'reject', 'Job رد شد');
}

async function startJob(jobId) {
  if (!confirm('آیا می‌خواهید این Job را شروع کنید؟')) return;
  
  await performAction(jobId, 'start', 'Job شروع شد');
}

async function completeJob(jobId) {
  if (!confirm('آیا این Job با موفقیت تکمیل شده است؟')) return;
  
  await performAction(jobId, 'complete', 'Job با موفقیت تکمیل شد');
}

async function failJob(jobId) {
  const reason = prompt('دلیل شکست Job را وارد کنید:');
  if (!reason) return;
  
  await performAction(jobId, 'fail', 'Job به عنوان ناموفق علامت‌گذاری شد', { error_message: reason });
}

// Perform admin action
async function performAction(jobId, action, successMessage, body = {}) {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/jobs/${jobId}/${action}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'عملیات ناموفق بود');
    }

    showAlert(successMessage, 'success');
    await loadAllJobs(); // Reload jobs

  } catch (error) {
    console.error(`Error performing ${action}:`, error);
    showAlert(error.message || `خطا در ${action}`, 'danger');
  }
}

// View job details in modal
async function viewJobDetails(jobId) {
  const job = allJobs.find(j => j.id === jobId);
  if (!job) return;

  const modalBody = document.getElementById("modal-job-details");
  
  modalBody.innerHTML = `
    <div class="row">
      <div class="col-md-6">
        <p><strong>شناسه:</strong> ${job.id}</p>
        <p><strong>نام:</strong> ${job.name}</p>
        <p><strong>نوع GPU:</strong> ${job.gpu_type}</p>
        <p><strong>تعداد GPU:</strong> ${job.num_gpus}</p>
        <p><strong>ساعت تخمینی:</strong> ${job.estimated_hours}</p>
      </div>
      <div class="col-md-6">
        <p><strong>وضعیت:</strong> <span class="job-status status-${job.status.toLowerCase()}">${translateStatus(job.status)}</span></p>
        <p><strong>تاریخ ایجاد:</strong> ${new Date(job.created_at).toLocaleString('fa-IR')}</p>
        ${job.started_at ? `<p><strong>تاریخ شروع:</strong> ${new Date(job.started_at).toLocaleString('fa-IR')}</p>` : ''}
        ${job.finished_at ? `<p><strong>تاریخ اتمام:</strong> ${new Date(job.finished_at).toLocaleString('fa-IR')}</p>` : ''}
      </div>
    </div>
    <hr>
    <p><strong>دستور:</strong></p>
    <pre class="bg-light p-2 rounded">${job.command}</pre>
    ${job.data_location ? `<p><strong>محل داده:</strong> ${job.data_location}</p>` : ''}
    ${job.is_sensitive ? `<p><span class="badge bg-warning">حاوی اطلاعات حساس</span></p>` : ''}
    ${job.error_message ? `
      <div class="alert alert-danger">
        <strong>پیام خطا:</strong><br>
        ${job.error_message}
      </div>
    ` : ''}
  `;

  const modal = new bootstrap.Modal(document.getElementById('jobDetailsModal'));
  modal.show();
}

// Filter jobs by search input
function filterJobs() {
  const searchTerm = document.getElementById("search-input").value.toLowerCase();
  
  if (!searchTerm) {
    displayJobs(allJobs);
    return;
  }
  
  const filtered = allJobs.filter(job => 
    job.name.toLowerCase().includes(searchTerm) ||
    job.command.toLowerCase().includes(searchTerm) ||
    (job.user_email && job.user_email.toLowerCase().includes(searchTerm))
  );
  
  displayJobs(filtered);
}

// Update statistics
function updateStats(jobs) {
  const stats = {
    total: jobs.length,
    pending: jobs.filter(j => j.status.toLowerCase() === 'pending').length,
    running: jobs.filter(j => j.status.toLowerCase() === 'running').length,
    completed: jobs.filter(j => j.status.toLowerCase() === 'completed').length
  };
  
  document.getElementById("stat-total").textContent = stats.total;
  document.getElementById("stat-pending").textContent = stats.pending;
  document.getElementById("stat-running").textContent = stats.running;
  document.getElementById("stat-completed").textContent = stats.completed;
}

// Show alert message
function showAlert(message, type = 'info') {
  const alertContainer = document.getElementById("alert-container");
  
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show`;
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  alertContainer.appendChild(alert);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    alert.remove();
  }, 5000);
}

// Translate job status to Persian
function translateStatus(status) {
  const statusMap = {
    'pending': 'در انتظار تایید',
    'approved': 'تایید شده',
    'running': 'در حال اجرا',
    'completed': 'تکمیل شده',
    'failed': 'ناموفق',
    'rejected': 'رد شده'
  };
  return statusMap[status.toLowerCase()] || status;
}

// Logout
function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
  await checkAdminAccess();
  await loadAllJobs();
  
  // Auto-refresh every 30 seconds
  setInterval(loadAllJobs, 30000);
});
