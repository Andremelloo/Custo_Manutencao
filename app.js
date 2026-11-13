/**
 * Dashboard de Gestão Estratégica de Custos de Manutenção :: TCP
 * Terminal de Contêineres de Paranaguá
 * 100% Standalone & Client-Side Execution
 */

// Global Chart Instances
let chartCurvaS = null;
let chartBalancoFamilias = null;
let chartPrePostWK22 = null;
let chartTopDespesasWK22 = null;
let chartImpactoPreco = null;
let chartFrotaSemanas = null;
let chartFrotaComponentes = null;
let chartResumoEvolucao = null;
let chartResumoRitmo = null;

// Table Pagination & Filter State
let currentPage = 1;
const pageSize = 50;
let filteredTransactions = [];
let sortColumn = 'd';
let sortDirection = 'asc';

// Active Fleet for Fleet Weekly Analysis Tab
let currentActiveFleet = 'RESUMO';
let currentFleetTableFilter = 'TODAS';

// ==================== ACCESS SECURITY AUTHENTICATION ====================
const DASHBOARD_PASSWORD = 'tcp@2026';
const AUTH_STORAGE_KEY = 'tcp_dashboard_auth_w44';

function checkAuth() {
  const isAuth = sessionStorage.getItem(AUTH_STORAGE_KEY) === 'true';
  const overlay = document.getElementById('login-overlay');
  const pwdInput = document.getElementById('login-password');
  const errBox = document.getElementById('login-error-msg');

  if (isAuth) {
    if (overlay) overlay.classList.add('hidden');
  } else {
    if (overlay) {
      overlay.classList.remove('hidden');
      if (errBox) errBox.style.display = 'none';
      if (pwdInput) {
        pwdInput.value = '';
        setTimeout(() => pwdInput.focus(), 150);
      }
    }
  }
}

function handleLogin(event) {
  if (event) event.preventDefault();
  const pwdInput = document.getElementById('login-password');
  const errBox = document.getElementById('login-error-msg');
  const overlay = document.getElementById('login-overlay');

  if (!pwdInput) return;

  const entered = pwdInput.value.trim();
  if (entered === DASHBOARD_PASSWORD) {
    sessionStorage.setItem(AUTH_STORAGE_KEY, 'true');
    if (errBox) errBox.style.display = 'none';
    if (overlay) overlay.classList.add('hidden');
  } else {
    if (errBox) {
      errBox.style.display = 'block';
    }
    pwdInput.value = '';
    pwdInput.focus();
  }
}

function handleLogout() {
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
  checkAuth();
}

function togglePasswordVisibility() {
  const pwdInput = document.getElementById('login-password');
  const toggleBtn = document.querySelector('.btn-toggle-pwd');
  if (!pwdInput) return;
  if (pwdInput.type === 'password') {
    pwdInput.type = 'text';
    if (toggleBtn) toggleBtn.textContent = '🔒';
  } else {
    pwdInput.type = 'password';
    if (toggleBtn) toggleBtn.textContent = '👁️';
  }
}

// Utility: Currency Formatter
function formatBRL(val) {
  if (val === null || val === undefined || isNaN(val)) return 'R$ 0,00';
  return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatNumber(val, decimals = 0) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return val.toLocaleString('pt-BR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

// ==================== THEME TOGGLE ====================
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('tcp_cost_theme', newTheme);

  const icon = document.getElementById('theme-icon');
  const text = document.getElementById('theme-text');
  if (icon && text) {
    icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    text.textContent = newTheme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
  }

  updateChartThemes();
}

function initTheme() {
  const savedTheme = localStorage.getItem('tcp_cost_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const icon = document.getElementById('theme-icon');
  const text = document.getElementById('theme-text');
  if (icon && text) {
    icon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    text.textContent = savedTheme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
  }
}

// ==================== TAB SWITCHING ====================
function switchTab(tabId) {
  const buttons = document.querySelectorAll('.tab-btn');
  buttons.forEach(btn => btn.classList.remove('active'));
  const targetBtn = document.getElementById(`tab-nav-${tabId}`);
  if (targetBtn) targetBtn.classList.add('active');

  const sections = document.querySelectorAll('.tab-section');
  sections.forEach(sec => sec.classList.remove('active'));
  const targetSec = document.getElementById(`tab-${tabId}`);
  if (targetSec) targetSec.classList.add('active');

  setTimeout(() => {
    if (tabId === 'visao-geral') {
      if (chartCurvaS) chartCurvaS.resize();
      if (chartBalancoFamilias) chartBalancoFamilias.resize();
    }
    if (tabId === 'frotas-analise') {
      if (chartFrotaSemanas) chartFrotaSemanas.resize();
      if (chartFrotaComponentes) chartFrotaComponentes.resize();
      if (chartResumoEvolucao) chartResumoEvolucao.resize();
      if (chartResumoRitmo) chartResumoRitmo.resize();
    }
    if (tabId === 'diagnostico-wk22') {
      if (chartPrePostWK22) chartPrePostWK22.resize();
      if (chartTopDespesasWK22) chartTopDespesasWK22.resize();
    }
    if (tabId === 'comparativo-anos' && chartImpactoPreco) chartImpactoPreco.resize();
  }, 100);
}

// ==================== SUB-TABS (COMPARATIVE ITEMS) ====================
function switchItemSubTab(subTabId) {
  document.getElementById('btn-subtab-inflacao').classList.toggle('active', subTabId === 'inflacao');
  document.getElementById('btn-subtab-novos').classList.toggle('active', subTabId === 'novos');
  document.getElementById('btn-subtab-descontinuados').classList.toggle('active', subTabId === 'descontinuados');

  document.getElementById('subtab-view-inflacao').style.display = subTabId === 'inflacao' ? 'block' : 'none';
  document.getElementById('subtab-view-novos').style.display = subTabId === 'novos' ? 'block' : 'none';
  document.getElementById('subtab-view-descontinuados').style.display = subTabId === 'descontinuados' ? 'block' : 'none';
}

// ==================== INITIALIZE GLOBAL CHARTS ====================
function initCharts() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;

  const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#475569';

  // 1. CHART CURVA S (WK 00 - WK 44)
  const ctxCurvaS = document.getElementById('chart-curva-s');
  if (ctxCurvaS) {
    const labels = data.curva_s.map(c => `WK ${c.week < 10 ? '0' + c.week : c.week}`);
    const forecastVals = data.curva_s.map(c => c.forecast);
    const realVals = data.curva_s.map(c => c.real);
    const pointColors = data.curva_s.map(c => c.week >= 22 ? '#ef4444' : '#10b981');
    const pointRadii = data.curva_s.map(c => c.week === 22 ? 8 : (c.week % 4 === 0 ? 5 : 3));

    chartCurvaS = new Chart(ctxCurvaS, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Orçamento Meta (Forecast)',
            data: forecastVals,
            borderColor: '#0284c7',
            backgroundColor: 'rgba(2, 132, 199, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.1,
            pointRadius: 4,
            pointBackgroundColor: '#0284c7'
          },
          {
            label: 'Custo Real Executado',
            data: realVals,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.15,
            pointRadius: pointRadii,
            pointBackgroundColor: pointColors,
            pointBorderColor: '#fff',
            pointBorderWidth: 1.5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: textColor, font: { family: 'Outfit', size: 12, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              label: context => `${context.dataset.label}: ${formatBRL(context.raw || 0)}`,
              afterBody: function(tooltipItems) {
                const idx = tooltipItems[0].dataIndex;
                const item = data.curva_s[idx];
                const bal = item.forecast - item.real;
                const balPct = item.forecast > 0 ? (bal / item.forecast * 100).toFixed(2) : 0;
                const sign = bal >= 0 ? '+' : '';
                const alertNote = item.week === 22 ? '\n🚨 PONTO DE INFLEXÃO (WK 22)' : '';
                return `\nBalanço: ${sign}${formatBRL(bal)} (${sign}${balPct}%)${alertNote}`;
              }
            }
          }
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor, font: { family: 'Inter', size: 11 } } },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              callback: value => 'R$ ' + (value / 1000000).toFixed(1) + 'M',
              font: { family: 'Inter', size: 11 }
            }
          }
        }
      }
    });
  }

  // 2. CHART BALANÇO POR FAMÍLIA (W44)
  const ctxBalanco = document.getElementById('chart-balanco-familias');
  if (ctxBalanco) {
    const sortedFamilias = [...data.familias].sort((a, b) => a.balance - b.balance);
    const labels = sortedFamilias.map(f => f.account);
    const balances = sortedFamilias.map(f => f.balance);
    const bgColors = balances.map(b => b < 0 ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)');

    chartBalancoFamilias = new Chart(ctxBalanco, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Balanço Orçamentário (R$)',
          data: balances,
          backgroundColor: bgColors,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: context => {
                const f = sortedFamilias[context.dataIndex];
                return `Desvio: ${formatBRL(f.balance)} (${f.balance_pct.toFixed(2)}%)`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, callback: val => 'R$ ' + (val / 1000000).toFixed(1) + 'M' }
          },
          y: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Outfit', weight: '600' } }
          }
        }
      }
    });
  }

  // 3. CHART PRÉ vs PÓS WK 22
  const ctxPrePost = document.getElementById('chart-pre-post-wk22');
  if (ctxPrePost) {
    const fams = data.wk22_comparativo;
    const labels = fams.map(f => f.family);
    const preVals = fams.map(f => f.pre_media_sem);
    const postVals = fams.map(f => f.post_media_sem);

    chartPrePostWK22 = new Chart(ctxPrePost, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Média Semanal Pré-WK22 (W01-W21)',
            data: preVals,
            backgroundColor: 'rgba(56, 189, 248, 0.75)',
            borderRadius: 6
          },
          {
            label: 'Média Semanal Pós-WK22 (W22-W44)',
            data: postVals,
            backgroundColor: 'rgba(239, 68, 68, 0.85)',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: textColor, font: { family: 'Outfit', size: 12, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              label: context => `${context.dataset.label}: ${formatBRL(context.raw)}`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor, font: { family: 'Outfit', weight: '600' } } },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k' }
          }
        }
      }
    });
  }

  // 4. CHART MAIORES DESPESAS WK 22+
  const ctxTopDespesas = document.getElementById('chart-top-despesas-wk22');
  if (ctxTopDespesas) {
    const topDespesas = [
      { nome: 'Descarte Ativos (Lote W35)', valor: 373217.48, fam: 'Asset Disposal' },
      { nome: 'Descarte Ativos (Lote W35-2)', valor: 225768.13, fam: 'Asset Disposal' },
      { nome: 'Certificação NR-12/29 (LRQA)', valor: 217335.00, fam: 'Others' },
      { nome: 'Bomba Injetora RTG#38', valor: 189566.59, fam: 'RTG' },
      { nome: 'Cabos de Aço Bridon STS', valor: 181382.40, fam: 'STS' },
      { nome: 'Inspeção STS/SE-00 (Grams)', valor: 148000.00, fam: 'Others' },
      { nome: 'Esteiras Brevetti RTG#17', valor: 107082.85, fam: 'RTG' },
      { nome: 'Suporte do Garfo EV-01', valor: 95287.50, fam: 'EH' },
      { nome: 'Freio de Elevação SB28 STS', valor: 94765.98, fam: 'STS' },
      { nome: 'Usinagem Compressores Manutec', valor: 92980.00, fam: 'Others' }
    ];

    chartTopDespesasWK22 = new Chart(ctxTopDespesas, {
      type: 'bar',
      data: {
        labels: topDespesas.map(d => d.nome),
        datasets: [{
          label: 'Valor da Ocorrência (R$)',
          data: topDespesas.map(d => d.valor),
          backgroundColor: '#8b5cf6',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: context => `Custo: ${formatBRL(context.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k' }
          },
          y: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  }

  // 5. CHART IMPACTO DE PREÇO (INFLAÇÃO)
  const ctxImpactoPreco = document.getElementById('chart-impacto-preco');
  if (ctxImpactoPreco) {
    const top10 = data.itens_inflacao_top.slice(0, 10);
    const labels = top10.map(i => i.desc.length > 30 ? i.desc.substring(0, 28) + '...' : i.desc);
    const impactos = top10.map(i => i.impacto_preco);

    chartImpactoPreco = new Chart(ctxImpactoPreco, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Impacto Financeiro pelo Aumento de Preço (R$)',
          data: impactos,
          backgroundColor: 'rgba(239, 68, 68, 0.85)',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                const it = top10[context.dataIndex];
                return [
                  `Impacto Preço: ${formatBRL(it.impacto_preco)}`,
                  `Preço Médio 2025: ${formatBRL(it.preco_2025)}`,
                  `Preço Médio 2026: ${formatBRL(it.preco_2026)} (+${it.var_preco_pct.toFixed(1)}%)`,
                  `Qtd Consumida 2026: ${it.qtd_2026} unidades`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Outfit', size: 11, weight: '600' } }
          },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k' }
          }
        }
      }
    });
  }
}

// =========================================================================
// FLEET WEEK-BY-WEEK INTELLIGENCE (TT, STS, RS, EH, MHC, RTG) + RESUMO GERAL
// =========================================================================
function selectFleetView(fleetCode) {
  currentActiveFleet = fleetCode;

  // Update fleet pills
  const pills = document.querySelectorAll('.fleet-pill-btn');
  pills.forEach(p => p.classList.remove('active'));
  const activePill = document.getElementById(`pill-fleet-${fleetCode}`);
  if (activePill) activePill.classList.add('active');

  const resumoView = document.getElementById('fleet-resumo-view');
  const singleView = document.getElementById('fleet-single-view');

  // Handle "RESUMO" tab selection
  if (fleetCode === 'RESUMO') {
    if (resumoView) resumoView.style.display = 'block';
    if (singleView) singleView.style.display = 'none';
    renderFleetResumoView();
    return;
  }

  // Handle individual fleet selection (TT, RTG, STS, RS, EH, MHC)
  if (resumoView) resumoView.style.display = 'none';
  if (singleView) singleView.style.display = 'block';

  const data = window.DASHBOARD_DATA;
  if (!data || !data.frotas_analytics || !data.frotas_analytics[fleetCode]) return;

  const fleetData = data.frotas_analytics[fleetCode];
  const info = fleetData.info;

  // 1. Update Alert Box
  const alertIcon = document.getElementById('fleet-alert-icon');
  const alertTitle = document.getElementById('fleet-alert-title');
  const alertDesc = document.getElementById('fleet-alert-desc');
  if (alertIcon) alertIcon.textContent = info.icone;
  if (alertTitle) alertTitle.textContent = `Raio-X Semanal: ${info.nome} • W01 a W44`;
  if (alertDesc) alertDesc.textContent = info.alert;

  // 2. Render Dynamic KPI Grid
  renderFleetKPIs(fleetData);

  // 3. Render Fleet Charts
  renderFleetCharts(fleetData);

  // 4. Render Fleet Weekly Table
  renderFleetWeeklyTable('TODAS');

  // 5. Render Fleet Machine Ranking Table
  renderFleetMachinesTable(fleetData);
}

// =========================================================================
// RENDER RESUMO GERAL DAS FROTAS (W01 a W44)
// =========================================================================
function renderFleetResumoView() {
  const data = window.DASHBOARD_DATA;
  if (!data || !data.frotas_analytics) return;

  const frotasAnalytics = data.frotas_analytics;
  const fleetCodes = ['TT', 'RTG', 'STS', 'RS', 'EH', 'MHC'];

  const viloesDesc = {
    'TT': '967 pneus Michelin (R$ 1,69M), reformas tandem CH (R$ 1,24M), freios e motor TT#30.',
    'RTG': '132 freios de gantry (R$ 980k), esteiras Brevetti RTG#15/#17 (R$ 214k), geradores e bomba RTG#38.',
    'STS': 'Cabos Bridon STS#08/#07/#11 (R$ 725k), freios SB28 e cabo MT STS#09 esmagado.',
    'RS': '12 bombas hidráulicas (R$ 193k), 10 rodas/cubos Konecranes e reposições de óleo HVLP 68.',
    'EH': 'Suporte garfo da FL#01 (R$ 95k), pneus 14.00-24 e módulos de transmissão EH#04.',
    'MHC': 'Bomba hidráulica principal MHC#01 (R$ 231k) e bomba tandem MHC#02 (R$ 67k).'
  };

  // Calculations
  let totalRealizado = 0;
  let totalBudget = 0;
  let totalPreMedia = 0;
  let totalPostMedia = 0;

  fleetCodes.forEach(code => {
    const f = frotasAnalytics[code];
    if (f) {
      totalRealizado += f.info.accum_cost;
      totalBudget += f.info.budget;
      totalPreMedia += f.pre_media_sem;
      totalPostMedia += f.post_media_sem;
    }
  });

  const totalBalance = totalBudget - totalRealizado;
  const totalBalancePct = totalBudget > 0 ? (totalBalance / totalBudget) * 100 : 0;
  const totalAumentoPct = totalPreMedia > 0 ? ((totalPostMedia - totalPreMedia) / totalPreMedia) * 100 : 0;

  // 1. Render Resumo KPIs
  const kpiContainer = document.getElementById('fleet-resumo-kpis');
  if (kpiContainer) {
    kpiContainer.innerHTML = `
      <div class="glass-panel kpi-card negative">
        <div class="kpi-header">
          <span class="kpi-title">Realizado Total das 6 Frotas (W44)</span>
          <span class="kpi-icon">💰</span>
        </div>
        <div class="kpi-value" style="color: var(--accent-red);">${formatBRL(totalRealizado)}</div>
        <div class="kpi-sub">
          <span>Budget YTD: ${formatBRL(totalBudget)}</span> &bull; 
          <strong style="color: var(--accent-red);">Saldo: ${formatBRL(totalBalance)} (${totalBalancePct.toFixed(1)}%)</strong>
        </div>
      </div>

      <div class="glass-panel kpi-card negative">
        <div class="kpi-header">
          <span class="kpi-title">Salto de Queima Semanal (Pós-WK22)</span>
          <span class="kpi-icon">📈</span>
        </div>
        <div class="kpi-value" style="color: var(--accent-red);">+${totalAumentoPct.toFixed(1)}%</div>
        <div class="kpi-sub">
          <span>Pré-WK22: ${formatBRL(totalPreMedia)}/sem</span> &bull; 
          <strong style="color: var(--accent-red);">Pós-WK22: ${formatBRL(totalPostMedia)}/sem</strong>
        </div>
      </div>

      <div class="glass-panel kpi-card warning">
        <div class="kpi-header">
          <span class="kpi-title">Maior Ofensor Orçamentário (Nominal)</span>
          <span class="kpi-icon">🚛</span>
        </div>
        <div class="kpi-value" style="font-size: 22px; color: var(--accent-red);">TT (Terminal Tractors)</div>
        <div class="kpi-sub">
          <span>Estouro: -R$ 3,80 M (-54,5%)</span> &bull; 
          <strong style="color: var(--accent-red);">Aceleração: +125,9%</strong>
        </div>
      </div>

      <div class="glass-panel kpi-card warning">
        <div class="kpi-header">
          <span class="kpi-title">Maior Desvio Relativo (%)</span>
          <span class="kpi-icon">🏗️</span>
        </div>
        <div class="kpi-value" style="font-size: 22px; color: var(--accent-red);">MHC (-110,7%)</div>
        <div class="kpi-sub">
          <span>Realizado: 2,1x o orçado</span> &bull; 
          <strong style="color: var(--accent-red);">MHC#01 & #02 (Bombas)</strong>
        </div>
      </div>
    `;
  }

  // 2. Render Resumo Table
  const tbody = document.getElementById('tbody-resumo-frotas');
  if (tbody) {
    let rowsHtml = '';
    fleetCodes.forEach(code => {
      const f = frotasAnalytics[code];
      if (!f) return;
      const info = f.info;
      const vilao = viloesDesc[code] || info.alert;
      const isOver = info.balance < 0;
      const sign = isOver ? '' : '+';
      const isSpike = f.aumento_pct > 50;

      rowsHtml += `
        <tr style="cursor: pointer;" onclick="selectFleetView('${code}')">
          <td>
            <strong>${code}</strong>
            <span style="display: block; font-size: 11px; color: var(--text-muted);">${info.nome.replace(code, '').replace('()', '').trim()}</span>
          </td>
          <td class="text-center" style="font-size: 20px;">${info.icone}</td>
          <td class="text-right font-bold">${formatBRL(info.accum_cost)}</td>
          <td class="text-right" style="color: var(--text-muted);">${formatBRL(info.budget)}</td>
          <td class="text-right font-bold" style="color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'};">
            ${sign}${formatBRL(info.balance)}
          </td>
          <td class="text-center">
            <span class="kpi-badge" style="background: ${isOver ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)'}; color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'}; font-weight: 700;">
              ${sign}${info.balance_pct.toFixed(2)}%
            </span>
          </td>
          <td class="text-right">${formatBRL(f.pre_media_sem)}/sem</td>
          <td class="text-right font-bold" style="color: var(--accent-red);">${formatBRL(f.post_media_sem)}/sem</td>
          <td class="text-center">
            <span class="kpi-badge" style="background: ${isSpike ? 'rgba(239, 68, 68, 0.2)' : (f.aumento_pct < 0 ? 'rgba(34, 197, 94, 0.2)' : 'rgba(245, 158, 11, 0.2)')}; color: ${isSpike ? 'var(--accent-red)' : (f.aumento_pct < 0 ? 'var(--accent-green)' : 'var(--accent-yellow)')}; font-weight: 700;">
              ${f.aumento_pct > 0 ? '+' : ''}${f.aumento_pct.toFixed(1)}%
            </span>
          </td>
          <td style="font-size: 12px; color: var(--text-muted); max-width: 320px; line-height: 1.4;">
            ${vilao}
          </td>
          <td class="text-center" onclick="event.stopPropagation();">
            <button class="btn-table-action" onclick="selectFleetView('${code}')" title="Abrir análise detalhada de ${code}">
              🔍 Raio-X
            </button>
          </td>
        </tr>
      `;
    });

    // Total Row
    rowsHtml += `
      <tr style="background: rgba(56, 189, 248, 0.08); font-weight: 700; border-top: 2px solid var(--border-color);">
        <td><strong>TOTAL FROTAS</strong></td>
        <td class="text-center">🚢</td>
        <td class="text-right" style="color: var(--brand-cyan);">${formatBRL(totalRealizado)}</td>
        <td class="text-right">${formatBRL(totalBudget)}</td>
        <td class="text-right" style="color: var(--accent-red);">${formatBRL(totalBalance)}</td>
        <td class="text-center">
          <span class="kpi-badge" style="background: rgba(239, 68, 68, 0.25); color: var(--accent-red); font-weight: 800;">
            ${totalBalancePct.toFixed(2)}%
          </span>
        </td>
        <td class="text-right">${formatBRL(totalPreMedia)}/sem</td>
        <td class="text-right" style="color: var(--accent-red);">${formatBRL(totalPostMedia)}/sem</td>
        <td class="text-center">
          <span class="kpi-badge" style="background: rgba(239, 68, 68, 0.25); color: var(--accent-red); font-weight: 800;">
            +${totalAumentoPct.toFixed(1)}%
          </span>
        </td>
        <td style="font-size: 12px; color: var(--text-muted);">
          Concentração em RTG e TT (somam R$ 26,13M, representando 74,7% de todo o gasto das frotas).
        </td>
        <td class="text-center">-</td>
      </tr>
    `;

    tbody.innerHTML = rowsHtml;
  }

  // 3. Render Resumo Charts
  renderResumoCharts(frotasAnalytics, fleetCodes);

  // 4. Render Quick Cards
  const cardsGrid = document.getElementById('fleet-quick-cards-grid');
  if (cardsGrid) {
    let cardsHtml = '';
    fleetCodes.forEach(code => {
      const f = frotasAnalytics[code];
      if (!f) return;
      const info = f.info;
      const vilao = viloesDesc[code] || info.alert;
      const isOver = info.balance < 0;

      cardsHtml += `
        <div class="glass-panel family-card">
          <div>
            <div class="family-card-header">
              <div>
                <span style="font-size: 26px; margin-right: 8px;">${info.icone}</span>
                <span class="family-card-title">${code} - ${info.nome.split('(')[0].trim()}</span>
              </div>
              <span class="kpi-badge" style="background: ${isOver ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)'}; color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'}; font-weight: 700;">
                ${isOver ? '' : '+'}${info.balance_pct.toFixed(1)}%
              </span>
            </div>

            <div class="family-metrics-row">
              <div class="family-metric-item">
                <p>Realizado YTD (W44)</p>
                <p style="color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'};">${formatBRL(info.accum_cost)}</p>
              </div>
              <div class="family-metric-item">
                <p>Budget YTD</p>
                <p>${formatBRL(info.budget)}</p>
              </div>
              <div class="family-metric-item">
                <p>Ritmo Pré-WK22</p>
                <p>${formatBRL(f.pre_media_sem)}/sem</p>
              </div>
              <div class="family-metric-item">
                <p>Ritmo Pós-WK22</p>
                <p style="color: var(--accent-red);">${formatBRL(f.post_media_sem)}/sem</p>
              </div>
            </div>

            <div class="family-notes-text" style="margin-bottom: 14px;">
              <strong>Ofensores:</strong> ${vilao}
            </div>
          </div>

          <button class="btn-action" style="width: 100%; justify-content: center;" onclick="selectFleetView('${code}')">
            🔍 Abrir Análise Detalhada de ${code} &rarr;
          </button>
        </div>
      `;
    });
    cardsGrid.innerHTML = cardsHtml;
  }
}

// =========================================================================
// RENDER RESUMO CHARTS (MULTILINE EVOLUTION & SIDE-BY-SIDE BURN RATE)
// =========================================================================
function renderResumoCharts(frotasAnalytics, fleetCodes) {
  const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#475569';

  const fleetColors = {
    'RTG': '#f59e0b',
    'TT': '#0284c7',
    'STS': '#6366f1',
    'RS': '#10b981',
    'EH': '#a855f7',
    'MHC': '#ec4899'
  };

  const weeks = Array.from({ length: 44 }, (_, i) => i + 1);
  const labels = weeks.map(w => `W${w < 10 ? '0' + w : w}`);

  // Chart 1: Evolution of all fleets
  const ctxEvolucao = document.getElementById('chart-resumo-evolucao');
  if (ctxEvolucao) {
    if (chartResumoEvolucao) chartResumoEvolucao.destroy();

    const datasets = fleetCodes.map(code => {
      const f = frotasAnalytics[code];
      const dataPoints = weeks.map(w => {
        const found = f ? f.semanas.find(s => s.week === w) : null;
        return found ? found.total : 0;
      });

      return {
        label: `${f.info.icone} ${code}`,
        data: dataPoints,
        borderColor: fleetColors[code] || '#38bdf8',
        backgroundColor: fleetColors[code] || '#38bdf8',
        borderWidth: (code === 'RTG' || code === 'TT') ? 3 : 2,
        pointRadius: 2,
        pointHoverRadius: 5,
        tension: 0.25,
        fill: false
      };
    });

    chartResumoEvolucao = new Chart(ctxEvolucao, {
      type: 'line',
      data: {
        labels: labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: textColor,
              font: { family: 'Outfit', size: 12, weight: '600' },
              usePointStyle: true,
              padding: 16
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${formatBRL(context.parsed.y)}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Inter', size: 10 } }
          },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k'
            }
          }
        }
      }
    });
  }

  // Chart 2: Burn rate pre vs post WK22 side by side
  const ctxRitmo = document.getElementById('chart-resumo-ritmo');
  if (ctxRitmo) {
    if (chartResumoRitmo) chartResumoRitmo.destroy();

    const fleetLabels = fleetCodes.map(c => `${frotasAnalytics[c].info.icone} ${c}`);
    const preRates = fleetCodes.map(c => frotasAnalytics[c].pre_media_sem);
    const postRates = fleetCodes.map(c => frotasAnalytics[c].post_media_sem);

    chartResumoRitmo = new Chart(ctxRitmo, {
      type: 'bar',
      data: {
        labels: fleetLabels,
        datasets: [
          {
            label: 'Ritmo Médio Pré-WK22 (W01-W21)',
            data: preRates,
            backgroundColor: 'rgba(56, 189, 248, 0.85)',
            borderColor: '#38bdf8',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Ritmo Médio Pós-WK22 (W22-W44)',
            data: postRates,
            backgroundColor: 'rgba(239, 68, 68, 0.85)',
            borderColor: '#ef4444',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: textColor,
              font: { family: 'Outfit', size: 12, weight: '600' },
              padding: 16
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ${formatBRL(context.parsed.y)}/semana`;
              },
              afterBody: function(contexts) {
                const idx = contexts[0].dataIndex;
                const code = fleetCodes[idx];
                const f = frotasAnalytics[code];
                return [
                  `Salto de queima: ${f.aumento_pct > 0 ? '+' : ''}${f.aumento_pct.toFixed(1)}%`,
                  `Realizado W44: ${formatBRL(f.info.accum_cost)}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor, font: { family: 'Outfit', size: 12, weight: '600' } }
          },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k/sem'
            }
          }
        }
      }
    });
  }
}

function renderFleetKPIs(fleetData) {
  const container = document.getElementById('fleet-kpi-grid');
  if (!container) return;

  const info = fleetData.info;
  const isOver = info.balance < 0;
  const sign = isOver ? '' : '+';
  const topCats = fleetData.categorias_comparativo.slice(0, 3);

  let cardsHtml = `
    <div class="glass-panel kpi-card ${isOver ? 'negative' : 'positive'}">
      <div class="kpi-header">
        <span class="kpi-title">Realizado YTD (W44)</span>
        <span class="kpi-icon">${info.icone}</span>
      </div>
      <div class="kpi-value" style="color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'}">${formatBRL(info.accum_cost)}</div>
      <div class="kpi-sub">
        <span>Budget: ${formatBRL(info.budget)}</span> &bull; 
        <strong style="color: ${isOver ? 'var(--accent-red)' : 'var(--accent-green)'}">Desvio: ${sign}${info.balance_pct.toFixed(1)}%</strong>
      </div>
    </div>

    <div class="glass-panel kpi-card negative">
      <div class="kpi-header">
        <span class="kpi-title">Ritmo Médio Semanal</span>
        <span class="kpi-icon">📈</span>
      </div>
      <div class="kpi-value" style="color: var(--accent-red);">${formatBRL(fleetData.post_media_sem)}/sem</div>
      <div class="kpi-sub">
        <span>Pré-WK22: ${formatBRL(fleetData.pre_media_sem)}/sem</span> &bull; 
        <strong style="color: var(--accent-red);">Salto: +${fleetData.aumento_pct.toFixed(1)}%</strong>
      </div>
    </div>
  `;

  // Top component cards
  topCats.forEach(c => {
    const isCatSpike = c.aumento_pct > 30;
    cardsHtml += `
      <div class="glass-panel kpi-card ${isCatSpike ? 'negative' : 'warning'}">
        <div class="kpi-header">
          <span class="kpi-title">${c.categoria.substring(0, 24)}</span>
          <span class="kpi-icon">⚙️</span>
        </div>
        <div class="kpi-value" style="font-size: 22px;">${formatBRL(c.total)}</div>
        <div class="kpi-sub">
          <span>Pré: ${formatBRL(c.pre_total)}</span> &bull; 
          <strong style="color: ${isCatSpike ? 'var(--accent-red)' : 'var(--accent-green)'}">Pós: ${formatBRL(c.post_total)} (+${c.aumento_pct.toFixed(0)}%)</strong>
        </div>
      </div>
    `;
  });

  container.innerHTML = cardsHtml;
}

function renderFleetCharts(fleetData) {
  const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#475569';

  const semanas = fleetData.semanas;
  const labels = semanas.map(s => `W${s.week < 10 ? '0' + s.week : s.week}`);
  const totals = semanas.map(s => s.total);
  const barColors = semanas.map(s => s.week < 22 ? 'rgba(56, 189, 248, 0.85)' : 'rgba(239, 68, 68, 0.85)');

  // 1. Chart Frota Semanas
  const ctxSemanas = document.getElementById('chart-frota-semanas');
  if (ctxSemanas) {
    if (chartFrotaSemanas) chartFrotaSemanas.destroy();

    chartFrotaSemanas = new Chart(ctxSemanas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            type: 'bar',
            label: `Gasto Semanal ${fleetData.info.nome} (R$)`,
            data: totals,
            backgroundColor: barColors,
            borderRadius: 4
          },
          {
            type: 'line',
            label: `Média Semanal Pré-WK22 (${formatBRL(fleetData.pre_media_sem)})`,
            data: semanas.map(s => s.week < 22 ? fleetData.pre_media_sem : null),
            borderColor: '#38bdf8',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          },
          {
            type: 'line',
            label: `Média Semanal Pós-WK22 (${formatBRL(fleetData.post_media_sem)})`,
            data: semanas.map(s => s.week >= 22 ? fleetData.post_media_sem : null),
            borderColor: '#ef4444',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: textColor, font: { family: 'Outfit', size: 12, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                if (context.dataset.type === 'line') return `${context.dataset.label}`;
                const idx = context.dataIndex;
                const s = semanas[idx];
                const res = [`Total ${currentActiveFleet}: ${formatBRL(s.total)}`];
                for (const [cat, val] of Object.entries(s.categorias)) {
                  if (val > 0) res.push(`${cat}: ${formatBRL(val)}`);
                }
                if (s.top_item) {
                  res.push(`Maior Item: ${s.top_mach} - ${s.top_item.substring(0, 45)} (${formatBRL(s.top_val)})`);
                }
                return res;
              }
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor, font: { family: 'Inter', size: 10 } } },
          y: {
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k'
            }
          }
        }
      }
    });
  }

  // 2. Chart Frota Componentes (Stacked Bar)
  const ctxComp = document.getElementById('chart-frota-componentes-semana');
  if (ctxComp) {
    if (chartFrotaComponentes) chartFrotaComponentes.destroy();

    // Distinct category names for this fleet
    const categoryNames = fleetData.categorias_comparativo.map(c => c.categoria);
    const palette = ['#ef4444', '#f59e0b', '#10b981', '#0284c7', '#8b5cf6', '#ec4899', '#64748b', '#14b8a6'];

    const datasets = categoryNames.map((catName, idx) => ({
      label: catName,
      data: semanas.map(s => s.categorias[catName] || 0),
      backgroundColor: palette[idx % palette.length],
      stack: 'frota'
    }));

    chartFrotaComponentes = new Chart(ctxComp, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: textColor, font: { family: 'Outfit', size: 11, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              label: context => `${context.dataset.label}: ${formatBRL(context.raw)}`
            }
          }
        },
        scales: {
          x: { stacked: true, grid: { display: false }, ticks: { color: textColor, font: { family: 'Inter', size: 10 } } },
          y: {
            stacked: true,
            grid: { color: gridColor },
            ticks: { color: textColor, callback: v => 'R$ ' + (v / 1000).toFixed(0) + 'k' }
          }
        }
      }
    });
  }
}

function renderFleetWeeklyTable(filterType = 'TODAS') {
  currentFleetTableFilter = filterType;
  document.getElementById('btn-fleet-filter-all').classList.toggle('active', filterType === 'TODAS');
  document.getElementById('btn-fleet-filter-pre').classList.toggle('active', filterType === 'PRE');
  document.getElementById('btn-fleet-filter-pos').classList.toggle('active', filterType === 'POS');

  const data = window.DASHBOARD_DATA;
  if (!data || !data.frotas_analytics || !data.frotas_analytics[currentActiveFleet]) return;

  const fleetData = data.frotas_analytics[currentActiveFleet];
  const thead = document.getElementById('thead-frota-semanal');
  const tbody = document.getElementById('tbody-frota-semanal');
  if (!thead || !tbody) return;

  // Get top 4 categories for columns
  const topCats = fleetData.categorias_comparativo.slice(0, 4).map(c => c.categoria);

  thead.innerHTML = `
    <tr>
      <th class="text-center">Semana</th>
      <th class="text-center">Período</th>
      <th class="text-right">Total Semana (R$)</th>
      ${topCats.map(c => `<th class="text-right">${c} (R$)</th>`).join('')}
      <th class="text-right">Outros (R$)</th>
      <th>Maior Evento / Máquina da Semana</th>
    </tr>
  `;

  const semanas = fleetData.semanas.filter(s => {
    if (filterType === 'PRE') return s.week < 22;
    if (filterType === 'POS') return s.week >= 22;
    return true;
  });

  tbody.innerHTML = semanas.map(s => {
    const isPos = s.week >= 22;
    const isPeak = s.total > (fleetData.post_media_sem * 1.5);
    const periodBadge = isPos
      ? '<span class="kpi-badge danger">Pós-WK22</span>'
      : '<span class="kpi-badge" style="background: rgba(56, 189, 248, 0.2); color: var(--brand-cyan);">Pré-WK22</span>';

    // Calculate sum of top 4 categories
    let topCatsSum = 0;
    const catColsHtml = topCats.map(c => {
      const v = s.categorias[c] || 0;
      topCatsSum += v;
      return `<td class="text-right font-semibold">${formatBRL(v)}</td>`;
    }).join('');

    const outrosVal = Math.max(0, s.total - topCatsSum);

    return `
      <tr style="${isPeak ? 'background: rgba(239, 68, 68, 0.06);' : ''}">
        <td class="text-center font-bold">W${s.week < 10 ? '0' + s.week : s.week}</td>
        <td class="text-center">${periodBadge}</td>
        <td class="text-right font-bold" style="color: ${isPeak ? 'var(--accent-red)' : 'var(--text-main)'}">
          ${formatBRL(s.total)}
        </td>
        ${catColsHtml}
        <td class="text-right" style="color: var(--text-dim);">${formatBRL(outrosVal)}</td>
        <td style="font-size: 12px; color: var(--text-muted); max-width: 340px;">
          ${s.top_item ? `<strong>${s.top_mach}:</strong> ${s.top_item.substring(0, 50)} (${formatBRL(s.top_val)})` : '-'}
        </td>
      </tr>
    `;
  }).join('');
}

function filterFleetTable(type) {
  renderFleetWeeklyTable(type);
}

function formatTopItemsList(items, isPost) {
  if (!items || !items.length) {
    return '<span style="color: var(--text-dim); font-size: 12px; font-style: italic;">Nenhum gasto relevante</span>';
  }

  const badgeColor = isPost ? 'var(--accent-red)' : 'var(--brand-cyan)';
  const icon = isPost ? '🔺' : '🔹';

  return `
    <div style="display: flex; flex-direction: column; gap: 6px;">
      ${items.map(it => `
        <div style="font-size: 12px; line-height: 1.35; display: flex; align-items: flex-start; gap: 6px;">
          <span style="font-size: 10px; margin-top: 2px;">${icon}</span>
          <div>
            <strong style="color: ${badgeColor}; font-weight: 700;">${it.qtd} un</strong>
            <span style="color: var(--text-main); font-weight: 500;"> • ${it.nome}</span>
            <span style="display: block; font-size: 11px; color: var(--text-muted); font-weight: 600;">
              Total: ${formatBRL(it.val)}
            </span>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderFleetMachinesTable(fleetData) {
  const tbody = document.getElementById('tbody-frota-maquinas');
  if (!tbody) return;

  if (!fleetData.maquinas_ranking || !fleetData.maquinas_ranking.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="padding: 24px; color: var(--text-muted);">Nenhum dado encontrado para esta frota.</td></tr>';
    return;
  }

  tbody.innerHTML = fleetData.maquinas_ranking.map((m, idx) => {
    const isTop3Mach = idx < 3;
    const isSpike = m.post_total > m.pre_total * 1.5 && m.post_total > 50000;

    return `
      <tr style="${isSpike ? 'background: rgba(239, 68, 68, 0.04);' : ''}">
        <td style="vertical-align: top;">
          <strong style="font-size: 14px; color: var(--text-main);">${m.maquina}</strong>
          ${isTop3Mach ? '<span class="kpi-badge" style="display: inline-block; margin-left: 6px; background: rgba(245, 158, 11, 0.2); color: var(--accent-yellow); font-size: 10px;">TOP GASTO</span>' : ''}
          ${isSpike ? '<span class="kpi-badge" style="display: inline-block; margin-top: 4px; background: rgba(239, 68, 68, 0.2); color: var(--accent-red); font-size: 10px;">SALTO PÓS-WK22</span>' : ''}
        </td>
        <td class="text-right" style="vertical-align: top; font-weight: 700; color: var(--brand-cyan);">
          ${formatBRL(m.pre_total)}
        </td>
        <td style="vertical-align: top; max-width: 320px; background: rgba(56, 189, 248, 0.02);">
          ${formatTopItemsList(m.top_pre, false)}
        </td>
        <td class="text-right" style="vertical-align: top; font-weight: 700; color: var(--accent-red);">
          ${formatBRL(m.post_total)}
        </td>
        <td style="vertical-align: top; max-width: 320px; background: rgba(239, 68, 68, 0.02);">
          ${formatTopItemsList(m.top_post, true)}
        </td>
        <td class="text-right font-bold" style="vertical-align: top; font-size: 14px; color: var(--text-main);">
          ${formatBRL(m.total)}
        </td>
      </tr>
    `;
  }).join('');
}

// Update Theme for all charts
function updateChartThemes() {
  const isDark = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
  const textColor = isDark ? '#94a3b8' : '#475569';

  [chartCurvaS, chartBalancoFamilias, chartPrePostWK22, chartTopDespesasWK22, chartImpactoPreco, chartFrotaSemanas, chartFrotaComponentes, chartResumoEvolucao, chartResumoRitmo].forEach(c => {
    if (c) {
      if (c.options.scales?.x) {
        if (c.options.scales.x.grid) c.options.scales.x.grid.color = gridColor;
        if (c.options.scales.x.ticks) c.options.scales.x.ticks.color = textColor;
      }
      if (c.options.scales?.y) {
        if (c.options.scales.y.grid) c.options.scales.y.grid.color = gridColor;
        if (c.options.scales.y.ticks) c.options.scales.y.ticks.color = textColor;
      }
      if (c.options.plugins?.legend?.labels) {
        c.options.plugins.legend.labels.color = textColor;
      }
      c.update();
    }
  });
}

// ==================== TAB 1: Tabela Oficial de Famílias W44 ====================
function renderTabelaFamilias() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;
  const tbody = document.getElementById('tbody-familias-geral');
  if (!tbody) return;

  let totalBudget = 0;
  let totalReal = 0;

  const rowsHtml = data.familias.map(f => {
    totalBudget += f.budget;
    totalReal += f.accum_cost;
    const isNegative = f.balance < 0;
    const badgeClass = isNegative ? 'status-overbudget' : 'status-underbudget';
    const statusText = isNegative ? '⚠️ Estouro' : '✅ No Orçamento';
    const sign = isNegative ? '' : '+';

    return `
      <tr>
        <td class="font-bold">${f.nome}</td>
        <td class="text-right font-semibold">${formatBRL(f.budget)}</td>
        <td class="text-right font-semibold">${formatBRL(f.accum_cost)}</td>
        <td class="text-right font-bold" style="color: ${isNegative ? 'var(--accent-red)' : 'var(--accent-green)'}">
          ${formatBRL(f.balance)}
        </td>
        <td class="text-center font-bold" style="color: ${isNegative ? 'var(--accent-red)' : 'var(--accent-green)'}">
          ${sign}${f.balance_pct.toFixed(2)}%
        </td>
        <td class="text-center"><span class="status-badge ${badgeClass}">${statusText}</span></td>
        <td style="font-size: 12px; color: var(--text-muted); max-width: 480px;">${f.notes || '-'}</td>
      </tr>
    `;
  }).join('');

  const totalBal = totalBudget - totalReal;
  const totalBalPct = (totalBal / totalBudget) * 100;

  const footerHtml = `
    <tr style="background: rgba(255, 255, 255, 0.05); border-top: 2px solid var(--border-color); font-weight: 800;">
      <td>TOTAL GERAL</td>
      <td class="text-right">${formatBRL(totalBudget)}</td>
      <td class="text-right">${formatBRL(totalReal)}</td>
      <td class="text-right" style="color: var(--accent-red);">${formatBRL(totalBal)}</td>
      <td class="text-center" style="color: var(--accent-red);">${totalBalPct.toFixed(2)}%</td>
      <td class="text-center"><span class="status-badge status-overbudget">🚨 -31,70%</span></td>
      <td>Posição oficial auditada na Semana 44 da Diretoria de Manutenção.</td>
    </tr>
  `;

  tbody.innerHTML = rowsHtml + footerHtml;
}

// ==================== TAB 3: Tabela Comparativa WK 22 ====================
function renderTabelaWK22() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;
  const tbody = document.getElementById('tbody-wk22-tabela');
  if (!tbody) return;

  tbody.innerHTML = data.wk22_comparativo.map(item => {
    const isSpike = item.aumento_pct > 30;
    const color = isSpike ? 'var(--accent-red)' : 'var(--accent-green)';
    const sign = item.aumento_pct > 0 ? '+' : '';
    let causa = 'Operação regular.';
    if (item.family === 'Asset Disposal') causa = 'Entrada maciça de baixas patrimoniais na W35 e W36.';
    if (item.family === 'TT') causa = 'Ciclo concentrado de pneus Michelin (967 un) e reformas de eixos tandem CH.';
    if (item.family === 'RTG') causa = '132 freios de translado, 13 geradores e bombas injetoras.';
    if (item.family === 'STS') causa = 'Troca de cabos de elevação Bridon nos STS#08, #07 e #11 e freios.';
    if (item.family === 'Others') causa = 'Contratos de inspeção NR-12/29 (LRQA) e compressores.';

    return `
      <tr>
        <td class="font-bold">${item.family}</td>
        <td class="text-right">${formatBRL(item.pre_total)}</td>
        <td class="text-right font-semibold">${formatBRL(item.pre_media_sem)}</td>
        <td class="text-right">${formatBRL(item.post_total)}</td>
        <td class="text-right font-semibold" style="color: ${color};">${formatBRL(item.post_media_sem)}</td>
        <td class="text-center font-bold" style="color: ${color};">${sign}${item.aumento_pct.toFixed(1)}%</td>
        <td style="font-size: 12px; color: var(--text-muted);">${causa}</td>
      </tr>
    `;
  }).join('');
}

// ==================== TAB 4: Tabelas de Itens (Inflação & Novos) ====================
function renderTabelasItens() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;

  // 1. Inflação
  const tbodyInf = document.getElementById('tbody-inflacao');
  if (tbodyInf) {
    tbodyInf.innerHTML = data.itens_inflacao_top.map(it => {
      const isHigher = it.var_preco_pct > 0;
      const color = isHigher ? 'var(--accent-red)' : 'var(--accent-green)';
      const sign = isHigher ? '+' : '';
      return `
        <tr>
          <td class="font-semibold" style="max-width: 320px;">${it.desc}</td>
          <td><span class="status-badge" style="background: rgba(56, 189, 248, 0.15); color: var(--brand-cyan);">${it.family}</span></td>
          <td class="text-right">${formatBRL(it.preco_2025)}</td>
          <td class="text-right font-bold">${formatBRL(it.preco_2026)}</td>
          <td class="text-center font-bold" style="color: ${color};">${sign}${it.var_preco_pct.toFixed(1)}%</td>
          <td class="text-right">${it.qtd_2025}</td>
          <td class="text-right font-semibold">${it.qtd_2026}</td>
          <td class="text-right font-bold" style="color: ${it.impacto_preco > 0 ? 'var(--accent-red)' : 'var(--accent-green)'}">
            ${formatBRL(it.impacto_preco)}
          </td>
          <td class="text-right font-semibold">${formatBRL(it.total_2026)}</td>
        </tr>
      `;
    }).join('');
  }

  // 2. Novos Itens 2026
  const tbodyNovos = document.getElementById('tbody-novos-itens');
  if (tbodyNovos) {
    tbodyNovos.innerHTML = data.novos_itens_top.map(it => `
      <tr>
        <td class="font-semibold" style="max-width: 360px;">${it.desc}</td>
        <td><span class="status-badge" style="background: rgba(56, 189, 248, 0.15); color: var(--brand-cyan);">${it.family}</span></td>
        <td style="color: var(--text-muted); font-size: 12px;">${it.sup || 'Estoque Geral / Requisição'}</td>
        <td class="text-right font-bold">${formatBRL(it.preco_medio)}</td>
        <td class="text-center font-semibold">${it.count}</td>
        <td class="text-right font-bold" style="color: var(--brand-cyan);">${formatBRL(it.total_val)}</td>
      </tr>
    `).join('');
  }

  // 3. Descontinuados
  const tbodyDesc = document.getElementById('tbody-descontinuados');
  if (tbodyDesc) {
    tbodyDesc.innerHTML = data.itens_apenas_2025_top.map(it => `
      <tr>
        <td class="font-semibold" style="max-width: 360px;">${it.desc}</td>
        <td><span class="status-badge" style="background: rgba(255, 255, 255, 0.08);">${it.family}</span></td>
        <td style="color: var(--text-muted); font-size: 12px;">${it.sup || 'Estoque Geral / Requisição'}</td>
        <td class="text-right font-bold">${formatBRL(it.preco_medio)}</td>
        <td class="text-center font-semibold">${it.count}</td>
        <td class="text-right font-semibold">${formatBRL(it.total_val)}</td>
      </tr>
    `).join('');
  }
}

// ==================== TAB 5: Deep Dive Cards por Frota ====================
function renderDeepDiveCards() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;
  const container = document.getElementById('container-frotas-cards');
  if (!container) return;

  container.innerHTML = data.familias.map(f => {
    const isNegative = f.balance < 0;
    const badgeClass = isNegative ? 'status-overbudget' : 'status-underbudget';
    const statusText = isNegative ? 'Estouro Orçamentário' : 'Economia / No Orçamento';
    const borderAccent = isNegative ? 'var(--accent-red)' : 'var(--accent-green)';
    const sign = isNegative ? '' : '+';

    return `
      <div class="glass-panel family-card" style="border-left: 4px solid ${borderAccent}; cursor: pointer;" onclick="switchToFleetDirect('${f.account}')">
        <div>
          <div class="family-card-header">
            <div>
              <div class="family-card-title">${f.nome}</div>
              <span class="status-badge ${badgeClass}" style="margin-top: 6px;">${statusText} (${sign}${f.balance_pct.toFixed(1)}%)</span>
            </div>
            <div style="font-size: 26px;">
              ${f.account === 'RTG' ? '🏗️' : f.account === 'TT' ? '🚛' : f.account === 'STS' ? '⚓' : f.account === 'RS' ? '🚜' : f.account === 'EH' ? '📦' : '⚙️'}
            </div>
          </div>

          <div class="family-metrics-row">
            <div class="family-metric-item">
              <p>Budget 2026</p>
              <p>${formatBRL(f.budget)}</p>
            </div>
            <div class="family-metric-item">
              <p>Realizado YTD</p>
              <p style="color: ${isNegative ? 'var(--accent-red)' : 'var(--accent-green)'}">${formatBRL(f.accum_cost)}</p>
            </div>
          </div>

          <div style="margin-bottom: 12px; display: flex; justify-content: space-between; font-size: 13px;">
            <span style="color: var(--text-muted); font-weight: 600;">Desvio Acumulado:</span>
            <span class="font-bold" style="color: ${isNegative ? 'var(--accent-red)' : 'var(--accent-green)'}">${formatBRL(f.balance)}</span>
          </div>
        </div>

        <div>
          <p style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: var(--text-dim); margin-bottom: 6px;">Ocorrências & Causas Técnicas:</p>
          <div class="family-notes-text">${f.notes || 'Operação conforme orçamento de manutenção preventiva.'}</div>
          <div style="margin-top: 10px; font-size: 11px; font-weight: 700; color: var(--brand-cyan); text-align: right;">Ver Análise Semanal W01-W44 &rarr;</div>
        </div>
      </div>
    `;
  }).join('');
}

function switchToFleetDirect(fleetCode) {
  if (['TT', 'STS', 'RS', 'EH', 'MHC', 'RTG'].includes(fleetCode)) {
    switchTab('frotas-analise');
    selectFleetView(fleetCode);
  }
}

// ==================== TAB 6: Master Transaction Table ====================
function initTransacoesTable() {
  const data = window.DASHBOARD_DATA;
  if (!data || !data.transacoes) return;

  filteredTransactions = [...data.transacoes];
  renderTransacoesPage();
}

function renderTransacoesPage() {
  const tbody = document.getElementById('tbody-transacoes-master');
  if (!tbody) return;

  const total = filteredTransactions.length;
  const totalPages = Math.ceil(total / pageSize) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, total);
  const pageData = filteredTransactions.slice(startIdx, endIdx);

  tbody.innerHTML = pageData.map(t => `
    <tr>
      <td class="font-semibold" style="white-space: nowrap;">${t.d}</td>
      <td class="text-center font-bold"><span class="kpi-badge ${t.w >= 22 ? 'danger' : ''}">W${t.w}</span></td>
      <td><span class="status-badge" style="background: rgba(56, 189, 248, 0.12); color: var(--brand-cyan);">${t.f}</span></td>
      <td class="font-semibold">${t.i || '-'}</td>
      <td style="max-width: 380px; font-size: 12px;">${t.m}</td>
      <td style="font-size: 12px; color: var(--text-muted); white-space: nowrap;">${t.s || '-'}</td>
      <td class="text-right font-bold">${formatBRL(t.v)}</td>
      <td style="font-size: 11px; color: var(--text-dim); max-width: 250px;">${t.h || '-'}</td>
    </tr>
  `).join('');

  const pInfo = document.getElementById('pagination-info');
  if (pInfo) {
    pInfo.textContent = `Mostrando ${startIdx + 1}-${endIdx} de ${formatNumber(total)} registros (Página ${currentPage} de ${totalPages})`;
  }

  const btnPrev = document.getElementById('btn-page-prev');
  const btnNext = document.getElementById('btn-page-next');
  if (btnPrev) btnPrev.disabled = currentPage <= 1;
  if (btnNext) btnNext.disabled = currentPage >= totalPages;
}

function prevPage() {
  if (currentPage > 1) {
    currentPage--;
    renderTransacoesPage();
  }
}

function nextPage() {
  currentPage++;
  renderTransacoesPage();
}

function handleTableSearch(term) {
  applyFilters();
}

function handleFamilyFilter(val) {
  applyFilters();
}

function handlePeriodFilter(val) {
  applyFilters();
}

function applyFilters() {
  const data = window.DASHBOARD_DATA;
  if (!data) return;

  const term = (document.getElementById('filtro-busca-tabela')?.value || '').toLowerCase().trim();
  const fam = document.getElementById('filtro-familia-select')?.value || 'TODAS';
  const period = document.getElementById('filtro-periodo-select')?.value || 'TODAS';

  filteredTransactions = data.transacoes.filter(t => {
    if (fam !== 'TODAS' && t.f !== fam) return false;
    if (period === 'PRE_WK22' && t.w > 21) return false;
    if (period === 'POS_WK22' && t.w < 22) return false;

    if (term) {
      const matchM = (t.m || '').toLowerCase().includes(term);
      const matchS = (t.s || '').toLowerCase().includes(term);
      const matchH = (t.h || '').toLowerCase().includes(term);
      const matchI = (t.i || '').toLowerCase().includes(term);
      if (!matchM && !matchS && !matchH && !matchI) return false;
    }

    return true;
  });

  currentPage = 1;
  renderTransacoesPage();
}

function sortTable(col) {
  if (sortColumn === col) {
    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn = col;
    sortDirection = 'asc';
  }

  filteredTransactions.sort((a, b) => {
    let valA = a[col];
    let valB = b[col];

    if (col === 'v' || col === 'w') {
      valA = Number(valA) || 0;
      valB = Number(valB) || 0;
    } else {
      valA = String(valA || '').toLowerCase();
      valB = String(valB || '').toLowerCase();
    }

    if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
    if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  renderTransacoesPage();
}

function exportToExcel() {
  if (!filteredTransactions || !filteredTransactions.length) {
    alert('Nenhum dado filtrado para exportar.');
    return;
  }

  const exportData = filteredTransactions.map(t => ({
    'Data': t.d,
    'Semana': t.w,
    'Frota': t.f,
    'Conta': t.a,
    'Item/Máquina': t.i,
    'Material/Serviço': t.m,
    'Fornecedor': t.s,
    'Valor (R$)': t.v,
    'Histórico': t.h
  }));

  const worksheet = XLSX.utils.json_to_sheet(exportData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Custos_Manutencao_TCP');
  XLSX.writeFile(workbook, `Custos_Manutencao_TCP_W44_${new Date().toISOString().slice(0, 10)}.xlsx`);
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  initTheme();
  initCharts();
  renderTabelaFamilias();
  selectFleetView('RESUMO'); // Start on RESUMO Geral
  renderTabelaWK22();
  renderTabelasItens();
  renderDeepDiveCards();
  initTransacoesTable();
});
