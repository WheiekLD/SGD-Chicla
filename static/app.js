'use strict';

const glyphs = {
  municipal: '<path d="M3 9l9-5 9 5M4 9h16M5 19h14M3 21h18M7 10v8m5-8v8m5-8v8"/>',
  inbox: '<path d="M4 5h16l2 10v4a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-4L4 5zM2 15h6l2 2h4l2-2h6"/>',
  'file-plus': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M12 11v7m-3.5-3.5h7"/>',
  archive: '<path d="M4 8v12h16V8M3 4h18v4H3zm6 8h6"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m20 0v-2a4 4 0 0 0-3-4m-3-11a4 4 0 0 1 0 8"/><circle cx="9" cy="8" r="4"/>',
  shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11zM9 12l2 2 4-4"/>',
  flask: '<path d="M9 3h6m-5 0v6l-6 9a2 2 0 0 0 1.7 3h12.6a2 2 0 0 0 1.7-3l-6-9V3M7 15h10"/>',
  'chevron-right': '<path d="m9 18 6-6-6-6"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="m16 16 4 4"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8m-8 4h6"/>',
  undo: '<path d="M8 7 3 12l5 5m-5-5h13a4 4 0 0 1 4 4"/>',
  arrow: '<path d="M19 12H5m7-7-7 7 7 7"/>',
  paperclip: '<path d="m21 11-9 9a5 5 0 0 1-7-7l10-10a3 3 0 0 1 4 4L9 17a1 1 0 0 1-2-2l9-9"/>',
};
const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${glyphs[name]}</svg>`;
document.querySelectorAll('[data-icon]').forEach(element => { element.innerHTML = icon(element.dataset.icon); });

const navigation = document.querySelector('#navigation');
const menu = document.querySelector('#menu');
function setNav(open) {
  navigation.classList.toggle('open', open);
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Ocultar navegación' : 'Mostrar navegación');
}
if (menu) {
  menu.addEventListener('click', () => setNav(!navigation.classList.contains('open')));
  document.addEventListener('click', event => {
    if (!navigation.contains(event.target) && !menu.contains(event.target)) setNav(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navigation.classList.contains('open')) {
      setNav(false);
      menu.focus();
    }
  });
}
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
