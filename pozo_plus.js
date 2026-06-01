(function(){
  function esc(s){
    return String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  }

  function ensureUI(){
    if(document.getElementById('pozoPlusLauncher')) return;

    const modal = document.createElement('div');
    modal.className = 'pozo-plus-modal';
    modal.id = 'pozoPlusModal';
    modal.setAttribute('aria-hidden','true');
    modal.innerHTML = `
      <div class="pozo-plus-box">
        <div class="pozo-plus-head">
          <input class="pozo-plus-input" id="pozoPlusInput" placeholder="Buscar bomba, tag, serie, calle, proveedor, remito..." autocomplete="off">
          <button class="pozo-plus-close" id="pozoPlusClose">Cerrar</button>
        </div>
        <div class="pozo-plus-results" id="pozoPlusResults">
          <div class="pozo-plus-empty">Escribí al menos 2 caracteres para buscar en todo el sistema.</div>
        </div>
      </div>
    `;

    const btn = document.createElement('button');
    btn.className = 'pozo-plus-search-launcher';
    btn.id = 'pozoPlusLauncher';
    btn.type = 'button';
    btn.innerHTML = `🔎 Buscador global <span class="pozo-plus-kbd">Ctrl K</span>`;

    document.body.appendChild(modal);
    document.body.appendChild(btn);

    bindSearch();
  }

  function bindSearch(){
    const modal = document.getElementById('pozoPlusModal');
    const input = document.getElementById('pozoPlusInput');
    const results = document.getElementById('pozoPlusResults');
    const launcher = document.getElementById('pozoPlusLauncher');
    const closeBtn = document.getElementById('pozoPlusClose');
    let timer = null;

    function openSearch(){
      modal.classList.add('open');
      modal.setAttribute('aria-hidden','false');
      setTimeout(()=>input.focus(), 30);
    }

    function closeSearch(){
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden','true');
    }

    async function doSearch(){
      const q = input.value.trim();
      if(q.length < 2){
        results.innerHTML = '<div class="pozo-plus-empty">Escribí al menos 2 caracteres para buscar en todo el sistema.</div>';
        return;
      }

      results.innerHTML = '<div class="pozo-plus-empty">Buscando...</div>';

      try{
        const res = await fetch('/api/pozo-plus/search?q=' + encodeURIComponent(q) + '&limit=10');
        const data = await res.json();
        const arr = data.results || [];

        if(!arr.length){
          results.innerHTML = '<div class="pozo-plus-empty">No encontré resultados para <b>' + esc(q) + '</b>.</div>';
          return;
        }

        results.innerHTML = arr.map(item => `
          <div class="pozo-plus-item" data-type="${esc(item.type)}" data-id="${esc(item.id)}">
            <div class="pozo-plus-type">${esc(item.type)}</div>
            <div>
              <div class="pozo-plus-title">${esc(item.label)} ${item.title ? '— ' + esc(item.title) : ''}</div>
              <div class="pozo-plus-meta">${esc(item.meta || '')}</div>
            </div>
            <div class="pozo-plus-badge">${esc(item.badge || '')}</div>
          </div>
        `).join('');
      }catch(e){
        results.innerHTML = '<div class="pozo-plus-empty">Error buscando. Revisá sesión o conexión.</div>';
      }
    }

    function debounceSearch(){
      clearTimeout(timer);
      timer = setTimeout(doSearch, 220);
    }

    launcher.addEventListener('click', openSearch);
    closeBtn.addEventListener('click', closeSearch);
    input.addEventListener('input', debounceSearch);

    modal.addEventListener('click', (ev)=>{
      if(ev.target === modal) closeSearch();
    });

    document.addEventListener('keydown', (ev)=>{
      if((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 'k'){
        ev.preventDefault();
        openSearch();
      }
      if(ev.key === 'Escape' && modal.classList.contains('open')){
        closeSearch();
      }
    });

    results.addEventListener('click', (ev)=>{
      const item = ev.target.closest('.pozo-plus-item');
      if(!item) return;

      const type = item.dataset.type;
      closeSearch();

      const map = {
        bomba: 'inventario',
        perforacion: 'perforaciones',
        reparacion: 'reparaciones'
      };

      const panel = map[type];

      if(panel && typeof window.showPanel === 'function'){
        window.showPanel(panel);
      }
    });
  }

  async function injectDashboard(){
    try{
      const container = document.querySelector('#dashboard') || document.querySelector('.panel.active') || document.querySelector('.main');
      if(!container || document.getElementById('pozoPlusDash')) return;

      const res = await fetch('/api/pozo-plus/dashboard');
      const d = await res.json();
      const money = Number(d.costo_reparaciones_activas_usd || 0).toLocaleString('es-AR', {maximumFractionDigits:0});

      const wrap = document.createElement('div');
      wrap.id = 'pozoPlusDash';
      wrap.className = 'pozo-plus-dash';
      wrap.innerHTML = `
        <div class="pozo-plus-card"><div class="n">${esc(d.total_bombas)}</div><div class="l">Bombas total</div></div>
        <div class="pozo-plus-card good"><div class="n">${esc(d.montadas)}</div><div class="l">Montadas</div></div>
        <div class="pozo-plus-card"><div class="n">${esc(d.disponibles)}</div><div class="l">Disponibles</div></div>
        <div class="pozo-plus-card warn"><div class="n">${esc(d.en_reparacion)}</div><div class="l">En reparación</div></div>
        <div class="pozo-plus-card"><div class="n">USD ${esc(money)}</div><div class="l">Costo rep. activas</div></div>
      `;

      const firstCard = container.querySelector('.card');
      if(firstCard) container.insertBefore(wrap, firstCard);
      else container.prepend(wrap);
    }catch(e){}
  }

  function start(){
    ensureUI();
    injectDashboard();
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', start);
  }else{
    start();
  }
})();