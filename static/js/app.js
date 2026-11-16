const EYE='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>';
const EYEOFF='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.9 17.9A10.9 10.9 0 0 1 12 19C5.5 19 2 12 2 12a18 18 0 0 1 4.1-5.2M9.9 5.1A9.7 9.7 0 0 1 12 5c6.5 0 10 7 10 7a18 18 0 0 1-2.2 3.2M1 1l22 22"/></svg>';
// Add a show/hide eye button to every password input
document.querySelectorAll('input[type=password]').forEach(input => {
  const wrap = document.createElement('div');
  wrap.className = 'fld';
  input.parentNode.insertBefore(wrap, input);
  wrap.appendChild(input);
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'eye'; btn.innerHTML = EYE;
  btn.setAttribute('aria-label', 'Show password');
  btn.onclick = () => {
    const hide = input.type === 'password';
    input.type = hide ? 'text' : 'password';
    btn.innerHTML = hide ? EYEOFF : EYE;
    btn.setAttribute('aria-label', hide ? 'Hide password' : 'Show password');
  };
  wrap.appendChild(btn);
});
