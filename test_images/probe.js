(() => {
  const overlay = document.querySelector('vite-error-overlay');
  if (overlay && overlay.shadowRoot) {
    const win = overlay.shadowRoot.querySelector('.window');
    if (win) win.style.display = 'none';
  }
  const root = document.getElementById('root');
  return {
    title: document.title,
    url: location.href,
    bodySnippet: document.body.innerHTML.substring(0, 800),
    rootHTML: root ? root.innerHTML.substring(0, 800) : '(no #root)',
    scripts: Array.from(document.scripts).map(s => s.src),
  };
})()
