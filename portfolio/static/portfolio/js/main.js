// =============================================================
//  プロフィール画面 メインスクリプト
//  - 活動・実績 / 資格 / スキルは Django がサーバーサイドでレンダリング済みのため、
//    ここではテーマ切替 / スクロールリベール / グローエフェクトのみを担当する
// =============================================================

/**
 * テーマ切替（ダーク / ライト）
 */
function initThemeToggle() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  const rootElement = document.documentElement;
  if (!themeToggleBtn) return;

  themeToggleBtn.addEventListener('click', () => {
    rootElement.classList.toggle('light-mode');
    const isLightMode = rootElement.classList.contains('light-mode');
    localStorage.setItem('theme', isLightMode ? 'light' : 'dark');
  });
}

/**
 * アバター画像のフォールバック
 */
function initAvatar() {
  const avatarDark = document.getElementById('avatar-dark');
  const avatarLight = document.getElementById('avatar-light');

  const darkFallback = 'https://ui-avatars.com/api/?name=YM&background=4682B4&color=fff';
  const lightFallback = 'https://ui-avatars.com/api/?name=YM&background=cbd5e1&color=0f172a';

  if (avatarDark) avatarDark.onerror = function () { this.src = darkFallback; };
  if (avatarLight) avatarLight.onerror = function () { this.src = lightFallback; };
}

/**
 * スクロールリベール（Intersection Observer）
 */
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
}

/**
 * カーソル追従グローエフェクト（デスクトップのみ）
 */
function initCursorGlow() {
  if (!window.matchMedia('(min-width: 1024px)').matches) return;

  const glow = document.getElementById('cursor-glow');
  if (!glow) return;
  let ticking = false;

  document.addEventListener('mousemove', (e) => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        glow.style.left = `${e.clientX}px`;
        glow.style.top = `${e.clientY}px`;
        ticking = false;
      });
      ticking = true;
    }
  });
}

// ---------------------------------------------------------------
//  起動
// ---------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initAvatar();
  initThemeToggle();
  initScrollReveal();
  initCursorGlow();

  // data-lucide 属性を持つ要素（サーバーサイドでレンダリング済み）をアイコンに変換
  if (window.lucide) {
    lucide.createIcons();
  }
});
