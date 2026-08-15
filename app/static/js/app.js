(function () {
  const loginView = document.getElementById('login-view');
  const appView = document.getElementById('app-view');

  const usernameInput = document.getElementById('username-input');
  const usernameValue = document.getElementById('username-value');
  const usernameDropdown = document.getElementById('username-dropdown');
  const usernameField = document.getElementById('username-field');
  const passwordInput = document.getElementById('password-input');
  const loginBtn = document.getElementById('login-btn');
  const loginError = document.getElementById('login-error');

  const userTag = document.getElementById('user-tag');
  const logoutBtn = document.getElementById('logout-btn');
  const titleInput = document.getElementById('title-input');
  const startDate = document.getElementById('start-date');
  const endDate = document.getElementById('end-date');
  const previewWrap = document.getElementById('preview-wrap');
  const downloadBtn = document.getElementById('download-btn');
  const appError = document.getElementById('app-error');

  const bannerFileInput = document.getElementById('banner-file-input');
  const bannerUploadBtn = document.getElementById('banner-upload-btn');
  const bannerResetBtn = document.getElementById('banner-reset-btn');
  const bannerStatus = document.getElementById('banner-status');

  let allUsernames = [];
  let debounceTimer = null;

  // -------------------- Username searchable dropdown --------------------

  function loadUsernames() {
    fetch('/api/usernames')
      .then(r => r.json())
      .then(list => { allUsernames = list; })
      .catch(() => { allUsernames = []; });
  }

  function renderDropdown(filter) {
    const q = (filter || '').toLowerCase();
    const matches = allUsernames.filter(u => u.toLowerCase().includes(q));

    if (matches.length === 0) {
      usernameDropdown.classList.add('hidden');
      usernameDropdown.innerHTML = '';
      return;
    }

    usernameDropdown.innerHTML = '';
    matches.forEach(u => {
      const item = document.createElement('div');
      item.className = 'dropdown-item';
      item.textContent = u;
      item.addEventListener('mousedown', (e) => {
        e.preventDefault();
        usernameInput.value = u;
        usernameValue.value = u;
        usernameDropdown.classList.add('hidden');
      });
      usernameDropdown.appendChild(item);
    });
    usernameDropdown.classList.remove('hidden');
  }

  usernameInput.addEventListener('focus', () => renderDropdown(usernameInput.value));
  usernameInput.addEventListener('input', () => {
    usernameValue.value = '';
    renderDropdown(usernameInput.value);
  });
  document.addEventListener('click', (e) => {
    if (!usernameField.contains(e.target)) {
      usernameDropdown.classList.add('hidden');
    }
  });

  // -------------------- Login --------------------

  function attemptLogin() {
    const username = usernameValue.value || usernameInput.value;
    const password = passwordInput.value;
    loginError.textContent = '';

    if (!username || !password) {
      loginError.textContent = 'Enter username and password.';
      return;
    }

    loginBtn.disabled = true;
    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
      .then(r => r.json().then(data => ({ status: r.status, data })))
      .then(({ status, data }) => {
        loginBtn.disabled = false;
        if (status === 200 && data.ok) {
          enterApp(data.username);
        } else {
          loginError.textContent = data.error || 'Login failed.';
        }
      })
      .catch(() => {
        loginBtn.disabled = false;
        loginError.textContent = 'Something went wrong.';
      });
  }

  loginBtn.addEventListener('click', attemptLogin);
  passwordInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') attemptLogin();
  });

  // -------------------- Session check --------------------

  function checkSession() {
    fetch('/api/me')
      .then(r => r.json())
      .then(data => {
        if (data.logged_in) {
          enterApp(data.username);
        } else {
          loadUsernames();
        }
      })
      .catch(() => loadUsernames());
  }

  function enterApp(username) {
    loginView.classList.add('hidden');
    appView.classList.remove('hidden');
    userTag.textContent = username;
    refreshBannerStatus();
    updatePreview();
  }

  logoutBtn.addEventListener('click', () => {
    fetch('/api/logout', { method: 'POST' })
      .then(() => {
        appView.classList.add('hidden');
        loginView.classList.remove('hidden');
        usernameInput.value = '';
        usernameValue.value = '';
        passwordInput.value = '';
        loadUsernames();
      });
  });

  // -------------------- Custom banner --------------------

  function refreshBannerStatus() {
    fetch('/api/banner/status')
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          bannerStatus.textContent = data.has_custom_banner
            ? 'Using your published banner.'
            : 'Using the default banner.';
          bannerResetBtn.disabled = !data.has_custom_banner;
        }
      })
      .catch(() => {});
  }

  bannerUploadBtn.addEventListener('click', () => {
    const file = bannerFileInput.files[0];
    if (!file) {
      bannerStatus.textContent = 'Choose an image first.';
      return;
    }

    const formData = new FormData();
    formData.append('banner', file);

    bannerUploadBtn.disabled = true;
    bannerStatus.textContent = 'Publishing banner...';

    fetch('/api/banner/upload', { method: 'POST', body: formData })
      .then(r => r.json().then(data => ({ status: r.status, data })))
      .then(({ status, data }) => {
        bannerUploadBtn.disabled = false;
        if (status === 200 && data.ok) {
          bannerFileInput.value = '';
          refreshBannerStatus();
          updatePreview();
        } else {
          bannerStatus.textContent = data.error || 'Upload failed.';
        }
      })
      .catch(() => {
        bannerUploadBtn.disabled = false;
        bannerStatus.textContent = 'Something went wrong.';
      });
  });

  bannerResetBtn.addEventListener('click', () => {
    bannerResetBtn.disabled = true;
    fetch('/api/banner', { method: 'DELETE' })
      .then(() => {
        refreshBannerStatus();
        updatePreview();
      })
      .catch(() => {
        bannerResetBtn.disabled = false;
      });
  });

  // -------------------- Live preview --------------------

  function updatePreview() {
    const title = titleInput.value;
    const start = startDate.value;
    const end = endDate.value;

    fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, start_date: start, end_date: end })
    })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          previewWrap.innerHTML = '';
          const img = document.createElement('img');
          img.src = data.image;
          previewWrap.appendChild(img);
        }
      })
      .catch(() => {});
  }

  function debouncedUpdatePreview() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updatePreview, 250);
  }

  titleInput.addEventListener('input', debouncedUpdatePreview);
  startDate.addEventListener('change', debouncedUpdatePreview);
  endDate.addEventListener('change', debouncedUpdatePreview);

  // -------------------- Download --------------------

  downloadBtn.addEventListener('click', () => {
    appError.textContent = '';
    const title = titleInput.value.trim();
    const start = startDate.value;
    const end = endDate.value;

    if (!title || !start || !end) {
      appError.textContent = 'Fill in title, start date, and end date.';
      return;
    }

    downloadBtn.disabled = true;
    fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, start_date: start, end_date: end })
    })
      .then(async (r) => {
        downloadBtn.disabled = false;
        if (!r.ok) {
          const data = await r.json().catch(() => ({}));
          appError.textContent = data.error || 'Download failed.';
          return;
        }
        const blob = await r.blob();
        const disposition = r.headers.get('Content-Disposition') || '';
        const match = disposition.match(/filename="?([^"]+)"?/);
        const filename = match ? match[1] : 'banner.png';

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(() => {
        downloadBtn.disabled = false;
        appError.textContent = 'Something went wrong.';
      });
  });

  checkSession();
})();
