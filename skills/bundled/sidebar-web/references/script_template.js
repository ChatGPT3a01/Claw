/**
 * 側邊欄導覽網站 — 互動邏輯
 * 導覽切換、Markdown 渲染、響應式選單、程式碼複製
 * 側邊欄拖拉調整、設定面板、文字大小切換
 */

(function () {
  'use strict';

  // --- DOM Elements ---
  const navList = document.getElementById('navList');
  const contentInner = document.getElementById('contentInner');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  const menuToggle = document.getElementById('menuToggle');
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  const sidebarResizer = document.getElementById('sidebarResizer');
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsPanel = document.getElementById('settingsPanel');
  const settingsClose = document.getElementById('settingsClose');
  const fontSizeOptions = document.getElementById('fontSizeOptions');
  const themeOptions = document.getElementById('themeOptions');

  // --- State ---
  let currentUnitId = null;

  // --- Constants ---
  var SIDEBAR_MIN = 200;
  var SIDEBAR_MAX = 500;
  var STORAGE_KEY_SIDEBAR = 'sidebar-width';
  var STORAGE_KEY_FONTSIZE = 'font-size';
  var STORAGE_KEY_THEME = 'color-theme';
  var THEME_LIST = ['warm', 'ocean', 'forest', 'sakura'];

  // --- Initialize ---
  function init() {
    if (typeof UNITS_DATA === 'undefined') {
      contentInner.innerHTML = '<div class="loading">載入內容中...</div>';
      return;
    }

    buildNavigation();
    setupEventListeners();
    createScrollTopButton();
    restoreSettings();

    // 載入第一個有內容的單元
    var firstUnit = UNITS_DATA.find(function (u) { return !u.isGroup; });
    if (firstUnit) {
      loadUnit(firstUnit.id);
    }
  }

  // --- Restore Settings from localStorage ---
  function restoreSettings() {
    // Restore sidebar width
    var savedWidth = localStorage.getItem(STORAGE_KEY_SIDEBAR);
    if (savedWidth && window.innerWidth > 768) {
      var w = parseInt(savedWidth, 10);
      if (w >= SIDEBAR_MIN && w <= SIDEBAR_MAX) {
        setSidebarWidth(w);
      }
    }

    // Restore font size
    var savedFontSize = localStorage.getItem(STORAGE_KEY_FONTSIZE) || 'large';
    setFontSize(savedFontSize);

    // Restore theme
    var savedTheme = localStorage.getItem(STORAGE_KEY_THEME) || 'warm';
    setTheme(savedTheme);
  }

  // --- Build Navigation ---
  function buildNavigation() {
    navList.innerHTML = '';

    UNITS_DATA.forEach(function (unit) {
      var li = document.createElement('li');
      li.className = 'nav-item';

      var a = document.createElement('a');
      a.setAttribute('data-unit-id', unit.id);

      if (unit.isGroup) {
        li.className += ' group-title expanded';
        a.innerHTML = unit.shortTitle + ' <span class="expand-icon">&#9654;</span>';
        a.addEventListener('click', function (e) {
          e.preventDefault();
          toggleGroup(li);
        });
      } else if (unit.parent) {
        li.className += ' sub-item';
        li.setAttribute('data-parent', unit.parent);
        a.textContent = unit.shortTitle;
        a.addEventListener('click', function (e) {
          e.preventDefault();
          loadUnit(unit.id);
        });
      } else {
        a.textContent = unit.shortTitle;
        a.addEventListener('click', function (e) {
          e.preventDefault();
          loadUnit(unit.id);
        });
      }

      li.appendChild(a);
      navList.appendChild(li);
    });
  }

  // --- Toggle Group (expand/collapse) ---
  function toggleGroup(groupLi) {
    var isExpanded = groupLi.classList.contains('expanded');
    groupLi.classList.toggle('expanded');

    var groupId = groupLi.querySelector('a').getAttribute('data-unit-id');
    var subItems = navList.querySelectorAll('[data-parent="' + groupId + '"]');

    subItems.forEach(function (item) {
      item.style.display = isExpanded ? 'none' : '';
    });
  }

  // --- Load Unit ---
  function loadUnit(unitId) {
    var unit = UNITS_DATA.find(function (u) { return u.id === unitId; });
    if (!unit || unit.isGroup) return;

    currentUnitId = unitId;

    // Update nav active state
    var allLinks = navList.querySelectorAll('a');
    allLinks.forEach(function (link) {
      link.classList.remove('active');
    });
    var activeLink = navList.querySelector('[data-unit-id="' + unitId + '"]');
    if (activeLink) {
      activeLink.classList.add('active');
    }

    // Render markdown content
    renderContent(unit);

    // Close mobile sidebar
    closeSidebar();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- Render Content ---
  function renderContent(unit) {
    if (!unit.content) {
      contentInner.innerHTML = '<div class="welcome-screen"><h2>' + escapeHtml(unit.title) + '</h2><p>此單元暫無內容</p></div>';
      return;
    }

    if (typeof marked !== 'undefined') {
      marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function (code, lang) {
          if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(code, { language: lang }).value;
            } catch (e) { /* ignore */ }
          }
          if (typeof hljs !== 'undefined') {
            try {
              return hljs.highlightAuto(code).value;
            } catch (e) { /* ignore */ }
          }
          return code;
        }
      });

      var html = marked.parse(unit.content);
      contentInner.innerHTML = html;
    } else {
      contentInner.innerHTML = '<pre style="white-space: pre-wrap; padding: 24px;">' + escapeHtml(unit.content) + '</pre>';
    }

    addCopyButtons();

    if (typeof hljs !== 'undefined') {
      contentInner.querySelectorAll('pre code:not(.hljs)').forEach(function (block) {
        hljs.highlightElement(block);
      });
    }
  }

  // --- Add Copy Buttons to Code Blocks ---
  function addCopyButtons() {
    var pres = contentInner.querySelectorAll('pre');
    pres.forEach(function (pre) {
      var wrapper = document.createElement('div');
      wrapper.className = 'code-wrapper';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);

      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = '\u8907\u88fd';
      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        var text = code ? code.textContent : pre.textContent;
        copyToClipboard(text, btn);
      });
      wrapper.appendChild(btn);
    });
  }

  // --- Copy to Clipboard ---
  function copyToClipboard(text, btn) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function () {
        showCopied(btn);
      }).catch(function () {
        fallbackCopy(text, btn);
      });
    } else {
      fallbackCopy(text, btn);
    }
  }

  function fallbackCopy(text, btn) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      showCopied(btn);
    } catch (e) {
      // ignore
    }
    document.body.removeChild(textarea);
  }

  function showCopied(btn) {
    btn.textContent = '\u5df2\u8907\u88fd!';
    btn.classList.add('copied');
    setTimeout(function () {
      btn.textContent = '\u8907\u88fd';
      btn.classList.remove('copied');
    }, 2000);
  }

  // --- Mobile Sidebar ---
  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  // ============================================================
  // Sidebar Resizer (Drag to resize)
  // ============================================================
  function initSidebarResizer() {
    if (!sidebarResizer) return;

    var startX, startWidth;

    sidebarResizer.addEventListener('mousedown', function (e) {
      e.preventDefault();
      startX = e.clientX;
      startWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width'), 10);
      document.body.classList.add('resizing');

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });

    function onMouseMove(e) {
      var newWidth = startWidth + (e.clientX - startX);
      if (newWidth < SIDEBAR_MIN) newWidth = SIDEBAR_MIN;
      if (newWidth > SIDEBAR_MAX) newWidth = SIDEBAR_MAX;
      setSidebarWidth(newWidth);
    }

    function onMouseUp() {
      document.body.classList.remove('resizing');
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      var currentWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width'), 10);
      localStorage.setItem(STORAGE_KEY_SIDEBAR, currentWidth);
    }
  }

  function setSidebarWidth(px) {
    document.documentElement.style.setProperty('--sidebar-width', px + 'px');
  }

  // ============================================================
  // Settings Panel
  // ============================================================
  function initSettingsPanel() {
    if (!settingsBtn || !settingsPanel) return;

    settingsBtn.addEventListener('click', function () {
      var isOpen = settingsPanel.classList.contains('open');
      if (isOpen) {
        closeSettingsPanel();
      } else {
        openSettingsPanel();
      }
    });

    if (settingsClose) {
      settingsClose.addEventListener('click', closeSettingsPanel);
    }

    // Font size options
    if (fontSizeOptions) {
      fontSizeOptions.addEventListener('click', function (e) {
        var btn = e.target.closest('.settings-option');
        if (!btn) return;
        var size = btn.getAttribute('data-size');
        setFontSize(size);
        localStorage.setItem(STORAGE_KEY_FONTSIZE, size);
      });
    }

    // Theme options
    if (themeOptions) {
      themeOptions.addEventListener('click', function (e) {
        var btn = e.target.closest('.theme-card');
        if (!btn) return;
        var theme = btn.getAttribute('data-theme');
        setTheme(theme);
        localStorage.setItem(STORAGE_KEY_THEME, theme);
      });
    }
  }

  function openSettingsPanel() {
    settingsPanel.classList.add('open');
  }

  function closeSettingsPanel() {
    settingsPanel.classList.remove('open');
  }

  function setFontSize(size) {
    document.body.classList.remove('font-medium', 'font-large', 'font-xlarge');
    document.body.classList.add('font-' + size);

    if (fontSizeOptions) {
      var buttons = fontSizeOptions.querySelectorAll('.settings-option');
      buttons.forEach(function (btn) {
        btn.classList.toggle('active', btn.getAttribute('data-size') === size);
      });
    }
  }

  // --- Theme Switching ---
  function setTheme(theme) {
    // Remove all theme classes
    THEME_LIST.forEach(function (t) {
      document.body.classList.remove('theme-' + t);
    });
    // 'warm' is default (no class needed), others add class
    if (theme !== 'warm') {
      document.body.classList.add('theme-' + theme);
    }

    // Update active button
    if (themeOptions) {
      var cards = themeOptions.querySelectorAll('.theme-card');
      cards.forEach(function (card) {
        card.classList.toggle('active', card.getAttribute('data-theme') === theme);
      });
    }
  }

  // --- Scroll to Top Button ---
  function createScrollTopButton() {
    var btn = document.createElement('button');
    btn.className = 'scroll-top';
    btn.innerHTML = '&#9650;';
    btn.setAttribute('aria-label', '\u56de\u5230\u9802\u90e8');
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.body.appendChild(btn);

    window.addEventListener('scroll', function () {
      if (window.scrollY > 400) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    });
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Hamburger menu toggle
    menuToggle.addEventListener('click', function () {
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    // Overlay click to close
    overlay.addEventListener('click', function () {
      closeSidebar();
      closeSettingsPanel();
    });

    // Keyboard: Escape to close sidebar / settings
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        closeSidebar();
        closeSettingsPanel();
      }
    });

    // Keyboard navigation: left/right arrows for prev/next unit
    document.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      var contentUnits = UNITS_DATA.filter(function (u) { return !u.isGroup; });
      var currentIndex = contentUnits.findIndex(function (u) { return u.id === currentUnitId; });

      if (e.key === 'ArrowLeft' && currentIndex > 0) {
        loadUnit(contentUnits[currentIndex - 1].id);
      } else if (e.key === 'ArrowRight' && currentIndex < contentUnits.length - 1) {
        loadUnit(contentUnits[currentIndex + 1].id);
      }
    });

    // Fullscreen toggle
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', toggleFullscreen);

      document.addEventListener('fullscreenchange', updateFullscreenButton);
      document.addEventListener('webkitfullscreenchange', updateFullscreenButton);
    }

    // Initialize sidebar resizer
    initSidebarResizer();

    // Initialize settings panel
    initSettingsPanel();
  }

  // --- Fullscreen ---
  function toggleFullscreen() {
    if (!document.fullscreenElement && !document.webkitFullscreenElement) {
      var el = document.documentElement;
      if (el.requestFullscreen) {
        el.requestFullscreen();
      } else if (el.webkitRequestFullscreen) {
        el.webkitRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  }

  function updateFullscreenButton() {
    var isFS = !!(document.fullscreenElement || document.webkitFullscreenElement);
    var icon = document.getElementById('fullscreenIcon');
    var label = fullscreenBtn.querySelector('.btn-label');

    if (isFS) {
      fullscreenBtn.classList.add('fullscreen-active');
      if (icon) icon.innerHTML = '<path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>';
      if (label) label.textContent = '\u96e2\u958b\u5168\u87a2\u5e55';
    } else {
      fullscreenBtn.classList.remove('fullscreen-active');
      if (icon) icon.innerHTML = '<path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>';
      if (label) label.textContent = '\u5168\u87a2\u5e55';
    }
  }

  // --- Utility ---
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // --- Start ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
