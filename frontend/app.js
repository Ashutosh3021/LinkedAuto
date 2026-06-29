/* ================================================================
   LINKEDAUTO — APP.JS
   Vanilla JS, no frameworks
   ================================================================ */

'use strict';

/* ================================================================
   1. MOCK DATA
   ================================================================ */

const MOCK_SCHEDULED = [
  { id: 1, topic: 'Building side projects as a student',           date: '2024-07-15', time: '09:00', status: 'scheduled' },
  { id: 2, topic: 'What I learned shipping my first open-source library', date: '2024-07-16', time: '18:30', status: 'published' },
  { id: 3, topic: 'My data engineering roadmap at 20',             date: '2024-07-17', time: '09:00', status: 'pending' },
  { id: 4, topic: 'How I built PrepIQ in 3 months while in college', date: '2024-07-18', time: '12:00', status: 'scheduled' },
  { id: 5, topic: '5 Python libraries every ML student should know', date: '2024-07-19', time: '09:00', status: 'failed' },
  { id: 6, topic: 'FinNexus — paper trading app walkthrough',       date: '2024-07-20', time: '18:30', status: 'scheduled' },
];

const MOCK_POSTS = [
  {
    id: 1,
    topic: 'Building side projects as a student',
    body: 'Most students wait for the perfect time to build something. I was one of them.\n\nThen I started PrepIQ — an AI-powered exam prep platform — during my second year, debugging on hostel Wi-Fi at midnight.\n\nHere is what I learned: the perfect time never arrives. You ship with what you have, improve as you go, and the momentum carries you further than any plan ever could.\n\nIf you are a student sitting on an idea, start this weekend.',
    hashtags: ['#SideProject', '#StudentLife', '#BuildInPublic', '#AIEngineering'],
    scheduledTime: '2024-07-15 09:00',
    status: 'scheduled',
  },
  {
    id: 2,
    topic: 'What I learned shipping my first open-source library',
    body: 'I published JARVISE to PyPI last month. It broke immediately for 40% of users.\n\nThat single experience taught me more about dependency management, versioning, and CI hygiene than six months of coursework.\n\nBeing public about your work — even when it fails — is underrated. The feedback loop is instant and brutally honest.\n\nShip early. Break things. Fix them publicly.',
    hashtags: ['#OpenSource', '#Python', '#PyPI', '#LessonsLearned'],
    scheduledTime: '2024-07-16 18:30',
    status: 'published',
  },
  {
    id: 3,
    topic: 'My data engineering roadmap at 20',
    body: 'I am a second-year CSE student targeting a Data Engineering role by end of third year.\n\nHere is the exact roadmap I am following:\n\n→ SQL mastery — window functions, CTEs, query optimisation\n→ Python for data pipelines — Pandas, PySpark basics\n→ Cloud fundamentals — AWS S3, IAM, basics of EMR\n→ Orchestration — Airflow DAGs\n→ Capstone project — end-to-end pipeline with real datasets\n\nOff-campus. Tier-3 college. No placement cell.\n\nThe path is longer but entirely possible.',
    hashtags: ['#DataEngineering', '#Roadmap', '#TechCareers', '#Odisha'],
    scheduledTime: '2024-07-17 09:00',
    status: 'draft',
  },
  {
    id: 4,
    topic: 'How I built PrepIQ in 3 months',
    body: 'PrepIQ is a full-stack AI exam prep platform — Next.js frontend, FastAPI backend, Supabase for auth and DB, Gemini for generation.\n\nThe honest build log:\n\n• Week 1-2: Architecture and auth (Google/GitHub OAuth)\n• Week 3-4: PDF parser with multi-format fallback\n• Week 5-8: ML prediction engine — 37 tests written\n• Week 9-10: Deployment bugs (Python 3.13 broke everything)\n• Week 11-12: Mobile fixes and final polish\n\nDeployed. Vercel + Railway + Supabase. Zero cost.\n\nCollege never taught this. The internet did.',
    hashtags: ['#NextJS', '#FastAPI', '#SideProject', '#AIEngineering', '#BuildInPublic'],
    scheduledTime: '2024-07-18 12:00',
    status: 'scheduled',
  },
];

const MOCK_LOGS = [
  { time: '10:15:02', msg: 'Scheduler started successfully.',       type: 'success' },
  { time: '10:15:05', msg: 'OpenRouter API key validated.',         type: 'success' },
  { time: '10:20:00', msg: 'Generating post: "Building side projects as a student"', type: 'info' },
  { time: '10:20:04', msg: 'Post generated. 1842 characters.',      type: 'success' },
  { time: '10:21:00', msg: 'Post scheduled for 2024-07-15 09:00.',  type: 'success' },
  { time: '10:35:11', msg: 'Generating post: "Open-source lessons"', type: 'info' },
  { time: '10:35:14', msg: 'Post generated. 1624 characters.',      type: 'success' },
  { time: '10:35:15', msg: 'Post scheduled for 2024-07-16 18:30.',  type: 'success' },
  { time: '12:00:01', msg: 'Publishing post ID #2 to LinkedIn…',   type: 'info' },
  { time: '12:00:03', msg: 'Post published successfully. Post ID: li_9a3c7f2.', type: 'success' },
  { time: '14:00:00', msg: 'Post ID #5 publish failed. Retrying (1/3)…', type: 'error' },
  { time: '14:05:00', msg: 'Retry attempt 2/3 failed. API rate limit.', type: 'error' },
  { time: '14:10:00', msg: 'Retry attempt 3/3 failed. Post marked as failed.', type: 'error' },
  { time: '15:30:00', msg: 'Connection search: 12 profiles matched criteria.', type: 'info' },
  { time: '15:30:22', msg: 'Connection request sent to profile #1.', type: 'success' },
];

/* ================================================================
   2. UTILITY FUNCTIONS
   ================================================================ */

/**
 * Select a single DOM element.
 * @param {string} selector
 * @param {HTMLElement} [root]
 * @returns {HTMLElement|null}
 */
function $(selector, root = document) {
  return root.querySelector(selector);
}

/**
 * Select multiple DOM elements.
 * @param {string} selector
 * @param {HTMLElement} [root]
 * @returns {NodeList}
 */
function $$(selector, root = document) {
  return root.querySelectorAll(selector);
}

/**
 * Debounce a function.
 * @param {Function} fn
 * @param {number} delay
 * @returns {Function}
 */
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Format a date string as DD MMM YYYY.
 * @param {string} dateStr
 * @returns {string}
 */
function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

/**
 * Escape HTML entities.
 * @param {string} str
 * @returns {string}
 */
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

/**
 * Show a toast notification.
 * @param {string} message
 * @param {'success'|'error'|'info'|'warn'} [type]
 * @param {number} [duration] ms
 */
function showToast(message, type = 'info', duration = 3500) {
  const container = $('#toast-container');
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

/**
 * Show the loading overlay.
 * @param {string} [label]
 */
function showLoading(label = 'Processing…') {
  const overlay = $('#loading-overlay');
  const lbl = $('#loading-label');
  if (lbl) lbl.textContent = label;
  overlay.hidden = false;
}

/** Hide the loading overlay. */
function hideLoading() {
  $('#loading-overlay').hidden = true;
}

/* ================================================================
   5. PROGRESS BAR
   ================================================================ */

let progressTimer = null;

/**
 * Animate a fake progress bar for async actions.
 * @param {number} [duration] ms
 */
function runProgressBar(duration = 2000) {
  const wrap = $('#progress-bar-wrap');
  const bar  = $('#progress-bar');
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

/** Complete and hide the progress bar. */
function completeProgressBar() {
  clearInterval(progressTimer);
  const bar  = $('#progress-bar');
  const wrap = $('#progress-bar-wrap');
  bar.style.width = '100%';
  setTimeout(() => {
    wrap.hidden = true;
    bar.style.width = '0%';
  }, 400);
}

/* ================================================================
   6. MODAL SYSTEM
   ================================================================ */

/**
 * Open the post preview modal.
 * @param {Object} post
 */
function openPreviewModal(post) {
  const overlay = $('#modal-overlay');
  const body    = $('#modal-body');
  body.innerHTML = `
    <p class="post-card-topic" style="margin-bottom:10px;">${escapeHtml(post.topic)}</p>
    <p style="white-space:pre-line;margin-bottom:14px;">${escapeHtml(post.body)}</p>
    <div class="post-card-hashtags" style="margin-bottom:10px;">
      ${post.hashtags.map(h => `<span class="hashtag">${escapeHtml(h)}</span>`).join('')}
    </div>
    <p style="font-size:.8125rem;color:var(--color-text-faint);">Scheduled: ${escapeHtml(post.scheduledTime)}</p>
  `;
  overlay.hidden = false;
  $('#btn-modal-close').focus();
}

/** Close the post preview modal. */
function closePreviewModal() {
  $('#modal-overlay').hidden = true;
}

/* ================================================================
   7. CONFIRM DIALOG
   ================================================================ */

let pendingDeleteCallback = null;

/**
 * Show a confirmation dialog.
 * @param {string} message
 * @param {Function} onConfirm
 */
function showConfirm(message, onConfirm) {
  const overlay = $('#confirm-overlay');
  $('#confirm-message').textContent = message;
  pendingDeleteCallback = onConfirm;
  overlay.hidden = false;
  $('#btn-confirm-delete').focus();
}

/** Close the confirm dialog. */
function closeConfirmDialog() {
  $('#confirm-overlay').hidden = true;
  pendingDeleteCallback = null;
}

/* ================================================================
   8. NAVIGATION
   ================================================================ */

/** Initialise responsive navigation + hamburger toggle. */
function initNavigation() {
  const toggle = $('#btn-nav-toggle');
  const nav    = $('#main-nav');

  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(isOpen));
  });

  // Close nav when a link is clicked on mobile
  $$('.nav-link', nav).forEach(link => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });

  // Close nav when clicking outside on mobile
  document.addEventListener('click', e => {
    if (!nav.contains(e.target) && !toggle.contains(e.target)) {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Highlight active nav link based on current page
  const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'home';
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  const active = $(`.nav-link[data-page="${currentPage}"]`);
  if (active) active.classList.add('active');
}

/* ================================================================
   9. CHARACTER COUNTERS
   ================================================================ */

/** Attach char counter to a textarea. */
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

/** Initialise all character counters. */
function initAllCharCounters() {
  initCharCounter('posting-topics',   'count-topics');
  initCharCounter('posting-projects', 'count-projects');
  initCharCounter('conn-keywords',    'count-keywords');
  initCharCounter('conn-message',     'count-conn-message');
}

/* ================================================================
   10. TIME SLOTS (DYNAMIC)
   ================================================================ */

let timeSlotCount = 0;

/**
 * Add a new time slot input to the list.
 * @param {string} [value] pre-fill value
 */
function addTimeSlot(value = '') {
  const list = $('#posting-times-list');
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

/** Initialise time slot management. */
function initTimeSlots() {
  // Seed with defaults
  addTimeSlot('09:00');
  addTimeSlot('18:30');

  $('#btn-add-time').addEventListener('click', () => {
    addTimeSlot();
    showToast('Time slot added.', 'info', 2000);
  });
}

/* ================================================================
   11. FORM VALIDATION
   ================================================================ */

/**
 * Validate the posting config form.
 * @returns {boolean}
 */
function validatePostingForm() {
  let valid = true;
  const apiKey = $('#openrouter-api-key');

  // Clear previous errors
  $$('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  $$('.form-error').forEach(el => el.remove());

  // API key required
  if (!apiKey.value.trim()) {
    apiKey.classList.add('is-invalid');
    const err = document.createElement('span');
    err.className = 'form-error';
    err.textContent = 'OpenRouter API key is required.';
    apiKey.insertAdjacentElement('afterend', err);
    valid = false;
  }

  // Date range
  const start = $('#posting-start-date').value;
  const end   = $('#posting-end-date').value;
  if (start && end && start > end) {
    const endEl = $('#posting-end-date');
    endEl.classList.add('is-invalid');
    const err = document.createElement('span');
    err.className = 'form-error';
    err.textContent = 'End date must be after start date.';
    endEl.insertAdjacentElement('afterend', err);
    valid = false;
  }

  return valid;
}

/* ================================================================
   12. POSTING CONFIG BUTTONS
   ================================================================ */

/** Initialise posting form actions. */
function initPostingForm() {
  $('#btn-generate-posts').addEventListener('click', () => {
    if (!validatePostingForm()) {
      showToast('Please fix the errors before generating.', 'error');
      return;
    }
    showLoading('Generating posts…');
    runProgressBar(2500);
    setTimeout(() => {
      hideLoading();
      completeProgressBar();
      addLog('Post generation triggered via UI.', 'info');
      showToast('4 posts generated successfully!', 'success');
    }, 2500);
  });

  $('#btn-schedule-posts').addEventListener('click', () => {
    if (!validatePostingForm()) {
      showToast('Please fix the errors before scheduling.', 'error');
      return;
    }
    showLoading('Scheduling posts…');
    runProgressBar(1800);
    setTimeout(() => {
      hideLoading();
      completeProgressBar();
      addLog('Posts scheduled via UI.', 'success');
      showToast('Posts scheduled successfully.', 'success');
    }, 1800);
  });

  $('#btn-reset-posting').addEventListener('click', () => {
    $$('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    $$('.form-error').forEach(el => el.remove());
    showToast('Form reset.', 'info', 2000);
  });
}

/* ================================================================
   13. CONNECTION CONFIG BUTTONS
   ================================================================ */

/** Initialise connection form actions. */
function initConnectionForm() {
  $('#btn-search-professionals').addEventListener('click', () => {
    showLoading('Searching profiles…');
    runProgressBar(2000);
    setTimeout(() => {
      hideLoading();
      completeProgressBar();
      addLog('Profile search executed. 12 matches found.', 'info');
      showToast('Found 12 matching profiles.', 'success');
    }, 2000);
  });

  $('#btn-preview-results').addEventListener('click', () => {
    showToast('Preview requires a live backend connection.', 'info');
  });

  $('#btn-save-conn-config').addEventListener('click', () => {
    addLog('Connection configuration saved.', 'success');
    showToast('Connection configuration saved.', 'success');
  });
}

/* ================================================================
   14. SETTINGS FORM
   ================================================================ */

/** Initialise settings form actions. */
function initSettings() {
  $('#btn-save-settings').addEventListener('click', () => {
    addLog('App settings saved.', 'success');
    showToast('Settings saved.', 'success');
  });

  $('#btn-export-config').addEventListener('click', () => {
    const config = {
      exported_at:   new Date().toISOString(),
      db_location:   $('#setting-db-location').value,
      scheduler_interval: $('#setting-scheduler-interval').value,
    };
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'linkedauto-config.json';
    a.click();
    URL.revokeObjectURL(url);
    addLog('Configuration exported.', 'success');
    showToast('Configuration exported as JSON.', 'success');
  });
}

/* ================================================================
   15. SCHEDULED POSTS TABLE
   ================================================================ */

let scheduledPosts = [...MOCK_SCHEDULED];

/**
 * Return the HTML for a status badge.
 * @param {string} status
 * @returns {string}
 */
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

/**
 * Render the scheduled posts table.
 * @param {Array} posts
 */
function renderScheduledTable(posts) {
  const tbody = $('#tbody-scheduled');
  if (!posts.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--color-text-faint);padding:32px;">No scheduled posts found.</td></tr>`;
    return;
  }

  tbody.innerHTML = posts.map(post => `
    <tr data-id="${post.id}">
      <td>${escapeHtml(post.topic)}</td>
      <td>${formatDate(post.date)}</td>
      <td style="font-variant-numeric:tabular-nums;font-family:var(--font-mono);font-size:.8125rem;">${escapeHtml(post.time)}</td>
      <td>${statusBadge(post.status)}</td>
      <td class="col-actions">
        <div class="table-actions">
          <button class="btn btn-icon btn-sm btn-edit-post"    title="Edit"    data-id="${post.id}">✎</button>
          <button class="btn btn-icon btn-sm btn-preview-post" title="Preview" data-id="${post.id}">◉</button>
          <button class="btn btn-icon btn-sm btn-delete-post"  title="Delete"  data-id="${post.id}">✕</button>
        </div>
      </td>
    </tr>
  `).join('');

  // Bind action buttons
  $$('.btn-edit-post', tbody).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      showToast(`Edit post #${id} — requires backend.`, 'info');
    });
  });

  $$('.btn-preview-post', tbody).forEach(btn => {
    btn.addEventListener('click', () => {
      const id   = Number(btn.dataset.id);
      const post = MOCK_POSTS.find(p => p.id === id) || MOCK_POSTS[0];
      openPreviewModal(post);
    });
  });

  $$('.btn-delete-post', tbody).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      showConfirm('Delete this scheduled post? This cannot be undone.', () => {
        scheduledPosts = scheduledPosts.filter(p => p.id !== id);
        renderScheduledTable(scheduledPosts);
        addLog(`Scheduled post #${id} deleted.`, 'warn');
        showToast('Post deleted.', 'warn');
      });
    });
  });
}

/** Initialise table search. */
function initTableSearch() {
  const search = $('#search-scheduled');
  search.addEventListener('input', debounce(() => {
    const q = search.value.toLowerCase().trim();
    const filtered = scheduledPosts.filter(p =>
      p.topic.toLowerCase().includes(q) || p.status.includes(q)
    );
    renderScheduledTable(filtered);
  }, 200));
}

/* ================================================================
   16. GENERATED POSTS CARDS
   ================================================================ */

let generatedPosts = [...MOCK_POSTS];

/**
 * Render the generated posts grid.
 * @param {Array} posts
 */
function renderPostsGrid(posts) {
  const grid = $('#posts-grid');
  if (!posts.length) {
    grid.innerHTML = `<p style="color:var(--color-text-faint);">No generated posts yet. Use the Posting Configuration to generate posts.</p>`;
    return;
  }

  grid.innerHTML = posts.map(post => `
    <article class="post-card" data-id="${post.id}">
      <div class="post-card-header">
        <p class="post-card-topic">${escapeHtml(post.topic)}</p>
        ${statusBadge(post.status)}
      </div>
      <p class="post-card-body">${escapeHtml(post.body)}</p>
      <div class="post-card-hashtags">
        ${post.hashtags.map(h => `<span class="hashtag">${escapeHtml(h)}</span>`).join('')}
      </div>
      <div class="post-card-meta">
        <span>${escapeHtml(post.scheduledTime)}</span>
      </div>
      <div class="post-card-actions">
        <button class="btn btn-secondary btn-sm btn-pc-edit"        data-id="${post.id}">Edit</button>
        <button class="btn btn-ghost    btn-sm btn-pc-regenerate"   data-id="${post.id}">Regenerate</button>
        <button class="btn btn-ghost    btn-sm btn-pc-preview"      data-id="${post.id}">Preview</button>
        <button class="btn btn-primary  btn-sm btn-pc-publish"      data-id="${post.id}">Publish Now</button>
        <button class="btn btn-ghost    btn-sm btn-pc-delete"       data-id="${post.id}" style="color:var(--color-red);">Delete</button>
      </div>
    </article>
  `).join('');

  // Bind card action buttons
  $$('.btn-pc-edit', grid).forEach(btn => {
    btn.addEventListener('click', () => showToast(`Edit post #${btn.dataset.id} — requires backend.`, 'info'));
  });

  $$('.btn-pc-regenerate', grid).forEach(btn => {
    btn.addEventListener('click', () => {
      showLoading('Regenerating post…');
      setTimeout(() => {
        hideLoading();
        addLog(`Post #${btn.dataset.id} regenerated.`, 'success');
        showToast('Post regenerated.', 'success');
      }, 1600);
    });
  });

  $$('.btn-pc-preview', grid).forEach(btn => {
    btn.addEventListener('click', () => {
      const id   = Number(btn.dataset.id);
      const post = generatedPosts.find(p => p.id === id);
      if (post) openPreviewModal(post);
    });
  });

  $$('.btn-pc-publish', grid).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      showLoading('Publishing to LinkedIn…');
      setTimeout(() => {
        hideLoading();
        generatedPosts = generatedPosts.map(p =>
          p.id === id ? { ...p, status: 'published' } : p
        );
        renderPostsGrid(generatedPosts);
        addLog(`Post #${id} published to LinkedIn.`, 'success');
        showToast('Post published successfully!', 'success');
      }, 1800);
    });
  });

  $$('.btn-pc-delete', grid).forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.id);
      showConfirm('Delete this generated post?', () => {
        generatedPosts = generatedPosts.filter(p => p.id !== id);
        renderPostsGrid(generatedPosts);
        addLog(`Generated post #${id} deleted.`, 'warn');
        showToast('Post deleted.', 'warn');
      });
    });
  });
}

/* ================================================================
   17. LOG VIEWER
   ================================================================ */

const logEntries = [...MOCK_LOGS];

/**
 * Add a new log entry and re-render.
 * @param {string} msg
 * @param {'success'|'error'|'warn'|'info'} [type]
 */
function addLog(msg, type = 'info') {
  const now = new Date();
  const time = now.toTimeString().slice(0, 8);
  logEntries.push({ time, msg, type });
  renderLogs();
}

/** Render the log viewer. */
function renderLogs() {
  const viewer = $('#log-viewer');
  viewer.innerHTML = logEntries.map(entry => `
    <div class="log-entry">
      <span class="log-time">[${escapeHtml(entry.time)}]</span>
      <span class="log-msg log-msg--${escapeHtml(entry.type)}">${escapeHtml(entry.msg)}</span>
    </div>
  `).join('');
  // Scroll to bottom
  viewer.scrollTop = viewer.scrollHeight;
}

/** Initialise log controls. */
function initLogs() {
  renderLogs();

  $('#btn-clear-logs').addEventListener('click', () => {
    logEntries.length = 0;
    renderLogs();
    showToast('Logs cleared.', 'info', 2000);
  });

  $('#btn-export-logs').addEventListener('click', () => {
    const text = logEntries.map(e => `[${e.time}] [${e.type.toUpperCase()}] ${e.msg}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'linkedauto-logs.txt';
    a.click();
    URL.revokeObjectURL(url);
    showToast('Logs exported.', 'success');
  });
}

/* ================================================================
   18. MODAL EVENT BINDINGS
   ================================================================ */

/** Bind modal open/close events. */
function initModals() {
  // Post preview modal
  $('#btn-modal-close').addEventListener('click', closePreviewModal);
  $('#btn-modal-cancel').addEventListener('click', closePreviewModal);
  $('#btn-modal-publish').addEventListener('click', () => {
    closePreviewModal();
    showLoading('Publishing…');
    setTimeout(() => {
      hideLoading();
      addLog('Post published via preview modal.', 'success');
      showToast('Post published!', 'success');
    }, 1500);
  });

  // Confirm dialog
  $('#btn-confirm-close').addEventListener('click', closeConfirmDialog);
  $('#btn-confirm-cancel').addEventListener('click', closeConfirmDialog);
  $('#btn-confirm-delete').addEventListener('click', () => {
    if (pendingDeleteCallback) pendingDeleteCallback();
    closeConfirmDialog();
  });

  // Close modals on overlay click
  $('#modal-overlay').addEventListener('click', e => {
    if (e.target === $('#modal-overlay')) closePreviewModal();
  });
  $('#confirm-overlay').addEventListener('click', e => {
    if (e.target === $('#confirm-overlay')) closeConfirmDialog();
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closePreviewModal();
      closeConfirmDialog();
    }
  });
}

/* ================================================================
   19. DUMMY DASHBOARD UPDATES
   ================================================================ */

/** Periodically nudge dashboard stats to simulate live data. */
function initDashboardUpdates() {
  setInterval(() => {
    const stats = {
      'stat-generated':   () => Math.floor(48 + Math.random() * 3),
      'stat-connections': () => Math.floor(143 + Math.random() * 5),
    };

    Object.entries(stats).forEach(([id, fn]) => {
      const el = $(`#${id}`);
      if (el) el.textContent = fn();
    });
  }, 8000);
}

/* ================================================================
   20. HERO ACTIONS
   ================================================================ */

/** Initialise hero CTA buttons. */
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
   21. INIT
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
      initPostingForm();
      renderScheduledTable(scheduledPosts);
      initTableSearch();
      renderPostsGrid(generatedPosts);
      break;
    case 'connections':
      initAllCharCounters();
      initConnectionForm();
      break;
    case 'dashboard':
      initDashboardUpdates();
      break;
    case 'logs':
      initLogs();
      break;
    case 'settings':
      initSettings();
      break;
  }
});