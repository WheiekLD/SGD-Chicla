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

const areas = ['Mesa de Partes', 'Secretaría General', 'Gestión Ambiental', 'Infraestructura'];
const recipients = areas.slice(1);
const names = {'Secretaría General':'Ana Rojas', 'Gestión Ambiental':'Elena Torres', 'Infraestructura':'Marco Díaz'};
const states = {
  registered: ['Registrado', 'file'], pending: ['Por recibir', 'inbox'], active: ['En atención', 'clock'],
  returned: ['Devuelto', 'undo'], done: ['Atendido', 'check'], archived: ['Archivado', 'archive'],
};
const profiles = {admin:'Administrador', office:'Mesa de Partes', area:'Elena Torres'};
const initials = {admin:'AD', office:'MP', area:'ET'};
const sample = [
  ['0128','Solicitud de mantenimiento de vía vecinal','Solicitud','Infraestructura','pending','12 nov 2026','Presencial','Asociación Vecinal Mirador','18 nov 2026'],
  ['0127','Informe de inspección ambiental','Informe','Gestión Ambiental','active','12 nov 2026','Interno','Equipo técnico de ejemplo','17 nov 2026'],
  ['0126','Solicitud de acceso a información pública','Solicitud','Secretaría General','registered','11 nov 2026','Presencial','María Gómez (ejemplo)',''],
  ['0125','Oficio de coordinación interinstitucional','Oficio','Secretaría General','returned','11 nov 2026','Presencial','Oficina de Enlace (ejemplo)',''],
  ['0124','Programación de limpieza de espacios públicos','Memorando','Gestión Ambiental','pending','10 nov 2026','Interno','Unidad de Servicios (ejemplo)','19 nov 2026'],
  ['0123','Constancia de recepción de materiales','Acta','Infraestructura','done','10 nov 2026','Interno','Almacén (ejemplo)',''],
  ['0122','Inventario de mobiliario municipal','Informe','Secretaría General','archived','9 nov 2026','Interno','Equipo de Inventario (ejemplo)',''],
  ['0121','Solicitud de revisión de señalización vial','Solicitud','Infraestructura','pending','9 nov 2026','Presencial','Junta Barrial (ejemplo)',''],
  ['0120','Coordinación de jornada de reciclaje','Oficio','Gestión Ambiental','done','9 nov 2026','Interno','Comité Ambiental (ejemplo)',''],
];
const demoEvents = {
  pending:['Derivado','Mesa de Partes','Remisión al área para revisión.'],
  active:['Recepción confirmada','Elena Torres','El área inició la atención.'],
  returned:['Devuelto a Mesa de Partes','Ana Rojas','La documentación corresponde a otra área.'],
  done:['Atención completada','Responsable de área','Se registró la actuación de cierre.'],
  archived:['Expediente archivado','Mesa de Partes','Atención concluida.'],
};
const records = sample.map(([suffix,subject,type,area,state,date,channel,sender,due]) => ({
  id:'CH-2026-' + suffix, subject, type, area, state, date, channel, sender, due, attachments:[],
  history:[...(demoEvents[state] ? [{title:demoEvents[state][0], actor:demoEvents[state][1], detail:demoEvents[state][2],date}] : []),
    {title:'Expediente registrado', actor:'Mesa de Partes', detail:'Se asignó el correlativo interno.', date}],
}));
const activity = [];
const perPage = 6;
const view = document.querySelector('#view');
const dialog = document.querySelector('#action-dialog');
const profileField = document.querySelector('#profile');
const nav = document.querySelector('#navigation');
const menu = document.querySelector('#menu');
let profile = profileField.value;
let filter = {tab:'all', search:'', state:'', area:'', page:1};
let feedbackTimer;

const safe = value => String(value ?? '').replace(/[&<>"']/g, character => ({
  '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;',
})[character]);
const normalize = value => value.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
const status = key => `<span class="status status-${key}">${icon(states[key][1])}${states[key][0]}</span>`;
const options = (values, selected = '') => values.map(value => `<option${value === selected ? ' selected' : ''}>${safe(value)}</option>`).join('');
const stateOptions = () => Object.entries(states).map(([key,[label]]) => `<option value="${key}"${key === filter.state ? ' selected' : ''}>${label}</option>`).join('');
const visible = item => profile !== 'area' || (item.area === 'Gestión Ambiental' && ['pending','active','done','archived'].includes(item.state));
const today = () => new Intl.DateTimeFormat('es-PE', {day:'numeric',month:'short',year:'numeric',timeZone:'America/Lima'}).format(new Date());
const allowed = page => !(['usuarios','bitacora'].includes(page) && profile !== 'admin') && !(page === 'registro' && profile === 'area');
const setNav = open => { nav.classList.toggle('open', open); menu.setAttribute('aria-expanded', String(open)); menu.setAttribute('aria-label', open ? 'Ocultar navegación' : 'Mostrar navegación'); };

function notify(message) {
  const region = document.querySelector('#feedback');
  region.textContent = message;
  clearTimeout(feedbackTimer);
  feedbackTimer = setTimeout(() => { region.textContent = ''; }, 4200);
}
function addMovement(item, title, detail = '') {
  const event = {title, actor:profiles[profile], detail, date:today()};
  item.history.unshift(event);
  activity.unshift({...event, id:item.id});
}
function heading(title, description, action = '') {
  return `<div class="heading"><div><h1>${title}</h1><p>${description}</p></div>${action}</div>`;
}
function chooseTab(tab) {
  filter = {...filter, tab, state:'', page:1};
  if (location.hash !== '#bandeja' && location.hash !== '') location.hash = 'bandeja';
  else drawListControls();
}
function drawListControls() {
  const pool = records.filter(visible).filter(item => item.state !== 'archived');
  const tabs = [['all','Todos'],['registered','Por derivar'],['pending','Por recibir'],['active','En atención'],['returned','Devueltos'],['done','Atendidos']];
  document.querySelector('#tabs').innerHTML = tabs.map(([key,label]) => `<button type="button" class="tab" data-tab="${key}" aria-pressed="${filter.tab === key}">${label}<span>${key === 'all' ? pool.length : pool.filter(item => item.state === key).length}</span></button>`).join('');
  document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => { chooseTab(button.dataset.tab); document.querySelector(`[data-tab="${button.dataset.tab}"]`).focus(); }));
  document.querySelector('#state').value = filter.state;
  document.querySelectorAll('[data-metric]').forEach(button => button.setAttribute('aria-pressed', String(filter.tab === button.dataset.metric)));
  drawRows(false);
}
function drawRows(archive) {
  const query = normalize(filter.search.trim());
  const shown = records.filter(visible).filter(item =>
    (archive ? item.state === 'archived' : item.state !== 'archived' && (filter.tab === 'all' || filter.tab === item.state) && (!filter.state || filter.state === item.state)) &&
    (!filter.area || filter.area === item.area) &&
    (!query || normalize(`${item.id} ${item.subject} ${item.sender}`).includes(query)));
  const pages = Math.max(1, Math.ceil(shown.length / perPage));
  filter.page = Math.min(pages, filter.page);
  const start = (filter.page - 1) * perPage;
  const chunk = shown.slice(start, start + perPage);
  document.querySelector('#rows').innerHTML = chunk.length ? chunk.map(item => `<tr>
    <td><a class="record" href="#expediente/${item.id}">${item.id}</a><small>${safe(item.type)}</small></td>
    <td><strong>${safe(item.subject)}</strong><small>${safe(item.sender)}</small></td>
    <td>${safe(item.area)}</td><td>${status(item.state)}</td><td>${safe(item.date)}</td>
    <td><a class="icon-button" href="#expediente/${item.id}" aria-label="Abrir ${item.id}">${icon('chevron-right')}</a></td></tr>`).join('')
    : '<tr><td colspan="6" class="empty">No hay expedientes que coincidan. Cambia los filtros para volver a buscar.</td></tr>';
  document.querySelector('#range').textContent = shown.length ? `Mostrando ${start + 1}–${start + chunk.length} de ${shown.length} expedientes` : '0 expedientes';
  document.querySelector('#prev').disabled = filter.page <= 1;
  document.querySelector('#next').disabled = filter.page >= pages;
}
function listView(archive) {
  const pool = records.filter(visible);
  const metrics = [['pending','Por recibir'],['active','En atención'],['returned','Devueltos']];
  const create = allowed('registro') ? `<a class="button primary" href="#registro">${icon('plus')} Nuevo expediente</a>` : '';
  view.innerHTML = archive ? heading('Archivo', 'Consulta expedientes cuya atención ya concluyó.')
    : heading('Bandeja de expedientes', 'Consulta y seguimiento de los trámites de la municipalidad.', create);
  view.innerHTML += `${archive ? '' : `<section class="banner" aria-label="Resumen de la bandeja">
    <div class="banner-intro"><h2>Carga de trabajo</h2><p>Selecciona un estado para ver sus expedientes.</p></div>
    ${metrics.map(([key,label]) => `<button class="metric" type="button" data-metric="${key}"><strong>${String(pool.filter(item => item.state === key).length).padStart(2,'0')}</strong><span>${label}</span></button>`).join('')}
    </section>`}
    <section class="panel" aria-labelledby="list-title">
      <div class="panel-head"><h2 id="list-title">${archive ? 'Expedientes archivados' : 'Expedientes en trámite'}</h2></div>
      ${archive ? '' : '<div class="tabs" id="tabs" role="group" aria-label="Filtrar por bandeja"></div>'}
      <div class="filters">
        <label class="search">${icon('search')}<span class="sr-only">Buscar expediente o asunto</span><input id="search" type="search" placeholder="Buscar código, asunto o remitente" value="${safe(filter.search)}"></label>
        ${archive ? '' : `<select id="state" class="field" aria-label="Estado"><option value="">Todos los estados</option>${stateOptions()}</select>`}
        <select id="area" class="field" aria-label="Área"><option value="">Todas las áreas</option>${options(areas,filter.area)}</select>
      </div>
      <div class="table-wrap" tabindex="0" role="region" aria-label="Resultados de expedientes">
        <table><thead><tr><th scope="col">Expediente</th><th scope="col">Asunto</th><th scope="col">Área</th><th scope="col">Estado</th><th scope="col">Registro</th><th scope="col"><span class="sr-only">Abrir</span></th></tr></thead><tbody id="rows"></tbody></table>
      </div>
      <div class="row-end"><span id="range" aria-live="polite"></span><div><button type="button" class="icon-button" id="prev" aria-label="Página anterior">${icon('arrow')}</button> <button type="button" class="icon-button" id="next" aria-label="Página siguiente">${icon('chevron-right')}</button></div></div>
    </section>`;
  [['search','input'],['state','change'],['area','change']].forEach(([key,event]) => {
    document.getElementById(key)?.addEventListener(event, e => {
      filter[key] = e.target.value;
      if (key === 'state') filter.tab = 'all';
      filter.page = 1;
      if (key === 'state') drawListControls();
      else drawRows(archive);
    });
  });
  document.querySelectorAll('[data-metric]').forEach(button => button.addEventListener('click', () => chooseTab(button.dataset.metric)));
  document.querySelector('#prev').onclick = () => { filter.page--; drawRows(archive); };
  document.querySelector('#next').onclick = () => { filter.page++; drawRows(archive); };
  if (archive) drawRows(true);
  else drawListControls();
}
function showRecord(item) {
  const entries = [['Tipo',item.type],['Fecha de registro',item.date],['Remitente',item.sender],['Canal de ingreso',item.channel],
    ['Área asignada',item.area],['Responsable', ['registered','returned'].includes(item.state) ? 'Mesa de Partes' : names[item.area]],
    ['Fecha objetivo',item.due || 'Sin fecha asignada']];
  const actions = [];
  if (profile !== 'area' && ['registered','returned'].includes(item.state)) actions.push(['derive','Derivar']);
  if (profile !== 'office' && item.state === 'pending') actions.push(['receive','Confirmar recepción'],['return','Devolver']);
  if (profile !== 'office' && item.state === 'active') actions.push(['finish','Marcar como atendido'],['return','Devolver']);
  if (profile !== 'area' && item.state === 'done') actions.push(['archive','Archivar']);
  view.innerHTML = `<a class="back" href="#${item.state === 'archived' ? 'archivo' : 'bandeja'}">${icon('arrow')} Volver a ${item.state === 'archived' ? 'Archivo' : 'Bandeja'}</a>
    ${heading(item.id, safe(item.subject), status(item.state))}
    <div class="detail-grid">
      <div>
        <section class="panel pad"><h2>Datos del expediente</h2><dl class="details">${entries.map(([label,value]) => `<div><dt>${label}</dt><dd>${safe(value)}</dd></div>`).join('')}</dl>
          <div class="action-list">${actions.map(([key,label],index) => `<button type="button" class="button${index === 0 ? ' primary' : ''}" data-action="${key}">${label}</button>`).join('')}
          <button type="button" class="button" id="print">${item.state === 'registered' ? 'Imprimir cargo' : 'Imprimir ficha'}</button></div>
          <p class="print-note">SGD Chicla · Prototipo web</p>
        </section>
        <section class="panel pad"><h2>Adjuntos</h2>${item.attachments.length ? item.attachments.map(file => `<p class="file-line">${icon('paperclip')}${safe(file)}</p>`).join('') : '<p class="note">Este expediente no tiene archivos adjuntos.</p>'}
        ${item.state !== 'archived' ? '<label class="note file-line" for="attach">Agregar PDF</label><input type="file" id="attach" accept=".pdf,application/pdf"><p id="attach-error" class="note" role="alert"></p>' : ''}</section>
      </div>
      <section class="panel pad"><h2>Historial de custodia</h2><p class="note">Movimientos del expediente, del más reciente al más antiguo.</p>
        <ol class="timeline">${item.history.map(event => `<li><strong>${safe(event.title)}</strong><small>${safe(event.date)} · ${safe(event.actor)}</small><p>${safe(event.detail)}</p></li>`).join('')}</ol>
      </section>
    </div>`;
  document.querySelectorAll('[data-action]').forEach(button => button.onclick = () => openAction(item, button.dataset.action, button.textContent));
  document.querySelector('#print').onclick = () => window.print();
  document.querySelector('#attach')?.addEventListener('change', event => {
    const file = event.target.files[0];
    if (!file) return;
    if (!/\.pdf$/i.test(file.name) || (file.type && file.type !== 'application/pdf') || file.size > 5 * 1024 ** 2 || item.attachments.length >= 3) {
      document.querySelector('#attach-error').textContent = 'Selecciona un PDF de hasta 5 MiB. Se permiten tres adjuntos por expediente.';
      event.target.value = '';
      return;
    }
    item.attachments.push(file.name);
    addMovement(item, 'Adjunto agregado', file.name);
    showRecord(item);
    notify('Adjunto registrado.');
  });
}
function openAction(item, key, title) {
  const moves = {derive:['pending','Expediente derivado'],receive:['active','Recepción confirmada'],return:['returned','Devuelto a Mesa de Partes'],finish:['done','Atención completada'],archive:['archived','Expediente archivado']};
  dialog.innerHTML = `<form id="movement"><h2 id="dialog-title">${title}</h2><p class="note">${item.id}</p>
    ${key === 'derive' ? `<label>Área de destino<select class="field" name="area" required>${options(recipients,item.area)}</select></label>` : ''}
    <label>${key === 'return' ? 'Motivo de devolución' : 'Observación'}<textarea name="note" rows="3" maxlength="300"${key === 'return' ? ' required' : ''}></textarea></label>
    <div class="form-actions"><button type="submit" class="button primary">${title}</button><button type="button" class="button" id="cancel">Cancelar</button></div></form>`;
  dialog.querySelector('#cancel').onclick = () => dialog.close();
  dialog.querySelector('form').onsubmit = event => {
    event.preventDefault();
    const data = new FormData(event.target);
    const note = String(data.get('note')).trim();
    if (key === 'return' && !note) {
      const field = event.target.elements.note;
      field.setCustomValidity('Escribe el motivo de devolución.');
      field.reportValidity();
      field.oninput = () => field.setCustomValidity('');
      return;
    }
    if (key === 'derive') item.area = String(data.get('area'));
    const [next, text] = moves[key];
    item.state = next;
    addMovement(item, text, [key === 'derive' ? item.area : '',note].filter(Boolean).join(' · '));
    dialog.close();
    if (visible(item)) { showRecord(item); view.querySelector('h1').setAttribute('tabindex','-1'); view.querySelector('h1').focus(); }
    else location.hash = 'bandeja';
    notify(text + '.');
  };
  dialog.showModal();
}
function registerView() {
  view.innerHTML = heading('Registrar expediente','Registra un documento de entrada y genera su cargo interno.') + `
    <form class="panel form" id="register">
      <h2>Datos de ingreso</h2>
      <div class="form-grid">
        <label>Tipo de documento<select class="field" name="type" required><option value="">Selecciona un tipo</option>${options(['Solicitud','Oficio','Informe','Acta','Memorando'])}</select></label>
        <label>Canal de ingreso<select class="field" name="channel" required>${options(['Presencial','Interno'])}</select></label>
        <label class="wide">Asunto<input name="subject" required maxlength="120" placeholder="Ej. Solicitud de mantenimiento de vía vecinal"></label>
        <label>Remitente de prueba<input name="sender" required maxlength="100"></label>
        <label>Área sugerida<select class="field" name="area">${options(recipients)}</select></label>
      </div>
      <div class="form-actions"><button type="submit" class="button primary">${icon('plus')} Registrar expediente</button><a class="button" href="#bandeja">Cancelar</a></div>
    </form>`;
  document.querySelector('#register').onsubmit = event => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.target));
    for (const key of ['subject','sender']) {
      data[key] = data[key].trim();
      if (!data[key]) {
        const input = event.target.elements[key];
        input.setCustomValidity('Completa este campo.');
        input.reportValidity();
        input.oninput = () => input.setCustomValidity('');
        return;
      }
    }
    const id = 'CH-2026-' + String(129 + records.length - sample.length).padStart(4,'0');
    const item = {...data, id, state:'registered', date:today(), due:'', history:[], attachments:[]};
    addMovement(item, 'Expediente registrado', 'Se generó el código para el cargo interno.');
    records.unshift(item);
    location.hash = 'expediente/' + id;
    notify('Expediente registrado.');
  };
}
function simpleTable(title, desc, columns, rows) {
  view.innerHTML = heading(title, desc) + `<section class="panel"><div class="table-wrap" tabindex="0" role="region" aria-label="${title}">
    <table><thead><tr>${columns.map(column => `<th scope="col">${column}</th>`).join('')}</tr></thead><tbody>
    ${rows.length ? rows.map(row => `<tr>${row.map(cell => `<td>${safe(cell)}</td>`).join('')}</tr>`).join('') : `<tr><td class="empty" colspan="${columns.length}">Los movimientos que registres en este prototipo web aparecerán aquí.</td></tr>`}
    </tbody></table></div></section>`;
}
function render() {
  const [raw, id] = location.hash.slice(1).split('/');
  if (raw === 'principal') { document.querySelector('#principal').focus(); return; }
  const labels = {bandeja:'Bandeja', archivo:'Archivo', registro:'Registrar expediente', expediente:'Detalle', usuarios:'Usuarios y áreas', bitacora:'Bitácora'};
  const page = Object.hasOwn(labels,raw) && allowed(raw) ? raw : 'bandeja';
  document.querySelector('#crumb').textContent = labels[page];
  document.title = `${labels[page]} | SGD Chicla`;
  nav.querySelectorAll('[data-route]').forEach(link => {
    link.hidden = !allowed(link.dataset.route);
    if (link.dataset.route === page) link.setAttribute('aria-current','page');
    else link.removeAttribute('aria-current');
  });
  nav.querySelectorAll('.nav-label')[1].hidden = profile !== 'admin';
  if (page === 'registro') registerView();
  else if (page === 'expediente') {
    const item = records.find(record => record.id === id && visible(record));
    if (item) showRecord(item);
    else view.innerHTML = heading('Expediente no disponible','Vuelve a la bandeja para consultar los expedientes de este perfil.', '<a class="button" href="#bandeja">Volver a la bandeja</a>');
  } else if (page === 'usuarios') {
    simpleTable('Usuarios y áreas','Cuentas sintéticas y áreas asignadas para revisar los perfiles.', ['Cuenta','Perfil','Área'], [
      ['Administrador del prototipo web','Administrador','Administración'], ['Personal de Mesa de Partes','Administrativo','Mesa de Partes'],
      ...Object.entries(names).map(([area,name]) => [name,'Responsable de área',area]),
    ]);
  } else if (page === 'bitacora') {
    simpleTable('Bitácora','Movimientos registrados en esta sesión de la maqueta.', ['Fecha','Usuario','Expediente','Acción'], activity.map(event => [event.date,event.actor,event.id,event.title]));
  } else listView(page === 'archivo');
}
menu.onclick = () => setNav(!nav.classList.contains('open'));
document.addEventListener('click', event => {
  if (nav.classList.contains('open') && !nav.contains(event.target) && !menu.contains(event.target)) setNav(false);
});
nav.addEventListener('click', event => { if (event.target.closest('a')) setNav(false); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && nav.classList.contains('open')) { setNav(false); menu.focus(); } });
profileField.addEventListener('change', () => {
  profile = profileField.value;
  document.querySelector('#avatar').textContent = initials[profile];
  filter = {tab:'all', search:'', state:'', area:'', page:1};
  if (location.hash && location.hash !== '#bandeja') location.hash = 'bandeja';
  else render();
  notify('Perfil actualizado.');
});
window.addEventListener('hashchange', () => { render(); window.scrollTo(0, 0); document.querySelector('#principal').focus({preventScroll:true}); });
render();
