/* 共用：数据源加载。本地 = 127.0.0.1:8666/api/state；线上 = data.json + schedule.json */
function fmtTime(iso){
  if(!iso) return '-';
  return new Date(iso).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
}
async function loadData(){
  const err = document.getElementById('errbar');
  try {
    if (location.hostname === '127.0.0.1' || location.hostname === 'localhost') {
      const r = await fetch('/api/state');
      if (!r.ok) throw new Error('HTTP ' + r.status);
      err.style.display = 'none';
      return await r.json();
    }
    let d = {}, sd = {};
    try { d = await (await fetch('data.json?t=' + Date.now())).json(); } catch(e){}
    try { sd = await (await fetch('schedule.json?t=' + Date.now())).json(); } catch(e){}
    if (!Object.keys(d).length && !Object.keys(sd).length) throw new Error('empty');
    err.style.display = 'none';
    return Object.assign({}, d, {
      schedule: sd.schedule || d.schedule || [],
      standings: (d.standings && d.standings.leagues) ? d.standings : (sd.standings || {}),
      schedule_source: sd.source, schedule_updated: sd.updated,
    });
  } catch(e) {
    err.textContent = '⚠️ 数据加载失败。本地请确认已双击「一键启动.bat」，且系统代理没有拦截 127.0.0.1（Clash 加 localhost 白名单）。';
    err.style.display = 'block';
    return null;
  }
}
