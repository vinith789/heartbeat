const socket = io();
const statusDiv = document.getElementById('status');
const tbody = document.querySelector('#data-table tbody');
const rows = {}; // port -> row

function formatValues(values){
  if(!values) return '';
  return Object.entries(values).map(([k,v])=>`${k}=${v}`).join(', ');
}

function upsertRow(port, raw, result){
  let row = rows[port];
  const now = new Date().toLocaleTimeString();
  if(!row){
    row = document.createElement('tr');
    row.innerHTML = `<td class="port">${port}</td><td class="vals"></td><td class="alarms"></td><td class="ts"></td>`;
    rows[port] = row;
    tbody.appendChild(row);
  }
  const valsTd = row.querySelector('.vals');
  const alarmsTd = row.querySelector('.alarms');
  const tsTd = row.querySelector('.ts');
  valsTd.textContent = formatValues(result.values || {});
  if(result.result && result.result.alarms && result.result.alarms.length){
    alarmsTd.innerHTML = result.result.alarms.map(a=>`<div class="alarm">${a}</div>`).join('');
  } else {
    alarmsTd.textContent = '';
  }
  tsTd.textContent = now;
}

socket.on('connect', ()=>{ statusDiv.textContent = 'Connected'; });
socket.on('disconnect', ()=>{ statusDiv.textContent = 'Disconnected'; });

socket.on('initial', (state)=>{
  Object.entries(state).forEach(([port, v]) => {
    upsertRow(port, v.raw, v);
  });
});

socket.on('vent-data', ({port, raw, result})=>{
  upsertRow(port, raw, { values: result.values || result.values, result });
});
