// === Password Gate (SHA-256, 閱讀阻擋用途，非安全保護) ===
(function () {
  'use strict';
  var ADMIN_HASH  = '__ADMIN_HASH__';
  var DEFAULT_HASH = '__DEFAULT_HASH__';
  var HASH_STORAGE = '__HASH_STORAGE_KEY__';
  var AUTH_KEY     = '__SESSION_KEY__';

  var gate = document.getElementById('passwordGate');
  if (!gate) return;

  // Already authenticated this session
  if (sessionStorage.getItem(AUTH_KEY) === '1') {
    gate.classList.add('hidden');
    setTimeout(function () { gate.style.display = 'none'; }, 600);
    return;
  }

  var pwInput      = document.getElementById('pwInput');
  var pwSubmit     = document.getElementById('pwSubmit');
  var pwError      = document.getElementById('pwError');
  var togglePw     = document.getElementById('togglePw');
  var adminToggle  = document.getElementById('adminToggle');
  var adminPanel   = document.getElementById('adminPanel');
  var adminPwInput = document.getElementById('adminPwInput');
  var adminContent = document.getElementById('adminContent');
  var pwList       = document.getElementById('pwList');
  var newPwInput   = document.getElementById('newPwInput');
  var addPwBtn     = document.getElementById('addPwBtn');
  var enterSiteBtn = document.getElementById('enterSiteBtn');
  var adminMsg     = document.getElementById('adminMsg');

  // --- SHA-256 ---
  function sha256(str) {
    var encoder = new TextEncoder();
    return crypto.subtle.digest('SHA-256', encoder.encode(str)).then(function (buf) {
      return Array.from(new Uint8Array(buf)).map(function (b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
    });
  }

  // --- Hash list management ---
  function getHashes() {
    try {
      var raw = localStorage.getItem(HASH_STORAGE);
      if (!raw) {
        var initial = [DEFAULT_HASH];
        localStorage.setItem(HASH_STORAGE, JSON.stringify(initial));
        return initial;
      }
      return JSON.parse(raw);
    } catch (e) { return [DEFAULT_HASH]; }
  }

  function saveHashes(list) {
    localStorage.setItem(HASH_STORAGE, JSON.stringify(list));
  }

  function enterSite() {
    sessionStorage.setItem(AUTH_KEY, '1');
    gate.classList.add('hidden');
    setTimeout(function () { gate.style.display = 'none'; }, 600);
  }

  // --- Toggle password visibility ---
  if (togglePw) {
    togglePw.addEventListener('click', function () {
      pwInput.type = pwInput.type === 'password' ? 'text' : 'password';
    });
  }

  // --- Check password ---
  function checkPassword() {
    var val = pwInput.value.trim();
    if (!val) {
      pwError.textContent = '請輸入密碼';
      return;
    }
    sha256(val).then(function (hash) {
      // Admin password
      if (hash === ADMIN_HASH) {
        pwError.textContent = '';
        sessionStorage.setItem(AUTH_KEY, '1');
        if (adminPanel) {
          adminPanel.classList.add('show');
          if (adminContent) adminContent.style.display = 'block';
          renderHashList();
        }
        return;
      }
      // User password
      var hashes = getHashes();
      if (hashes.indexOf(hash) !== -1) {
        enterSite();
      } else {
        pwError.textContent = '密碼錯誤，請重新輸入';
        pwInput.value = '';
        pwInput.focus();
      }
    });
  }

  pwSubmit.addEventListener('click', checkPassword);
  pwInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') checkPassword();
  });

  // --- Admin toggle ---
  if (adminToggle) {
    adminToggle.addEventListener('click', function () {
      adminPanel.classList.toggle('show');
    });
  }

  // --- Admin password real-time check ---
  if (adminPwInput) {
    var debounce = null;
    adminPwInput.addEventListener('input', function () {
      clearTimeout(debounce);
      debounce = setTimeout(function () {
        sha256(adminPwInput.value).then(function (hash) {
          if (hash === ADMIN_HASH) {
            if (adminContent) adminContent.style.display = 'block';
            renderHashList();
          } else {
            if (adminContent) adminContent.style.display = 'none';
          }
        });
      }, 200);
    });
  }

  // --- Render password hash list ---
  function renderHashList() {
    if (!pwList) return;
    var hashes = getHashes();
    pwList.innerHTML = '';
    hashes.forEach(function (h, i) {
      var li = document.createElement('li');
      var span = document.createElement('span');
      span.textContent = h.substring(0, 8) + '...';
      span.title = h;
      li.appendChild(span);
      var btn = document.createElement('button');
      btn.textContent = '刪除';
      btn.addEventListener('click', function () {
        if (hashes.length <= 1) {
          if (adminMsg) adminMsg.textContent = '至少保留一組密碼';
          return;
        }
        hashes.splice(i, 1);
        saveHashes(hashes);
        renderHashList();
        if (adminMsg) {
          adminMsg.textContent = '已刪除';
          setTimeout(function () { adminMsg.textContent = ''; }, 2000);
        }
      });
      li.appendChild(btn);
      pwList.appendChild(li);
    });
  }

  // --- Add password ---
  function addPassword() {
    var val = newPwInput.value.trim();
    if (!val) { if (adminMsg) adminMsg.textContent = '請輸入密碼'; return; }
    sha256(val).then(function (hash) {
      if (hash === ADMIN_HASH) { if (adminMsg) adminMsg.textContent = '不可新增管理員密碼'; return; }
      var hashes = getHashes();
      if (hashes.indexOf(hash) !== -1) { if (adminMsg) adminMsg.textContent = '此密碼已存在'; return; }
      hashes.push(hash);
      saveHashes(hashes);
      newPwInput.value = '';
      if (adminMsg) {
        adminMsg.textContent = '密碼已新增';
        setTimeout(function () { adminMsg.textContent = ''; }, 2000);
      }
      renderHashList();
    });
  }

  if (addPwBtn) {
    addPwBtn.addEventListener('click', addPassword);
  }
  if (newPwInput) {
    newPwInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') addPassword();
    });
  }

  // --- Enter site button (from admin panel) ---
  if (enterSiteBtn) {
    enterSiteBtn.addEventListener('click', enterSite);
  }
})();
