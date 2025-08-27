const form = document.getElementById('portfolio-form');
const errorBox = document.getElementById('error');
const results = document.getElementById('results');
const tableBody = document.querySelector('#table tbody');
const constraints = document.getElementById('constraints');
const riskProfile = document.getElementById('risk-profile');
const asOf = document.getElementById('as-of');
const themes = document.getElementById('themes');
const sources = document.getElementById('sources');
const rationales = document.getElementById('rationales');
let chart;

async function postJSON(url, body) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`${resp.status}: ${txt}`);
  }
  return resp.json();
}

function renderPie(canvasId, holdings) {
  const ctx = document.getElementById(canvasId);
  const labels = holdings.map(h => h.symbol);
  const data = holdings.map(h => Math.round(h.weight * 100));
  const colors = labels.map((_, i) => `hsl(${(i * 47) % 360}deg 80% 50%)`);
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors }]
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
  });
}

function renderTable(holdings) {
  tableBody.innerHTML = '';
  for (const h of holdings) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${h.symbol}</td><td>${h.kind}</td><td>${(h.weight * 100).toFixed(1)}%</td><td>${h.rationale || ''}</td>`;
    tableBody.appendChild(tr);
  }
}

function renderExplain(notes) {
  constraints.innerHTML = '';
  for (const c of notes.binding_constraints || []) {
    const span = document.createElement('span');
    span.className = 'badge';
    span.textContent = c;
    constraints.appendChild(span);
  }
  riskProfile.textContent = notes.risk_profile;
  asOf.textContent = new Date().toISOString().slice(0, 10);
  themes.textContent = (notes.themes_detected || []).map(t => `${t.theme} (${Math.round((t.confidence || 0) * 100)}%)`).join(', ');
  sources.textContent = (notes.data_sources || []).join(', ');
  rationales.innerHTML = '';
  for (const r of notes.rationale_summary || []) {
    const li = document.createElement('li');
    li.textContent = r;
    rationales.appendChild(li);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorBox.style.display = 'none';
  results.style.display = 'none';

  const text = document.getElementById('text').value.trim();
  const risk = document.querySelector('input[name="risk"]:checked').value;
  const amount = parseFloat(document.getElementById('amount').value);
  const base = document.getElementById('api-base').value.trim().replace(/\/$/, '');

  try {
    const data = await postJSON(`${base}/generate_portfolio`, { text, risk, amount });
    renderPie('pie', data.holdings || []);
    renderTable(data.holdings || []);
    renderExplain(data.notes || {});
    results.style.display = 'block';
  } catch (err) {
    errorBox.textContent = err.message || 'Request failed';
    errorBox.style.display = 'block';
  }
});
