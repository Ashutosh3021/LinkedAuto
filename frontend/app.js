/* ================================================================
   LINKEDAUTO — APP.JS
   Vanilla JS, no frameworks
   ================================================================ */

'use strict';

const API_BASE = ''; // Relative URL since it's same origin

/* ================================================================
   1. API SERVICE FUNCTIONS
   ================================================================ */

async function apiRequest(endpoint, options = {}) {
  const url = API_BASE + endpoint;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  
  try {
    const response = await fetch(url, { ...options, headers });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    return data;
  } catch (error) {
    console.error(`API request to ${url} failed:`, error);
    throw error;
  }
}

// Dashboard Stats
async function getDashboardStats() {
  return apiRequest('/api/dashboard/stats');
}

// Posts
async function getGeneratedPosts() {
  return apiRequest('/api/dashboard/posts/generated');
}

async function getScheduledPosts() {
  return apiRequest('/api/dashboard/posts/scheduled');
}

async function generateSinglePost(data) {
  return apiRequest('/api/generate/post', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function generateBatchPosts(data) {
  return apiRequest('/api/generate/batch', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// Scheduler
async function schedulePost(data) {
  return apiRequest('/api/schedule', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function cancelSchedule(postId) {
  return apiRequest(`/api/schedule/${postId}`, {
    method: 'DELETE'
  });
}

async function reschedulePost(postId, data) {
  return apiRequest(`/api/schedule/${postId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

// Logs
async function getLogs() {
  return apiRequest('/api/dashboard/logs');
}

// LinkedIn Connection
async function getLinkedInStatus() {
  return apiRequest('/api/linkedin/status');
}

async function getLinkedInAuthUrl() {
  return apiRequest('/api/linkedin/auth');
}

async function disconnectLinkedIn() {
  return apiRequest('/api/linkedin/disconnect', { method: 'POST' });
}

// Connection Configs
async function getConnectionConfigs() {
  return apiRequest('/api/connections/configs');
}

async function createConnectionConfig(data) {
  return apiRequest('/api/connections/configs', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function updateConnectionConfig(configId, data) {
  return apiRequest(`/api/connections/configs/${configId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

async function deleteConnectionConfig(configId) {
  return apiRequest(`/api/connections/configs/${configId}`, {
    method: 'DELETE'
  });
}

// Connection Jobs
async function getConnectionJobs() {
  return apiRequest('/api/connections/jobs');
}

async function createConnectionJob(data) {
  return apiRequest('/api/connections/jobs', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function startConnectionJob(jobId) {
  return apiRequest(`/api/connections/jobs/${jobId}/start`, {
    method: 'POST'
  });
}

// Profiles
async function getProfiles(jobId) {
  const query = jobId ? `?job_id=${jobId}` : '';
  return apiRequest(`/api/connections/profiles${query}`);
}

// Daily Stats
async function getDailyConnectionStats() {
  return apiRequest('/api/connections/stats/daily');
}

// AI Providers
async function getProviders() {
  return apiRequest('/api/config/providers');
}

async function createProvider(data) {
  return apiRequest('/api/config/providers', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function updateProvider(providerId, data) {
  return apiRequest(`/api/config/providers/${providerId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

async function deleteProvider(providerId) {
  return apiRequest(`/api/config/providers/${providerId}`, {
    method: 'DELETE'
  });
}

async function activateProvider(providerId) {
  return apiRequest(`/api/config/providers/${providerId}/activate`, {
    method: 'POST'
  });
}

// LinkedIn App Credentials
async function getLinkedInApps() {
  return apiRequest('/api/config/linkedin-app');
}

async function createLinkedInApp(data) {
  return apiRequest('/api/config/linkedin-app', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function updateLinkedInApp(appId, data) {
  return apiRequest(`/api/config/linkedin-app/${appId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

async function deleteLinkedInApp(appId) {
  return apiRequest(`/api/config/linkedin-app/${appId}`, {
    method: 'DELETE'
  });
}

async function activateLinkedInApp(appId) {
  return apiRequest(`/api/config/linkedin-app/${appId}/activate`, {
    method: 'POST'
  });
}

/* ================================================================
   2. UTILITY FUNCTIONS
   ================================================================ */

function $(selector, root = document) {
  return root.querySelector(selector);
}

function $$(selector, root = document) {
  return root.querySelectorAll(selector);
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString('en-IN');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ================================================================
   3. TOAST NOTIFICATION SYSTEM
   ================================================================ */

const TOAST_ICONS = {
  success: '✓',
  error:   '✕',
  info:    'ℹ',
  warn:    '⚠',
};

function showToast(message, type = 'info', duration = 3500) {
  const container = $('#toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <span class="toast-icon">${TOAST_ICONS[type] || 'ℹ'}</span>
    <span class="toast-msg">${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(24px)';
    toast.style.transition = 'opacity 250ms, transform 250ms';
    setTimeout(() => toast.remove(), 260);
  }, duration);
}

/* ================================================================
   4. LOADING OVERLAY
   ================================================================ */

function showLoading(label = 'Processing…') {
  const overlay = $('#loading-overlay');
  const lbl = $('#loading-label');
  if (lbl) lbl.textContent = label;
  if (overlay) overlay.hidden = false;
}

function hideLoading() {
  const overlay = $('#loading-overlay');
  if (overlay) overlay.hidden = true;
}

/* ================================================================
   5. PROGRESS BAR
   ================================================================ */

let progressTimer = null;

function runProgressBar(duration = 2000) {
  const wrap = $('#progress-bar-wrap');
  const bar  = $('#progress-bar');
  if (!wrap || !bar) return;
  wrap.hidden = false;
  bar.style.width = '0%';

  let pct = 0;
  const step = 100 / (duration / 50);
  clearInterval(progressTimer);
  progressTimer = setInterval(() => {
    pct = Math.min(pct + step + Math.random() * step * 0.5, 92);
    bar.style.width = pct + '%';
    if (pct >= 92) clearInterval(progressTimer);
  }, 50);
}

function completeProgressBar() {
  clearInterval(progressTimer);
  const bar  = $('#progress-bar');
  const wrap = $('#progress-bar-wrap');
  if (!bar || !wrap) return;
  bar.style.width = '100%';
  setTimeout(() => {
    wrap.hidden = true;
    bar.style.width = '0%';
  }, 400);
}

/* ================================================================
   6. MODAL SYSTEM
   ================================================================ */

function openPreviewModal(post) {
  const overlay = $('#modal-overlay');
  const body    = $('#modal-body');
  if (!overlay || !body) return;
  
  body.innerHTML = `
    <p class="post-card-topic" style="margin-bottom:10px;">${escapeHtml(post.title || post.topic || 'Post')}</p>
    <p style="white-space:pre-line;margin-bottom:14px;">${escapeHtml(post.content || post.body || '')}</p>
    <p style="font-size:.8125rem;color:var(--color-text-faint);">${post.published_at ? `Published: ${formatDateTime(post.published_at)}` : post.scheduled_at ? `Scheduled: ${formatDateTime(post.scheduled_at)}` : ''}</p>
  `;
  overlay.hidden = false;
  $('#btn-modal-close').focus();
}

function closePreviewModal() {
  const overlay = $('#modal-overlay');
  if (overlay) overlay.hidden = true;
}

/* ================================================================
   7. CONFIRM DIALOG
   ================================================================ */

let pendingDeleteCallback = null;

function showConfirm(message, onConfirm) {
  const overlay = $('#confirm-overlay');
  $('#confirm-message').textContent = message;
  pendingDeleteCallback = onConfirm;
  overlay.hidden = false;
  $('#btn-confirm-delete').focus();
}

function closeConfirmDialog() {
  const overlay = $('#confirm-overlay');
  if (overlay) overlay.hidden = true;
  pendingDeleteCallback = null;
}

/* ================================================================
   PROVIDER MODAL
   ================================================================ */

let editingProviderId = null;

function openProviderModal(provider = null) {
  const overlay = $('#provider-overlay');
  const title = $('#provider-title');
  const form = $('#form-provider');
  
  editingProviderId = provider?.id || null;
  
  if (provider) {
    title.textContent = 'Edit AI Provider';
    $('#provider-id').value = provider.id;
    $('#provider-name').value = provider.name;
    $('#provider-model').value = provider.model_name;
    $('#provider-api-key').value = ''; // Don't populate existing key
    $('#provider-base-url').value = provider.base_url;
    $('#provider-active').checked = provider.is_active;
  } else {
    title.textContent = 'Add AI Provider';
    form.reset();
    $('#provider-id').value = '';
    $('#provider-base-url').value = 'https://openrouter.ai/api/v1';
  }
  
  overlay.hidden = false;
  $('#provider-name').focus();
}

function closeProviderModal() {
  const overlay = $('#provider-overlay');
  if (overlay) overlay.hidden = true;
  editingProviderId = null;
}

/* ================================================================
   LINKEDIN APP MODAL
   ================================================================ */

let editingLinkedInAppId = null;

function openLinkedInAppModal(app = null) {
  const overlay = $('#linkedin-app-overlay');
  const title = $('#linkedin-app-title');
  const form = $('#form-linkedin-app');
  
  editingLinkedInAppId = app?.id || null;
  
  if (app) {
    title.textContent = 'Edit LinkedIn App';
    $('#linkedin-app-id').value = app.id;
    $('#linkedin-client-id').value = app.client_id;
    $('#linkedin-client-secret').value = ''; // Don't populate existing secret
    $('#linkedin-redirect-uri').value = app.redirect_uri;
    $('#linkedin-app-active').checked = app.is_active;
  } else {
    title.textContent = 'Add LinkedIn App';
    form.reset();
    $('#linkedin-app-id').value = '';
    $('#linkedin-redirect-uri').value = 'http://localhost:5000/linkedin/callback';
  }
  
  overlay.hidden = false;
  $('#linkedin-client-id').focus();
}

function closeLinkedInAppModal() {
  const overlay = $('#linkedin-app-overlay');
  if (overlay) overlay.hidden = true;
  editingLinkedInAppId = null;
}

/* ================================================================
   8. NAVIGATION
   ================================================================ */

function initNavigation() {
  const toggle = $('#btn-nav-toggle');
  const nav    = $('#main-nav');

  toggle?.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(isOpen));
  });

  $$('.nav-link', nav).forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'home';
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  const active = $(`.nav-link[data-page="${currentPage}"]`);
  if (active) active.classList.add('active');
}

/* ================================================================
   9. CHARACTER COUNTERS
   ================================================================ */

function initCharCounter(textareaId, counterId) {
  const textarea = $(`#${textareaId}`);
  const counter  = $(`#${counterId}`);
  if (!textarea || !counter) return;

  const max = textarea.getAttribute('maxlength') || '∞';

  function update() {
    counter.textContent = `${textarea.value.length} / ${max}`;
  }

  textarea.addEventListener('input', update);
  update();
}

function initAllCharCounters() {
  initCharCounter('posting-topics',   'count-topics');
  initCharCounter('posting-projects', 'count-projects');
  initCharCounter('conn-keywords',    'count-keywords');
  initCharCounter('conn-message',     'count-conn-message');
}

/* ================================================================
   10. TIME SLOTS
   ================================================================ */

let timeSlotCount = 0;

function addTimeSlot(value = '') {
  const list = $('#posting-times-list');
  if (!list) return;
  timeSlotCount++;
  const id   = `time-slot-${timeSlotCount}`;
  const item = document.createElement('div');
  item.className = 'time-slot-item';
  item.dataset.slotId = id;
  item.innerHTML = `
    <label class="sr-only" for="${id}">Posting time ${timeSlotCount}</label>
    <input class="time-slot-input" type="time" id="${id}" name="posting_time" value="${escapeHtml(value)}" />
    <button type="button" class="time-slot-remove" aria-label="Remove time slot" data-remove="${id}">&times;</button>
  `;

  item.querySelector('.time-slot-remove').addEventListener('click', () => {
    item.remove();
    showToast('Time slot removed.', 'info', 2000);
  });

  list.appendChild(item);
}

function initTimeSlots() {
  if ($('#posting-times-list')) {
    addTimeSlot('09:00');
    addTimeSlot('18:30');

    $('#btn-add-time').addEventListener('click', () => {
      addTimeSlot();
      showToast('Time slot added.', 'info', 2000);
    });
  }
}

/* ================================================================
   11. STATUS BADGE
   ================================================================ */

function statusBadge(status) {
  const labels = {
    scheduled: 'Scheduled',
    published: 'Published',
    pending:   'Pending',
    failed:    'Failed',
    draft:     'Draft',
  };
  return `<span class="badge badge--${status}">${labels[status] || status}</span>`;
}

/* ================================================================
   12. DASHBOARD PAGE
   ================================================================ */

async function initDashboard() {
  try {
    const response = await getDashboardStats();
    if (!response.success) throw new Error('Failed to fetch stats');
    const stats = response.data;

    // Update stat cards
    if ($('#stat-generated')) $('#stat-generated').textContent = stats.posts.total || '0';
    if ($('#stat-scheduled')) $('#stat-scheduled').textContent = stats.posts.scheduled || '0';
    if ($('#stat-published')) $('#stat-published').textContent = stats.posts.published || '0';
    if ($('#stat-connections')) $('#stat-connections').textContent = stats.connections?.total_profiles || '0';

    // LinkedIn status
    if ($('#linkedin-status')) {
      const isConnected = stats.linkedin?.connected;
      $('#linkedin-status').textContent = isConnected ? 'Connected' : 'Not Connected';
      $('#linkedin-status').className = isConnected ? 'status-dot status-dot--success' : 'status-dot status-dot--error';
    }

  } catch (error) {
    console.error('Failed to initialize dashboard:', error);
    showToast('Failed to load dashboard stats', 'error');
  }
}

/* ================================================================
   13. POSTING PAGE
   ================================================================ */

let generatedPosts = [];
let scheduledPosts = [];

async function loadPostsForPostingPage() {
  try {
    const [genResponse, schedResponse] = await Promise.all([
      getGeneratedPosts(),
      getScheduledPosts()
    ]);
    
    generatedPosts = genResponse.data || [];
    scheduledPosts = schedResponse.data || [];
    
    renderPostsGrid(generatedPosts);
    renderScheduledTable(scheduledPosts);
  } catch (error) {
    console.error('Failed to load posts:', error);
    showToast('Failed to load posts', 'error');
  }
}

function renderScheduledTable(posts) {
  const tbody = $('#tbody-scheduled');
  if (!tbody) return;
  
  if (!posts.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--color-text-faint);padding:32px;">No scheduled posts found.</td></tr>`;
    return;
  }

  tbody.innerHTML = posts.map(post => `
    <tr data-id="${post.id}">
      <td>${escapeHtml(post.title || post.topic || 'Untitled')}</td>
      <td>${post.scheduled_at ? formatDate(post.scheduled_at) : '-'}</td>
      <td style="font-variant-numeric:tabular-nums;font-family:var(--font-mono);font-size:.8125rem;">${post.scheduled_at ? new Date(post.scheduled_at).toTimeString().slice(0,5) : '-'}</td>
      <td>${statusBadge(post.status)}</td>
      <td class="col-actions">
        <div class="table-actions">
          <button class="btn btn-icon btn-sm btn-preview-post" title="Preview" data-id="${post.id}">◉</button>
          <button class="btn btn-icon btn-sm btn-delete-post" title="Delete" data-id="${post.id}">✕</button>
        </div>
      </td>
    </tr>
  `).join('');

  $$('.btn-preview-post', tbody).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      const post = [...generatedPosts, ...scheduledPosts].find(p => p.id === id);
      if (post) openPreviewModal(post);
    });
  });

  $$('.btn-delete-post', tbody).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      showConfirm('Delete this scheduled post? This cannot be undone.', async () => {
        try {
          await cancelSchedule(id);
          scheduledPosts = scheduledPosts.filter(p => p.id !== id);
          renderScheduledTable(scheduledPosts);
          showToast('Post deleted.', 'warn');
        } catch (error) {
          showToast('Failed to delete post', 'error');
        }
      });
    });
  });
}

function renderPostsGrid(posts) {
  const grid = $('#posts-grid');
  if (!grid) return;
  
  if (!posts.length) {
    grid.innerHTML = `<p style="color:var(--color-text-faint);">No generated posts yet. Use the Posting Configuration to generate posts.</p>`;
    return;
  }

  grid.innerHTML = posts.map(post => `
    <article class="post-card" data-id="${post.id}">
      <div class="post-card-header">
        <p class="post-card-topic">${escapeHtml(post.title || post.topic || 'Untitled')}</p>
        ${statusBadge(post.status)}
      </div>
      <p class="post-card-body">${escapeHtml(post.content || post.body || '')}</p>
      <div class="post-card-meta">
        <span>${post.scheduled_at ? formatDateTime(post.scheduled_at) : post.created_at ? formatDateTime(post.created_at) : ''}</span>
      </div>
      <div class="post-card-actions">
        <button class="btn btn-ghost btn-sm btn-pc-preview" data-id="${post.id}">Preview</button>
        <button class="btn btn-primary btn-sm btn-pc-publish" data-id="${post.id}">Schedule</button>
        <button class="btn btn-ghost btn-sm btn-pc-delete" data-id="${post.id}" style="color:var(--color-red);">Delete</button>
      </div>
    </article>
  `).join('');

  $$('.btn-pc-preview', grid).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      const post = posts.find(p => p.id === id);
      if (post) openPreviewModal(post);
    });
  });

  $$('.btn-pc-publish', grid).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      const now = new Date(Date.now() + 3600000); // 1 hour from now
      const scheduledAt = now.toISOString().slice(0, 16);
      
      const userTime = prompt('Enter scheduled time (YYYY-MM-DDTHH:MM):', scheduledAt);
      if (!userTime) return;
      
      try {
        showLoading('Scheduling post…');
        await schedulePost({ post_id: id, scheduled_at: userTime });
        hideLoading();
        showToast('Post scheduled successfully!', 'success');
        await loadPostsForPostingPage();
      } catch (error) {
        hideLoading();
        showToast('Failed to schedule post', 'error');
      }
    });
  });
}

async function handleGeneratePosts() {
  const topics = $('#posting-topics')?.value;
  if (!topics || !topics.trim()) {
    showToast('Please enter at least one topic', 'error');
    return;
  }
  
  const topicList = topics.split('\n').map(t => t.trim()).filter(Boolean);
  
  try {
    showLoading('Generating posts…');
    runProgressBar(3000);
    
    let results;
    if (topicList.length === 1) {
      results = await generateSinglePost({ topic: topicList[0] });
    } else {
      results = await generateBatchPosts({ topics: topicList });
    }
    
    completeProgressBar();
    hideLoading();
    showToast(`Generated ${topicList.length} post(s) successfully!`, 'success');
    await loadPostsForPostingPage();
  } catch (error) {
    completeProgressBar();
    hideLoading();
    showToast(error.message || 'Failed to generate posts', 'error');
  }
}

function initPostingPage() {
  $('#btn-generate-posts')?.addEventListener('click', handleGeneratePosts);
  loadPostsForPostingPage();
}

/* ================================================================
   14. LOGS PAGE
   ================================================================ */

async function initLogsPage() {
  try {
    const response = await getLogs();
    const logs = response.data || [];
    renderLogs(logs);
  } catch (error) {
    console.error('Failed to load logs:', error);
    showToast('Failed to load logs', 'error');
  }
}

function renderLogs(logs) {
  const viewer = $('#log-viewer');
  if (!viewer) return;
  
  if (!logs.length) {
    viewer.innerHTML = `<p style="color:var(--color-text-faint);">No logs yet.</p>`;
    return;
  }

  viewer.innerHTML = logs.map(log => `
    <div class="log-entry">
      <span class="log-time">[${new Date(log.created_at).toTimeString().slice(0, 8)}]</span>
      <span class="log-msg log-msg--${escapeHtml(log.level)}">${escapeHtml(log.message)}</span>
    </div>
  `).join('');
  viewer.scrollTop = viewer.scrollHeight;
}

/* ================================================================
   15. CONNECTIONS PAGE
   ================================================================ */

let connectionConfigs = [];
let connectionJobs = [];
let profiles = [];

async function loadConnectionData() {
  try {
    const [configsResponse, jobsResponse, profilesResponse] = await Promise.all([
      getConnectionConfigs(),
      getConnectionJobs(),
      getProfiles()
    ]);
    
    connectionConfigs = configsResponse.data || [];
    connectionJobs = jobsResponse.data || [];
    profiles = profilesResponse.data || [];
    
    renderConfigsList(connectionConfigs);
    renderJobsList(connectionJobs);
    renderProfilesGrid(profiles);
  } catch (error) {
    console.error('Failed to load connection data:', error);
    showToast('Failed to load connection data', 'error');
  }
}

function renderConfigsList(configs) {
  const container = $('#conn-configs-list');
  if (!container) return;
  
  if (!configs.length) {
    container.innerHTML = `<p style="color:var(--color-text-faint);">No connection configurations yet.</p>`;
    return;
  }
  
  container.innerHTML = configs.map(config => `
    <div class="conn-config-item">
      <h3>${escapeHtml(config.name)}</h3>
      <p>Company: ${escapeHtml(config.company || 'Any')} | Role: ${escapeHtml(config.role || 'Any')} | Daily Limit: ${config.daily_limit}</p>
      <div class="config-actions">
        <button class="btn btn-sm btn-secondary" data-config-id="${config.id}">Edit</button>
        <button class="btn btn-sm btn-ghost delete-config" data-config-id="${config.id}">Delete</button>
      </div>
    </div>
  `).join('');
}

function renderJobsList(jobs) {
  const container = $('#conn-jobs-list');
  if (!container) return;
  
  if (!jobs.length) {
    container.innerHTML = `<p style="color:var(--color-text-faint);">No connection jobs yet.</p>`;
    return;
  }
  
  container.innerHTML = jobs.map(job => `
    <div class="conn-job-item">
      <h3>${escapeHtml(job.name)}</h3>
      <p>Status: ${statusBadge(job.status)} | Target: ${job.target_count || 'N/A'} | Completed: ${job.completed_count || 0}</p>
      <div class="job-actions">
        <button class="btn btn-sm btn-primary start-job" data-job-id="${job.id}">Start Job</button>
      </div>
    </div>
  `).join('');
  
  $$('.start-job', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const jobId = Number(btn.dataset.jobId);
      try {
        showLoading('Starting connection job…');
        await startConnectionJob(jobId);
        hideLoading();
        showToast('Connection job started!', 'success');
        await loadConnectionData();
      } catch (error) {
        hideLoading();
        showToast('Failed to start job', 'error');
      }
    });
  });
}

function renderProfilesGrid(profiles) {
  const grid = $('#conn-profiles-grid');
  if (!grid) return;
  
  if (!profiles.length) {
    grid.innerHTML = `<p style="color:var(--color-text-faint);">No profiles found yet.</p>`;
    return;
  }
  
  grid.innerHTML = profiles.map(profile => `
    <div class="profile-card">
      <h3>${escapeHtml(profile.name || 'Unknown')}</h3>
      <p style="font-size:.875rem;color:var(--color-text-secondary);">${escapeHtml(profile.title || profile.company || '')}</p>
      <p style="font-size:.75rem;color:var(--color-text-faint);">${profile.connection_request_sent ? 'Request sent' : 'Pending'}</p>
    </div>
  `).join('');
}

function initConnectionsPage() {
  $('#btn-save-conn-config')?.addEventListener('click', async () => {
    try {
      const configData = {
        name: $('#conn-config-name')?.value || 'New Config',
        company: $('#conn-company')?.value,
        role: $('#conn-role')?.value,
        industry: $('#conn-industry')?.value,
        location: $('#conn-location')?.value,
        university: $('#conn-university')?.value,
        keywords: $('#conn-keywords')?.value,
        daily_limit: Number($('#conn-daily-limit')?.value || 20),
        request_cooldown: Number($('#conn-cooldown')?.value || 5),
        connection_message: $('#conn-message')?.value,
        is_active: true
      };
      
      showLoading('Saving config…');
      await createConnectionConfig(configData);
      hideLoading();
      showToast('Configuration saved successfully!', 'success');
      await loadConnectionData();
    } catch (error) {
      hideLoading();
      showToast('Failed to save configuration', 'error');
    }
  });
  
  loadConnectionData();
}

/* ================================================================
   16. SETTINGS PAGE
   ================================================================ */

async function loadProviders() {
  try {
    const response = await getProviders();
    renderProvidersList(response.data || []);
  } catch (error) {
    console.error('Failed to load providers:', error);
    showToast('Failed to load providers', 'error');
  }
}

async function loadLinkedInApps() {
  try {
    const response = await getLinkedInApps();
    renderLinkedInAppsList(response.data || []);
  } catch (error) {
    console.error('Failed to load LinkedIn apps:', error);
    showToast('Failed to load LinkedIn apps', 'error');
  }
}

function renderLinkedInAppsList(apps) {
  const container = $('#linkedin-apps-list');
  if (!container) return;
  
  if (!apps.length) {
    container.innerHTML = `<p style="color:var(--color-text-faint);">No LinkedIn apps configured yet. Add your first app above!</p>`;
    return;
  }
  
  container.innerHTML = apps.map(app => `
    <div class="card" style="margin-bottom:16px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div>
          <h4 style="margin:0 0 4px 0;">Client ID: ${escapeHtml(app.client_id)}</h4>
          <p style="margin:4px 0 0 0;color:var(--color-text-faint);font-size:.75rem;">${escapeHtml(app.redirect_uri)}</p>
        </div>
        ${app.is_active ? '<span class="badge badge--success" style="margin-left:12px;">Active</span>' : ''}
      </div>
      <div style="display:flex;gap:8px;margin-top:12px;">
        <button class="btn btn-sm btn-secondary btn-edit-linkedin-app" data-id="${app.id}">Edit</button>
        ${!app.is_active ? `<button class="btn btn-sm btn-primary btn-activate-linkedin-app" data-id="${app.id}">Activate</button>` : ''}
        <button class="btn btn-sm btn-ghost btn-delete-linkedin-app" data-id="${app.id}" style="color:var(--color-red);">Delete</button>
      </div>
    </div>
  `).join('');
  
  $('.btn-edit-linkedin-app', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      const app = apps.find(a => a.id === id);
      if (app) openLinkedInAppModal(app);
    });
  });
  
  $('.btn-activate-linkedin-app', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      try {
        showLoading('Activating app…');
        await activateLinkedInApp(id);
        hideLoading();
        showToast('App activated successfully!', 'success');
        await loadLinkedInApps();
      } catch (error) {
        hideLoading();
        showToast('Failed to activate app', 'error');
      }
    });
  });
  
  $('.btn-delete-linkedin-app', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      showConfirm('Delete this LinkedIn app? This cannot be undone.', async () => {
        try {
          showLoading('Deleting app…');
          await deleteLinkedInApp(id);
          hideLoading();
          showToast('App deleted successfully!', 'success');
          await loadLinkedInApps();
        } catch (error) {
          hideLoading();
          showToast('Failed to delete app', 'error');
        }
      });
    });
  });
}

function renderProvidersList(providers) {
  const container = $('#providers-list');
  if (!container) return;
  
  if (!providers.length) {
    container.innerHTML = `<p style="color:var(--color-text-faint);">No AI providers configured yet. Add your first provider above!</p>`;
    return;
  }
  
  container.innerHTML = providers.map(provider => `
    <div class="card" style="margin-bottom:16px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
        <div>
          <h4 style="margin:0 0 4px 0;">${escapeHtml(provider.name)}</h4>
          <p style="margin:0;color:var(--color-text-secondary);font-size:.875rem;">Model: ${escapeHtml(provider.model_name)}</p>
          <p style="margin:4px 0 0 0;color:var(--color-text-faint);font-size:.75rem;">${escapeHtml(provider.base_url)}</p>
        </div>
        ${provider.is_active ? '<span class="badge badge--success" style="margin-left:12px;">Active</span>' : ''}
      </div>
      <div style="display:flex;gap:8px;margin-top:12px;">
        <button class="btn btn-sm btn-secondary btn-edit-provider" data-id="${provider.id}">Edit</button>
        ${!provider.is_active ? `<button class="btn btn-sm btn-primary btn-activate-provider" data-id="${provider.id}">Activate</button>` : ''}
        <button class="btn btn-sm btn-ghost btn-delete-provider" data-id="${provider.id}" style="color:var(--color-red);">Delete</button>
      </div>
    </div>
  `).join('');
  
  $$('.btn-edit-provider', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      const provider = providers.find(p => p.id === id);
      if (provider) openProviderModal(provider);
    });
  });
  
  $$('.btn-activate-provider', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      try {
        showLoading('Activating provider…');
        await activateProvider(id);
        hideLoading();
        showToast('Provider activated successfully!', 'success');
        await loadProviders();
      } catch (error) {
        hideLoading();
        showToast('Failed to activate provider', 'error');
      }
    });
  });
  
  $$('.btn-delete-provider', container).forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = Number(btn.dataset.id);
      showConfirm('Delete this AI provider? This cannot be undone.', async () => {
        try {
          showLoading('Deleting provider…');
          await deleteProvider(id);
          hideLoading();
          showToast('Provider deleted successfully!', 'success');
          await loadProviders();
        } catch (error) {
          hideLoading();
          showToast('Failed to delete provider', 'error');
        }
      });
    });
  });
}

async function initSettingsPage() {
  try {
    const response = await getLinkedInStatus();
    const isConnected = response.data?.is_connected;
    
    if (isConnected) {
      $('#linkedin-status-text')?.textContent = 'LinkedIn is connected';
      $('#linkedin-status-indicator')?.className = 'status-dot status-dot--success';
      $('#btn-linkedin-connect')?.textContent = 'Disconnect LinkedIn';
      $('#btn-linkedin-connect')?.onclick = async () => {
        try {
          await disconnectLinkedIn();
          showToast('LinkedIn disconnected', 'success');
          await initSettingsPage();
        } catch (error) {
          showToast('Failed to disconnect', 'error');
        }
      };
    } else {
      $('#linkedin-status-text')?.textContent = 'LinkedIn is not connected';
      $('#linkedin-status-indicator')?.className = 'status-dot status-dot--error';
      $('#btn-linkedin-connect')?.textContent = 'Connect LinkedIn';
      $('#btn-linkedin-connect')?.onclick = async () => {
        try {
          const response = await getLinkedInAuthUrl();
          window.location.href = response.data?.auth_url;
        } catch (error) {
          showToast('Failed to get auth URL', 'error');
        }
      };
    }
  } catch (error) {
    console.error('Failed to load LinkedIn status:', error);
  }
  
  // Load providers and LinkedIn apps
  await Promise.all([loadProviders(), loadLinkedInApps()]);
  
  // Add provider button
  $('#btn-add-provider')?.addEventListener('click', () => openProviderModal());
  
  // Provider modal save
  $('#btn-provider-save')?.addEventListener('click', async () => {
    const data = {
      name: $('#provider-name')?.value.trim(),
      model_name: $('#provider-model')?.value.trim(),
      api_key: $('#provider-api-key')?.value.trim(),
      base_url: $('#provider-base-url')?.value.trim(),
      is_active: $('#provider-active')?.checked
    };
    
    if (!data.name || !data.model_name || !data.base_url) {
      showToast('Please fill in all required fields', 'error');
      return;
    }
    
    if (!editingProviderId && !data.api_key) {
      showToast('API key is required for new providers', 'error');
      return;
    }
    
    try {
      showLoading('Saving provider…');
      
      if (editingProviderId) {
        await updateProvider(editingProviderId, data);
      } else {
        await createProvider(data);
      }
      
      hideLoading();
      closeProviderModal();
      showToast('Provider saved successfully!', 'success');
      await loadProviders();
    } catch (error) {
      hideLoading();
      showToast(error.message || 'Failed to save provider', 'error');
    }
  });
  
  // Provider modal cancel
  $('#btn-provider-cancel')?.addEventListener('click', closeProviderModal);
  $('#btn-provider-close')?.addEventListener('click', closeProviderModal);
  $('#provider-overlay')?.addEventListener('click', e => {
    if (e.target === $('#provider-overlay')) closeProviderModal();
  });
  
  // Add LinkedIn app button
  $('#btn-add-linkedin-app')?.addEventListener('click', () => openLinkedInAppModal());
  
  // LinkedIn app modal save
  $('#btn-linkedin-app-save')?.addEventListener('click', async () => {
    const data = {
      client_id: $('#linkedin-client-id')?.value.trim(),
      client_secret: $('#linkedin-client-secret')?.value.trim(),
      redirect_uri: $('#linkedin-redirect-uri')?.value.trim(),
      is_active: $('#linkedin-app-active')?.checked
    };
    
    if (!data.client_id || !data.redirect_uri) {
      showToast('Please fill in all required fields', 'error');
      return;
    }
    
    if (!editingLinkedInAppId && !data.client_secret) {
      showToast('Client secret is required for new apps', 'error');
      return;
    }
    
    try {
      showLoading('Saving app…');
      
      if (editingLinkedInAppId) {
        await updateLinkedInApp(editingLinkedInAppId, data);
      } else {
        await createLinkedInApp(data);
      }
      
      hideLoading();
      closeLinkedInAppModal();
      showToast('App saved successfully!', 'success');
      await loadLinkedInApps();
    } catch (error) {
      hideLoading();
      showToast(error.message || 'Failed to save app', 'error');
    }
  });
  
  // LinkedIn app modal cancel
  $('#btn-linkedin-app-cancel')?.addEventListener('click', closeLinkedInAppModal);
  $('#btn-linkedin-app-close')?.addEventListener('click', closeLinkedInAppModal);
  $('#linkedin-app-overlay')?.addEventListener('click', e => {
    if (e.target === $('#linkedin-app-overlay')) closeLinkedInAppModal();
  });
}

/* ================================================================
   17. MODAL EVENT BINDINGS
   ================================================================ */

function initModals() {
  $('#btn-modal-close')?.addEventListener('click', closePreviewModal);
  $('#btn-modal-cancel')?.addEventListener('click', closePreviewModal);
  $('#btn-confirm-close')?.addEventListener('click', closeConfirmDialog);
  $('#btn-confirm-cancel')?.addEventListener('click', closeConfirmDialog);
  
  $('#btn-confirm-delete')?.addEventListener('click', () => {
    if (pendingDeleteCallback) pendingDeleteCallback();
    closeConfirmDialog();
  });
  
  $('#modal-overlay')?.addEventListener('click', e => {
    if (e.target === $('#modal-overlay')) closePreviewModal();
  });
  $('#confirm-overlay')?.addEventListener('click', e => {
    if (e.target === $('#confirm-overlay')) closeConfirmDialog();
  });
  
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closePreviewModal();
      closeConfirmDialog();
      closeProviderModal();
      closeLinkedInAppModal();
    }
  });
}

/* ================================================================
   18. HERO ACTIONS
   ================================================================ */

function initHeroActions() {
  const btnPosting = $('#btn-hero-posting');
  const btnConnections = $('#btn-hero-connections');

  if (btnPosting) {
    btnPosting.addEventListener('click', e => {
      e.preventDefault();
      window.location.href = 'posting.html';
    });
  }

  if (btnConnections) {
    btnConnections.addEventListener('click', e => {
      e.preventDefault();
      window.location.href = 'connections.html';
    });
  }
}

/* ================================================================
   19. INIT
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initModals();

  const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'home';

  switch (currentPage) {
    case 'home':
      initHeroActions();
      break;
    case 'posting':
      initAllCharCounters();
      initTimeSlots();
      initPostingPage();
      break;
    case 'connections':
      initAllCharCounters();
      initConnectionsPage();
      break;
    case 'dashboard':
      initDashboard();
      break;
    case 'logs':
      initLogsPage();
      break;
    case 'settings':
      initSettingsPage();
      break;
  }
});
