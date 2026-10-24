const toggle = document.querySelector('#nav-toggle');
toggle?.addEventListener('click', () => {
  const expanded = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!expanded));
  document.querySelector('#nav-links').classList.toggle('hidden', expanded);
  document.querySelector('#nav-links').classList.toggle('flex', !expanded);
});
