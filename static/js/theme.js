(function(){
  const rootHtml = document.documentElement;
  // Support either id: theme-switch (new) or theme-toggle (legacy)
  const toggle = document.getElementById('theme-switch') || document.getElementById('theme-toggle');
  const storageKey = 'site-theme';

  function setTheme(theme){
    if(theme === 'dark'){
      rootHtml.setAttribute('data-theme', 'dark');
      if (toggle) { toggle.setAttribute('aria-pressed', 'true'); toggle.setAttribute('aria-label', 'Enable light mode'); }
    } else {
      rootHtml.removeAttribute('data-theme');
      if (toggle) { toggle.setAttribute('aria-pressed', 'false'); toggle.setAttribute('aria-label', 'Enable dark mode'); }
    }
    try{ localStorage.setItem(storageKey, theme); }catch(e){}
  }

  // On load, respect saved preference or system preference
  const saved = (function(){ try{return localStorage.getItem(storageKey);}catch(e){return null;} })();
  if(saved){ setTheme(saved); }
  else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches){ setTheme('dark'); }

  if(toggle){
    toggle.addEventListener('click', function(){
      const current = rootHtml.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();