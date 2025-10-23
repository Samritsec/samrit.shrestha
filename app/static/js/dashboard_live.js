// app/static/js/dashboard_live.js
(function(){
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');
  if (toggleBtn && sidebar){
    toggleBtn.addEventListener('click', () => {
      const collapsed = sidebar.getAttribute('data-collapsed') === 'true';
      sidebar.setAttribute('data-collapsed', String(!collapsed));
      window.TENSHI = window.TENSHI || {};
      window.TENSHI.collapsed = !collapsed;
      toggleBtn.title = (!collapsed ? 'Expand' : 'Collapse');
      toggleBtn.setAttribute('aria-label', (!collapsed ? 'Expand sidebar' : 'Collapse sidebar'));
    });
  }

  // Live fake uptime clock
  const elUptime = document.getElementById('kpi-uptime');
  let t0 = Date.now();
  function two(n){ return String(n).padStart(2,'0'); }
  function tick(){
    if (!elUptime) return;
    const s = Math.floor((Date.now()-t0)/1000);
    const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), ss = s%60;
    elUptime.textContent = `${two(h)}:${two(m)}:${two(ss)}`;
  }
  setInterval(tick, 1000); tick();

  // KPI pulse
  const elAlerts = document.getElementById('kpi-alerts');
  const elAlertsTrend = document.getElementById('kpi-alerts-trend');
  const elDevices = document.getElementById('kpi-devices');
  const elDevicesTrend = document.getElementById('kpi-devices-trend');

  function rand(min, max){ return Math.floor(Math.random()*(max-min+1))+min; }
  function pulseKPIs(){
    if (elAlerts){
      const base = Number(elAlerts.dataset.base || rand(1,5));
      const delta = [-1,0,1][rand(0,2)];
      const next = Math.max(0, base + delta);
      elAlerts.textContent = next;
      elAlerts.dataset.base = String(next);
      if (elAlertsTrend) elAlertsTrend.textContent = (delta >= 0 ? `▲ +${delta}` : `▼ ${delta}`) + ' past min';
    }
    if (elDevices){
      const base = Number(elDevices.dataset.base || rand(15,30));
      const delta = [-1,0,1][rand(0,2)];
      const next = Math.max(0, base + delta);
      elDevices.textContent = next;
      elDevices.dataset.base = String(next);
      if (elDevicesTrend) elDevicesTrend.textContent = (delta >= 0 ? `▲ +${delta}` : `▼ ${delta}`) + ' online';
    }
  }
  setInterval(pulseKPIs, 7000); pulseKPIs();

  // Refresh button fake latency
  const refreshBtn = document.getElementById('btn-refresh-events');
  if (refreshBtn){
    refreshBtn.addEventListener('click', () => {
      refreshBtn.disabled = true;
      refreshBtn.textContent = 'Refreshing…';
      setTimeout(() => {
        refreshBtn.disabled = false;
        refreshBtn.textContent = 'Refresh';
      }, 900);
    });
  }
})();
