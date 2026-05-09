// ═══════════════════════════════════════════════════════════════
//  SentinelAI — App Logic, Data Generation, Interactivity
// ═══════════════════════════════════════════════════════════════

// ─── CONSTANTS ───
const DEPTS = ['Engineering','Finance','HR','Marketing','Sales','IT Security','Legal','Executive','R&D','Operations'];
const TRIGGERS = ['After-hours login spike','Bulk file download','USB exfiltration','Email to external domain','Privilege escalation','Unusual VPN origin','Mass file deletion','Unauthorized DB query','Repeated auth failure','Sensitive dir access'];
const NAMES_FIRST = ['Alex','Jordan','Morgan','Casey','Riley','Drew','Taylor','Cameron','Avery','Quinn','Blake','Dakota','Reese','Skyler','Phoenix','Jamie','Rowan','Sage','Harper','Ellis'];
const NAMES_LAST = ['Chen','Rodriguez','Patel','Kim','Okafor','Müller','Santos','Nakamura','Anderson','Volkov','Singh','Dubois','Tanaka','Ali','Martinez','Johansson','Park','Ivanov','Garcia','Nguyen'];
const COLORS = { cyan: '#4fc3f7', red: '#ef5350', amber: '#ffa726', green: '#26c44b', purple: '#ab47bc', muted: '#4a5568', border: '#1a2940', surface: '#0d1624', bg: '#0a0e17', text: '#e0e6ed', textSec: '#7a8ba3' };
const DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

// ─── DATA GENERATION ───
function rand(min, max) { return Math.random() * (max - min) + min; }
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function genId() { return 'USR-' + String(Math.floor(rand(1000, 9999))); }
function genTimestamp() {
  const d = new Date();
  d.setHours(d.getHours() - Math.floor(rand(0, 72)));
  return d.toISOString().replace('T',' ').slice(0, 19);
}

function riskFromScore(s) {
  if (s >= 0.8) return 'critical';
  if (s >= 0.6) return 'high';
  if (s >= 0.35) return 'medium';
  return 'low';
}
function riskColor(r) {
  return { critical: COLORS.red, high: COLORS.amber, medium: COLORS.purple, low: COLORS.green }[r];
}

function generateUsers(n) {
  const users = [];
  for (let i = 0; i < n; i++) {
    const anomaly = Math.round(rand(0.05, 0.99) * 100) / 100;
    const isRedTeam = Math.random() < 0.12;
    const boosted = isRedTeam ? Math.min(1, anomaly + rand(0.15, 0.35)) : anomaly;
    const score = Math.round(boosted * 100) / 100;
    const risk = riskFromScore(score);
    const ifScore = Math.round(rand(0.1, 1) * 100) / 100;
    const svmScore = Math.round(rand(0.1, 1) * 100) / 100;
    const aeScore = Math.round(rand(0.1, 1) * 100) / 100;
    users.push({
      id: genId(),
      name: pick(NAMES_FIRST) + ' ' + pick(NAMES_LAST),
      dept: pick(DEPTS),
      risk,
      score,
      redTeam: isRedTeam,
      trigger: pick(TRIGGERS),
      lastEvent: genTimestamp(),
      ifScore, svmScore, aeScore,
      behavioral: {
        'Login Frequency': Math.floor(rand(1, 40)),
        'Avg Session Len': Math.floor(rand(5, 480)) + ' min',
        'After-Hours %': Math.floor(rand(0, 60)) + '%',
        'Failed Logins': Math.floor(rand(0, 15)),
        'Unique IPs': Math.floor(rand(1, 12)),
      },
      frequency: {
        'File Access / Day': Math.floor(rand(2, 200)),
        'Email Sent / Day': Math.floor(rand(1, 80)),
        'USB Events / Week': Math.floor(rand(0, 20)),
        'DB Queries / Day': Math.floor(rand(0, 150)),
        'Downloads / Day': Math.floor(rand(0, 50)),
      },
      shap: [
        { name: 'login_freq', val: rand(0, 1) },
        { name: 'file_access', val: rand(0, 1) },
        { name: 'after_hours', val: rand(0, 1) },
        { name: 'usb_events', val: rand(0, 1) },
        { name: 'email_external', val: rand(0, 1) },
        { name: 'failed_auth', val: rand(0, 1) },
      ].sort((a, b) => b.val - a.val),
      activity: DAYS.map(() => Math.floor(rand(0, 100))),
    });
  }
  return users.sort((a, b) => b.score - a.score);
}

const DATA = generateUsers(247);
let selectedUser = null;

// ─── TAB SWITCHING ───
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab === 'graph') initGraph();
  });
});

function switchToTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.remove('active');
    if (b.dataset.tab === tabId) b.classList.add('active');
  });
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
}

// ─── TAB 1: ANOMALY TABLE ───
function renderMetrics() {
  const critical = DATA.filter(u => u.risk === 'critical').length;
  const avg = (DATA.reduce((s, u) => s + u.score, 0) / DATA.length).toFixed(2);
  const redTeam = DATA.filter(u => u.redTeam).length;
  document.getElementById('mc-critical').textContent = critical;
  document.getElementById('mc-avg').textContent = avg;
  document.getElementById('mc-redteam').textContent = redTeam;
}

function scoreBarClass(score) {
  if (score >= 0.8) return 'red';
  if (score >= 0.6) return 'amber';
  if (score >= 0.35) return 'purple';
  return 'green';
}

function renderTable(users) {
  const tbody = document.getElementById('anomaly-tbody');
  tbody.innerHTML = users.map(u => `
    <tr data-uid="${u.id}" onclick="selectUser('${u.id}')">
      <td style="color:${COLORS.text};font-weight:500">${u.id}</td>
      <td>${u.dept}</td>
      <td><span class="badge badge-${u.risk}">${u.risk.toUpperCase()}</span></td>
      <td>
        <span class="score-bar"><span class="score-bar-fill ${scoreBarClass(u.score)}" style="width:${u.score * 100}%"></span></span>
        <span style="font-weight:500;color:${riskColor(u.risk)}">${u.score.toFixed(2)}</span>
      </td>
      <td><span class="${u.redTeam ? 'flag-yes' : 'flag-no'}">${u.redTeam ? '⚑ YES' : '—'}</span></td>
      <td style="color:${COLORS.textSec}">${u.trigger}</td>
      <td style="color:${COLORS.muted}">${u.lastEvent}</td>
    </tr>
  `).join('');
}

function filterAndRender() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const risk = document.getElementById('risk-filter').value;
  const flag = document.getElementById('flag-filter').value;
  let filtered = DATA;
  if (q) filtered = filtered.filter(u =>
    u.id.toLowerCase().includes(q) ||
    u.dept.toLowerCase().includes(q) ||
    u.trigger.toLowerCase().includes(q) ||
    u.name.toLowerCase().includes(q)
  );
  if (risk !== 'all') filtered = filtered.filter(u => u.risk === risk);
  if (flag === 'yes') filtered = filtered.filter(u => u.redTeam);
  if (flag === 'no') filtered = filtered.filter(u => !u.redTeam);
  renderTable(filtered);
}

document.getElementById('search-input').addEventListener('input', filterAndRender);
document.getElementById('risk-filter').addEventListener('change', filterAndRender);
document.getElementById('flag-filter').addEventListener('change', filterAndRender);

// ─── TAB 2: USER DETAIL ───
window.selectUser = function(uid) {
  const u = DATA.find(d => d.id === uid);
  if (!u) return;
  selectedUser = u;
  switchToTab('user-detail');
  document.getElementById('user-detail-placeholder').style.display = 'none';
  document.getElementById('user-detail-content').style.display = 'block';

  // Header
  const initials = u.name.split(' ').map(n => n[0]).join('');
  document.getElementById('user-header').innerHTML = `
    <div class="user-avatar">${initials}</div>
    <div class="user-meta">
      <h2>${u.name} <span class="badge badge-${u.risk}" style="vertical-align:middle;margin-left:10px">${u.risk.toUpperCase()}</span></h2>
      <p>${u.id} &middot; ${u.dept} &middot; Score: ${u.score.toFixed(2)}</p>
    </div>
  `;

  // Behavioral
  document.getElementById('behavioral-features').innerHTML =
    Object.entries(u.behavioral).map(([k, v]) => `
      <div class="feature-row"><span class="feature-name">${k}</span><span class="feature-val">${v}</span></div>
    `).join('');

  // Frequency
  document.getElementById('frequency-features').innerHTML =
    Object.entries(u.frequency).map(([k, v]) => `
      <div class="feature-row"><span class="feature-name">${k}</span><span class="feature-val">${v}</span></div>
    `).join('');

  // SHAP
  const maxShap = Math.max(...u.shap.map(s => s.val));
  document.getElementById('shap-features').innerHTML =
    u.shap.map(s => `
      <div class="feature-row">
        <span class="feature-name">${s.name}</span>
        <div class="shap-bar-wrap"><div class="shap-bar" style="width:${(s.val / maxShap) * 100}%"></div></div>
        <span class="feature-val">${s.val.toFixed(3)}</span>
      </div>
    `).join('');

  // Activity bars
  const maxAct = Math.max(...u.activity);
  document.getElementById('activity-bars').innerHTML =
    u.activity.map((v, i) => {
      const pct = maxAct > 0 ? (v / maxAct) * 100 : 0;
      let col = COLORS.muted;
      if (v > 70) col = COLORS.red;
      else if (v > 40) col = COLORS.amber;
      return `<div class="mini-bar">
        <div class="mini-bar-fill" style="height:${pct}%;background:${col}"></div>
        <span class="mini-bar-label">${DAYS[i]}</span>
      </div>`;
    }).join('');

  // Model scores
  const models = [
    { name: 'Isolation Forest', val: u.ifScore },
    { name: 'One-Class SVM', val: u.svmScore },
    { name: 'Autoencoder', val: u.aeScore },
  ];
  document.getElementById('model-scores').innerHTML =
    models.map(m => {
      const col = riskColor(riskFromScore(m.val));
      return `<div class="model-score-row">
        <span class="model-score-name">${m.name}</span>
        <div class="model-score-track"><div class="model-score-fill" style="width:${m.val * 100}%;background:${col}"></div></div>
        <span class="model-score-val" style="color:${col}">${m.val.toFixed(2)}</span>
      </div>`;
    }).join('');
};

// ─── TAB 3: FORCE-DIRECTED GRAPH ───
let graphInited = false;
let graphNodes = [];
let graphEdges = [];
let animId = null;

function initGraph() {
  if (graphInited) return;
  graphInited = true;

  const canvas = document.getElementById('graph-canvas');
  const ctx = canvas.getContext('2d');
  const container = canvas.parentElement;

  function resize() {
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  // Build nodes from top risk users
  const pool = DATA.filter(u => u.score >= 0.3).slice(0, 60);
  const highRisk = pool.filter(u => u.risk === 'critical' || u.risk === 'high').length;
  document.getElementById('mc-highrisk').textContent = highRisk;

  graphNodes = pool.map((u, i) => ({
    x: canvas.width / 2 + (Math.random() - 0.5) * 400,
    y: canvas.height / 2 + (Math.random() - 0.5) * 300,
    vx: 0, vy: 0,
    r: 4 + u.score * 10,
    color: riskColor(u.risk),
    label: u.id,
    risk: u.risk,
    score: u.score,
    uid: u.id,
  }));

  // Build edges
  graphEdges = [];
  let flaggedCount = 0;
  for (let i = 0; i < graphNodes.length; i++) {
    const conns = Math.floor(rand(1, 4));
    for (let c = 0; c < conns; c++) {
      const j = Math.floor(rand(0, graphNodes.length));
      if (j !== i) {
        const flagged = graphNodes[i].risk === 'critical' && graphNodes[j].risk !== 'low' && Math.random() < 0.4;
        if (flagged) flaggedCount++;
        graphEdges.push({ source: i, target: j, flagged });
      }
    }
  }
  document.getElementById('mc-connections').textContent = flaggedCount;
  document.getElementById('mc-clusters').textContent = Math.floor(rand(3, 8));

  // Physics
  function tick() {
    const W = canvas.width, H = canvas.height;
    // Repulsion
    for (let i = 0; i < graphNodes.length; i++) {
      for (let j = i + 1; j < graphNodes.length; j++) {
        let dx = graphNodes[j].x - graphNodes[i].x;
        let dy = graphNodes[j].y - graphNodes[i].y;
        let dist = Math.sqrt(dx * dx + dy * dy) || 1;
        let force = 800 / (dist * dist);
        graphNodes[i].vx -= (dx / dist) * force;
        graphNodes[i].vy -= (dy / dist) * force;
        graphNodes[j].vx += (dx / dist) * force;
        graphNodes[j].vy += (dy / dist) * force;
      }
    }
    // Attraction
    for (const e of graphEdges) {
      const a = graphNodes[e.source], b = graphNodes[e.target];
      let dx = b.x - a.x, dy = b.y - a.y;
      let dist = Math.sqrt(dx * dx + dy * dy) || 1;
      let force = (dist - 80) * 0.01;
      a.vx += (dx / dist) * force;
      a.vy += (dy / dist) * force;
      b.vx -= (dx / dist) * force;
      b.vy -= (dy / dist) * force;
    }
    // Center gravity
    for (const n of graphNodes) {
      n.vx += (W / 2 - n.x) * 0.001;
      n.vy += (H / 2 - n.y) * 0.001;
      n.vx *= 0.9; n.vy *= 0.9;
      n.x += n.vx; n.y += n.vy;
      n.x = Math.max(n.r, Math.min(W - n.r, n.x));
      n.y = Math.max(n.r, Math.min(H - n.r, n.y));
    }
  }

  // Hover detection
  let hoveredNode = null;
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    hoveredNode = null;
    for (const n of graphNodes) {
      const dx = mx - n.x, dy = my - n.y;
      if (dx * dx + dy * dy < (n.r + 4) * (n.r + 4)) {
        hoveredNode = n;
        canvas.style.cursor = 'pointer';
        break;
      }
    }
    if (!hoveredNode) canvas.style.cursor = 'default';
  });
  canvas.addEventListener('click', () => {
    if (hoveredNode) selectUser(hoveredNode.uid);
  });

  function draw() {
    tick();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Edges
    for (const e of graphEdges) {
      const a = graphNodes[e.source], b = graphNodes[e.target];
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = e.flagged ? 'rgba(239,83,80,0.35)' : 'rgba(74,85,104,0.2)';
      ctx.lineWidth = e.flagged ? 1.5 : 0.5;
      ctx.stroke();
    }

    // Nodes
    for (const n of graphNodes) {
      const isHovered = n === hoveredNode;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r + (isHovered ? 3 : 0), 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.globalAlpha = isHovered ? 1 : 0.85;
      ctx.fill();
      ctx.globalAlpha = 1;

      if (isHovered) {
        ctx.strokeStyle = n.color;
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.font = '11px IBM Plex Mono';
        ctx.fillStyle = COLORS.text;
        ctx.fillText(`${n.label}  ${n.score.toFixed(2)}`, n.x + n.r + 6, n.y + 4);
      }
    }
    animId = requestAnimationFrame(draw);
  }
  draw();
}

// ─── TAB 4: HOW IT WORKS ───
const SECTIONS = [
  {
    title: 'Data Ingestion',
    body: `The system ingests four categories of simulated enterprise logs:<br><br>
    <span class="code-tag">logins.csv</span> — user authentication events (login/logout, IP, timestamps)<br>
    <span class="code-tag">file_access.csv</span> — file read/write/delete operations by user<br>
    <span class="code-tag">usb_usage.csv</span> — removable media connect/disconnect events<br>
    <span class="code-tag">emails.csv</span> — email metadata including recipients and external domain flags<br><br>
    A red team simulation module (<span class="code-tag">simulate_red_team.py</span>) injects adversarial patterns to test detection robustness.`
  },
  {
    title: 'Feature Engineering',
    body: `Raw logs are transformed into per-user behavioral vectors via three pipelines:<br><br>
    <b>Behavioral Features</b> — login frequency, session duration, after-hours ratio, failed attempts<br>
    <b>Frequency Features</b> — file access rate, email volume, USB event rate, download velocity<br>
    <b>NLP Features</b> — email sentiment analysis using <span class="code-tag">TF-IDF</span> vectorization<br>
    <b>Graph Features</b> — degree centrality, betweenness, clustering coefficient from user interaction graphs<br><br>
    All features are merged into a single matrix via <span class="code-tag">merge_features.py</span> and normalized with <span class="code-tag">StandardScaler</span>.`
  },
  {
    title: 'Anomaly Detection Models',
    body: `Three unsupervised models run independently to produce anomaly scores:<br><br>
    <b>1. Isolation Forest</b><br>
    <span class="formula">score(x) = 2^(-E[h(x)] / c(n))</span>
    Isolates anomalies by random feature splits. Fewer splits to isolate ≈ higher anomaly score. Uses <span class="code-tag">contamination=0.1</span>, <span class="code-tag">n_estimators=100</span>.<br><br>
    <b>2. One-Class SVM</b><br>
    <span class="formula">min ½‖w‖² + (1/νn) Σ max(0, -(w·φ(xᵢ) - ρ))</span>
    Learns a decision boundary in kernel space (<span class="code-tag">RBF</span>). Points outside the boundary are anomalies. <span class="code-tag">nu=0.1</span>.<br><br>
    <b>3. Autoencoder</b><br>
    <span class="formula">L(x) = ‖x - D(E(x))‖²</span>
    Neural network trained to reconstruct normal behavior. High reconstruction error = anomalous. Architecture: <span class="code-tag">[n → 8 → 4 → 8 → n]</span>.<br><br>
    The final anomaly score is the <b>mean of all three normalized model outputs</b>.`
  },
  {
    title: 'Graph Analysis',
    body: `User interactions are modeled as a graph <span class="code-tag">G = (V, E)</span> where:<br><br>
    • Nodes <span class="code-tag">V</span> = users<br>
    • Edges <span class="code-tag">E</span> = shared file access, email exchanges, or co-login patterns<br><br>
    <b>Graph Features Extracted:</b><br>
    <span class="formula">Degree Centrality: C_D(v) = deg(v) / (n-1)</span>
    <span class="formula">Betweenness: C_B(v) = Σ σ_st(v) / σ_st</span>
    <span class="formula">Clustering Coeff: C_C(v) = 2T(v) / (deg(v)(deg(v)-1))</span>
    Visualized using <span class="code-tag">NetworkX</span> for analysis and <span class="code-tag">PyVis</span> for interactive HTML rendering.`
  },
  {
    title: 'SHAP Explainability',
    body: `Model predictions are explained using <span class="code-tag">SHAP</span> (SHapley Additive exPlanations):<br><br>
    <span class="formula">φᵢ = Σ_{S⊆N\\{i}} |S|!(|N|-|S|-1)!/|N|! × [f(S∪{i}) - f(S)]</span>
    Each feature's contribution is computed as its marginal impact across all possible feature coalitions. This provides:<br><br>
    • <b>Global importance</b> — which features drive model decisions overall<br>
    • <b>Local explanations</b> — why a specific user was flagged<br>
    • <b>Force plots</b> — per-user waterfall of feature contributions<br><br>
    For tree-based models, <span class="code-tag">TreeExplainer</span> provides exact Shapley values in polynomial time. <span class="code-tag">LIME</span> is used as a secondary explainer for models without native SHAP support.`
  },
];

function renderAccordions() {
  const container = document.getElementById('accordion-container');
  container.innerHTML = SECTIONS.map((s, i) => `
    <div class="accordion${i === 0 ? ' open' : ''}" id="acc-${i}">
      <div class="accordion-header" onclick="toggleAcc(${i})">
        <h3>${s.title}</h3>
        <span class="accordion-arrow">▼</span>
      </div>
      <div class="accordion-body">${s.body}</div>
    </div>
  `).join('');
}

window.toggleAcc = function(i) {
  document.getElementById('acc-' + i).classList.toggle('open');
};

// ─── INIT ───
renderMetrics();
renderTable(DATA);
renderAccordions();
document.getElementById('user-count').textContent = DATA.length;
