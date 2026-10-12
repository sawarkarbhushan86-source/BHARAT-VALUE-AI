/**
 * Bharat Value AI - Single Page Application Core Controller
 */

const App = {
  currentSymbol: 'CDSL',
  currentHorizon: 'medium_term',
  currentChartPeriod: '3mo',
  currentStatementsPeriod: 'annual',
  currentStatementsView: 'consolidated',
  universe: [],

  async init() {
    this.bindEvents();
    await this.fetchMarketStatus();
    await this.fetchUniverse();
    await this.updateContextBar();
    this.navigate('market');
  },

  bindEvents() {
    // Navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const viewId = item.getAttribute('data-view');
        this.navigate(viewId);
      });
    });

    // Global Search
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const val = searchInput.value.trim().toUpperCase();
          if (val) {
            this.selectSymbol(val);
            searchInput.value = '';
            document.getElementById('search-dropdown').style.display = 'none';
          }
        }
      });
    }

    // DCF Sliders
    const dcfGrowth = document.getElementById('dcf-growth-slider');
    const dcfWacc = document.getElementById('dcf-wacc-slider');
    const dcfTerminal = document.getElementById('dcf-terminal-slider');

    if (dcfGrowth) dcfGrowth.addEventListener('input', () => this.updateCustomDCF());
    if (dcfWacc) dcfWacc.addEventListener('input', () => this.updateCustomDCF());
    if (dcfTerminal) dcfTerminal.addEventListener('input', () => this.updateCustomDCF());

    // NLP Custom Headline Form
    const nlpBtn = document.getElementById('btn-run-nlp');
    if (nlpBtn) {
      nlpBtn.addEventListener('click', () => this.runCustomNLP());
    }

    // RAG Chat Send Button
    const ragBtn = document.getElementById('btn-send-rag');
    const ragInput = document.getElementById('rag-query-input');
    if (ragBtn && ragInput) {
      ragBtn.addEventListener('click', () => this.sendRAGQuery());
      ragInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') this.sendRAGQuery();
      });
    }

    // Multi-Agent Run Button
    const agentBtn = document.getElementById('btn-run-agents');
    if (agentBtn) {
      agentBtn.addEventListener('click', () => this.runMultiAgentWorkflow());
    }

    // Backtest Run Button
    const btBtn = document.getElementById('btn-run-backtest');
    if (btBtn) {
      btBtn.addEventListener('click', () => this.runBacktestSimulation());
    }

    // Screener Run Button
    const screenBtn = document.getElementById('btn-run-screener');
    if (screenBtn) {
      screenBtn.addEventListener('click', () => this.loadScreener());
    }

    // Report Generation Buttons
    const btnPdf = document.getElementById('btn-download-pdf');
    const btnCsv = document.getElementById('btn-download-csv');
    if (btnPdf) btnPdf.addEventListener('click', () => this.downloadReport('pdf'));
    if (btnCsv) btnCsv.addEventListener('click', () => this.downloadReport('csv'));
  },

  navigate(viewId) {
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

    const targetView = document.getElementById(`view-${viewId}`);
    const targetNav = document.querySelector(`.nav-item[data-view="${viewId}"]`);

    if (targetView) targetView.classList.add('active');
    if (targetNav) targetNav.classList.add('active');

    // Trigger page-specific data loading
    switch(viewId) {
      case 'market': this.loadMarketOverview(); break;
      case 'screener': this.loadScreener(); break;
      case 'details': this.loadStockDetails(); break;
      case 'fundamentals': this.loadFundamentals(); break;
      case 'valuation': this.loadValuation(); break;
      case 'growth': this.loadQualityGrowth(); break;
      case 'news': this.loadNewsFeed(); break;
      case 'timeline': this.loadEventTimeline(); break;
      case 'nlp': this.loadNLPOverview(); break;
      case 'rag': this.loadRAGStats(); break;
      case 'agents': this.loadMultiAgentView(); break;
      case 'ml': this.loadMLResearch(); break;
      case 'backtest': this.loadBacktestView(); break;
      case 'risk': this.loadRiskFlags(); break;
      case 'reports': this.loadReportsView(); break;
      case 'health': this.loadHealthStatus(); break;
      case 'settings': this.loadSettings(); break;
    }
  },

  async fetchMarketStatus() {
    try {
      const res = await fetch('/api/market/status');
      const data = await res.json();
      const pill = document.getElementById('market-status-pill');
      if (pill) {
        const dot = data.is_open ? 'green' : 'yellow';
        pill.innerHTML = `<span class="status-dot ${dot}"></span> NSE ${data.is_open ? 'OPEN' : 'CLOSED'} (${data.reason})`;
      }
    } catch (e) {
      console.warn('Failed to fetch market status:', e);
    }
  },

  async fetchUniverse() {
    try {
      const res = await fetch('/api/universe');
      this.universe = await res.json();
    } catch (e) {
      console.error('Failed to load universe:', e);
    }
  },

  handleSearch(query) {
    const dropdown = document.getElementById('search-dropdown');
    if (!dropdown) return;

    if (!query || query.trim().length < 1) {
      dropdown.style.display = 'none';
      return;
    }

    const q = query.toLowerCase().trim();
    const matches = this.universe.filter(c => 
      c.symbol.toLowerCase().includes(q) || c.name.toLowerCase().includes(q)
    ).slice(0, 8);

    if (matches.length === 0) {
      dropdown.style.display = 'none';
      return;
    }

    dropdown.innerHTML = matches.map(c => `
      <div class="search-item" onclick="App.selectSymbol('${c.symbol}')" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid var(--border-light);">
        <b style="color: var(--primary);">${c.symbol}</b> — <span style="font-size: 12px; color: var(--text-secondary);">${c.name}</span>
      </div>
    `).join('');
    dropdown.style.display = 'block';
  },

  selectSymbol(symbol) {
    let clean = (symbol || '').trim();
    const aliasMap = {
      'hdfc': 'HDFCBANK',
      'hdfc bank': 'HDFCBANK',
      'hdfcbank': 'HDFCBANK',
      'icici': 'ICICIBANK',
      'icici bank': 'ICICIBANK',
      'icicibank': 'ICICIBANK',
      'reliance': 'RELIANCE',
      'ril': 'RELIANCE',
      'reliance industries': 'RELIANCE',
      'reliance industries limited': 'RELIANCE',
      'reliance industries ltd': 'RELIANCE',
      'tcs': 'TCS',
      'tata consultancy': 'TCS',
      'tata consultancy services': 'TCS',
      'l&t': 'LT',
      'larsen': 'LT',
      'larsen & toubro': 'LT',
      'larsen and toubro': 'LT',
      'sbi': 'SBIN',
      'state bank of india': 'SBIN',
      'infy': 'INFY',
      'infosys': 'INFY',
      'tata motors': 'TATAMOTORS',
      'bharti airtel': 'BHARTIARTL',
      'airtel': 'BHARTIARTL',
      'hul': 'HINDUNILVR',
      'hindustan unilever': 'HINDUNILVR',
      'itc': 'ITC',
      'kotak': 'KOTAKBANK',
      'kotak bank': 'KOTAKBANK',
      'kotak mahindra bank': 'KOTAKBANK',
      'axis': 'AXISBANK',
      'axis bank': 'AXISBANK',
      'bajaj finance': 'BAJFINANCE',
      'asian paints': 'ASIANPAINT',
      'maruti': 'MARUTI',
      'maruti suzuki': 'MARUTI',
      'sun pharma': 'SUNPHARMA',
      'titan': 'TITAN'
    };
    const low = clean.toLowerCase();
    if (aliasMap[low]) {
      clean = aliasMap[low];
    } else if (this.universe && this.universe.length > 0) {
      const match = this.universe.find(u => 
        (u.name && u.name.toLowerCase() === low) ||
        (u.symbol && u.symbol.toLowerCase() === low) ||
        (u.bse_code && u.bse_code === clean) ||
        (u.isin && u.isin.toLowerCase() === low)
      );
      if (match) {
        clean = match.symbol;
      }
    }
    this.currentSymbol = clean.toUpperCase().replace('.NS', '').replace('.BO', '').replace(/[^A-Z0-9_\-]/g, '');
    const dropdown = document.getElementById('search-dropdown');
    if (dropdown) dropdown.style.display = 'none';

    // Update UI headers
    document.querySelectorAll('.active-symbol-badge').forEach(el => {
      el.textContent = this.currentSymbol;
    });

    this.updateContextBar();
    this.navigate('details');
  },

  async updateContextBar() {
    const sym = this.currentSymbol;
    try {
      const res = await fetch(`/api/market/quote/${sym}`);
      const q = await res.json();
      const meta = this.universe.find(u => u.symbol === sym) || {};

      const symEl = document.getElementById('ctx-symbol');
      if (symEl) symEl.textContent = sym;
      const nameEl = document.getElementById('ctx-name');
      if (nameEl) nameEl.textContent = meta.name || sym;
      const exchEl = document.getElementById('ctx-exchange');
      if (exchEl) exchEl.textContent = q.exchange || 'NSE';
      const secEl = document.getElementById('ctx-sector');
      if (secEl) secEl.textContent = meta.sector || 'Equities';

      const hasPrice = q.price && q.price > 0 && q.status !== 'UNAVAILABLE';
      const priceEl = document.getElementById('ctx-price');
      if (priceEl) priceEl.textContent = hasPrice ? `₹${q.price.toFixed(2)}` : '--';
      const chgEl = document.getElementById('ctx-change');
      if (chgEl) {
        if (hasPrice) {
          const chg = q.change || 0;
          const pct = q.change_percent || 0;
          chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)`;
          chgEl.className = `context-change-val ${chg >= 0 ? 'positive' : 'negative'}`;
        } else {
          chgEl.textContent = '--';
          chgEl.className = 'context-change-val';
        }
      }
      const badge = document.getElementById('ctx-status-badge');
      if (badge) {
        const st = (q.status || 'UNAVAILABLE').toUpperCase();
        badge.textContent = st;
        badge.className = `status-badge status-badge-${st.toLowerCase().replace(/\s+/g, '-')}`;
      }
      const timeEl = document.getElementById('ctx-time');
      if (timeEl) timeEl.textContent = q.retrieval_ist || q.exchange_timestamp || 'N/A';
    } catch (e) {
      console.warn('Failed to update context bar:', e);
    }
  },

  setStatementsPeriod(periodType) {
    this.currentStatementsPeriod = periodType;
    document.querySelectorAll('#statements-period-bar .horizon-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-period-type') === periodType);
    });
    this.loadFinancialStatements();
  },

  setStatementsView(view) {
    this.currentStatementsView = view;
    document.querySelectorAll('#statements-view-bar .horizon-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view-type') === view);
    });
    this.loadFinancialStatements();
  },

  setResearchHorizon(horizon) {
    this.currentHorizon = horizon;
    document.querySelectorAll('.horizon-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-horizon') === horizon);
    });
    this.loadResearchSummary(this.currentSymbol, horizon);
  },

  toggleDrawer(drawerId) {
    const el = document.getElementById(drawerId);
    if (el) {
      el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
    }
  },

  // 1. Market Overview
  async loadMarketOverview() {
    try {
      const res = await fetch('/api/market/indices');
      const indices = await res.json();
      const container = document.getElementById('market-indices-grid');
      if (container && indices.length > 0) {
        container.innerHTML = indices.map(idx => `
          <div class="card">
            <div class="card-title">${idx.name} <span class="badge badge-primary">${idx.status}</span></div>
            <div class="metric-big">${idx.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
            <div class="metric-change ${idx.change >= 0 ? 'positive' : 'negative'}">
              ${idx.change >= 0 ? '+' : ''}${idx.change.toFixed(2)} (${idx.change_percent >= 0 ? '+' : ''}${idx.change_percent.toFixed(2)}%)
            </div>
          </div>
        `).join('');
      }

      // Load Market Movers
      const topGainers = [
        { symbol: "AMBER", price: 6450.0, chg: 1.73, name: "Amber Enterprises" },
        { symbol: "CDSL", price: 1265.0, chg: 1.20, name: "Central Depository Services" },
        { symbol: "BSOFT", price: 640.0, chg: 1.34, name: "Birlasoft Ltd" },
        { symbol: "RADICO", price: 2450.0, chg: 1.87, name: "Radico Khaitan" }
      ];
      const moversContainer = document.getElementById('market-movers-list');
      if (moversContainer) {
        moversContainer.innerHTML = topGainers.map(m => `
          <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-light); cursor: pointer;" onclick="App.selectSymbol('${m.symbol}')">
            <div><b>${m.symbol}</b> <span style="font-size: 11px; color: var(--text-muted);">${m.name}</span></div>
            <div style="text-align: right;"><b>₹${m.price.toFixed(2)}</b> <span class="positive" style="font-size: 11px; font-weight: 600;">+${m.chg}%</span></div>
          </div>
        `).join('');
      }
      // Load Universe Coverage Summary (Phase 1)
      try {
        const covRes = await fetch('/api/universe/coverage');
        const cov = await covRes.json();
        const verEl = document.getElementById('cov-version');
        if (verEl) verEl.textContent = `v${cov.security_master_version || '2.1'}`;
        const actEl = document.getElementById('cov-active');
        if (actEl) actEl.textContent = cov.total_eligible_active || 22;
        const excEl = document.getElementById('cov-excluded');
        if (excEl) excEl.textContent = cov.total_excluded || 2;
        const awtEl = document.getElementById('cov-awaiting');
        if (awtEl) awtEl.textContent = cov.total_awaiting_data || 0;
      } catch (ce) {
        console.warn('Failed to load universe coverage summary:', ce);
      }
    } catch (e) {
      console.error('Error loading market overview:', e);
    }
  },

  // 2. Stock Screener
  async loadScreener() {
    const minRoce = document.getElementById('filter-min-roce')?.value || 0;
    const maxPe = document.getElementById('filter-max-pe')?.value || 150;
    const maxDte = document.getElementById('filter-max-dte')?.value || 3;
    const minScore = document.getElementById('filter-min-score')?.value || 0;

    try {
      const res = await fetch(`/api/screener?min_roce=${minRoce}&max_pe=${maxPe}&max_debt_to_equity=${maxDte}&min_quality_score=${minScore}`);
      const data = await res.json();
      const tbody = document.getElementById('screener-table-body');
      if (tbody) {
        tbody.innerHTML = data.map(item => `
          <tr style="cursor: pointer;" onclick="App.selectSymbol('${item.symbol}')">
            <td><b>${item.symbol}</b><br/><span style="font-size: 11px; color: var(--text-muted);">${item.name}</span></td>
            <td>₹${item.price.toFixed(2)}</td>
            <td>${item.pe_ratio !== null && item.pe_ratio !== undefined ? (item.pe_ratio > 0 ? item.pe_ratio.toFixed(1) + 'x' : 'Loss-Making') : 'N/A'}</td>
            <td class="${(item.roce_pct || 0) >= 20 ? 'positive' : ''}"><b>${item.roce_pct ? item.roce_pct.toFixed(1) + '%' : 'N/A'}</b></td>
            <td>${item.roe_pct ? item.roe_pct.toFixed(1) + '%' : 'N/A'}</td>
            <td>${item.debt_to_equity !== null && item.debt_to_equity !== undefined ? item.debt_to_equity.toFixed(2) + 'x' : 'N/A'}</td>
            <td><span class="badge ${item.quality_score >= 70 ? 'badge-success' : 'badge-primary'}">${item.quality_score}</span></td>
            <td>${item.valuation_status !== 'INSUFFICIENT_DATA' && item.fair_value > 0 ? '₹' + item.fair_value.toFixed(2) : '--'}</td>
            <td><span class="badge ${item.valuation_status === 'UNDERVALUED' ? 'badge-success' : (item.valuation_status === 'OVERVALUED' ? 'badge-danger' : 'badge-warning')}">${item.valuation_status === 'INSUFFICIENT_DATA' ? 'INSUFFICIENT DATA' : ((item.margin_of_safety_pct > 0 ? '+' : '') + (item.margin_of_safety_pct || 0).toFixed(1) + '%')}</span></td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading screener:', e);
    }
  },

  // 3. Stock Details & Interactive Chart
  async loadStockDetails() {
    const sym = this.currentSymbol;
    const period = this.currentChartPeriod || '3mo';
    try {
      const [quoteRes, candleRes, fundRes] = await Promise.all([
        fetch(`/api/market/quote/${sym}`),
        fetch(`/api/market/candles/${sym}?period=${period}`),
        fetch(`/api/fundamentals/${sym}`)
      ]);

      const quote = await quoteRes.json();
      const candles = await candleRes.json();
      const fund = await fundRes.json();

      document.getElementById('details-symbol-title').textContent = `${sym} — ${quote.exchange || 'NSE'}`;

      // Update status badge
      const statusBadge = document.getElementById('details-status-badge');
      if (statusBadge) {
        const st = (quote.status || 'UNAVAILABLE').toUpperCase();
        statusBadge.textContent = st;
        statusBadge.className = `status-badge status-badge-${st.toLowerCase().replace(/\s+/g, '-')}`;
      }

      const timeEl = document.getElementById('details-status-time');
      if (timeEl) timeEl.textContent = quote.retrieval_ist || quote.exchange_timestamp || 'N/A';

      const srcEl = document.getElementById('details-status-source');
      if (srcEl) srcEl.textContent = quote.data_source || quote.provider || 'NSE Adapter';

      const noteEl = document.getElementById('details-status-note');
      if (noteEl) {
        if (quote.status === 'LIVE') {
          noteEl.textContent = 'Real-time quote active during market hours.';
        } else if (quote.status === 'DELAYED') {
          noteEl.textContent = '15-minute delayed market quote.';
        } else if (quote.status === 'LAST AVAILABLE' || quote.status === 'STALE') {
          noteEl.textContent = '"Latest available" is an archived verified quote, not real-time.';
        } else if (quote.status === 'DEMO') {
          noteEl.textContent = 'Demo sandbox mode quote.';
        } else {
          noteEl.textContent = quote.note || 'Market data currently unavailable from exchange provider.';
        }
      }

      const hasDPrice = quote.price && quote.price > 0 && quote.status !== 'UNAVAILABLE';
      document.getElementById('details-price').textContent = hasDPrice ? `₹${quote.price.toFixed(2)}` : '--';
      const chgEl = document.getElementById('details-change');
      if (hasDPrice) {
        const chg = quote.change || 0;
        const chgPct = quote.change_percent || 0;
        chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)} (${chgPct >= 0 ? '+' : ''}${chgPct.toFixed(2)}%)`;
        chgEl.className = chg >= 0 ? 'positive' : 'negative';
      } else {
        chgEl.textContent = '--';
        chgEl.className = '';
      }

      document.getElementById('details-volume').textContent = quote.volume ? quote.volume.toLocaleString('en-IN') : '--';
      document.getElementById('details-turnover').textContent = quote.turnover_cr ? `₹${quote.turnover_cr} Cr` : '--';
      document.getElementById('details-52w').textContent = (quote.week_52_low && quote.week_52_high) ? `₹${quote.week_52_low} - ₹${quote.week_52_high}` : '--';
      document.getElementById('details-pe').textContent = (fund.pe_ratio !== null && fund.pe_ratio !== undefined) ? (fund.pe_ratio > 0 ? `${fund.pe_ratio}x` : 'Loss-Making') : 'N/A';

      // Sync range buttons
      document.querySelectorAll('#chart-range-bar .horizon-pill-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-period') === period);
      });

      ChartRenderer.renderCandlestickChart('stock-candle-chart', candles, sym, period);

      // Load Beginner Research Summary
      await this.loadResearchSummary(sym, this.currentHorizon);
    } catch (e) {
      console.error('Error loading stock details:', e);
    }
  },

  async setChartPeriod(period) {
    this.currentChartPeriod = period;
    document.querySelectorAll('#chart-range-bar .horizon-pill-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-period') === period);
    });

    const badge = document.getElementById('chart-interval-badge');
    if (badge) {
      if (['1d'].includes(period)) badge.textContent = 'Intraday (5m)';
      else if (['1w', '5d'].includes(period)) badge.textContent = 'Intraday (15m)';
      else if (['1mo', '3mo', '6mo', '1y'].includes(period)) badge.textContent = 'Daily Candles (1D)';
      else if (['5y'].includes(period)) badge.textContent = 'Weekly Candles (1W)';
    }

    try {
      const res = await fetch(`/api/market/candles/${this.currentSymbol}?period=${period}`);
      const candles = await res.json();
      ChartRenderer.renderCandlestickChart('stock-candle-chart', candles, this.currentSymbol, period);
    } catch (e) {
      console.error('Error fetching candles for period:', period, e);
    }
  },


  async loadResearchSummary(symbol, horizon = 'medium_term') {
    try {
      const res = await fetch(`/api/research/summary/${symbol}?horizon=${horizon}`);
      const data = await res.json();

      // Assessment badge styling
      const badge = document.getElementById('summary-assessment-badge');
      if (badge) {
        badge.textContent = data.assessment_label || 'EVALUATING';
        let cls = 'assessment-badge-large ';
        const lbl = (data.assessment_label || '').toLowerCase();
        if (lbl.includes('attractive')) cls += 'assessment-attractive';
        else if (lbl.includes('worth')) cls += 'assessment-worth';
        else if (lbl.includes('fairly')) cls += 'assessment-fair';
        else if (lbl.includes('expensive')) cls += 'assessment-expensive';
        else if (lbl.includes('elevated') || lbl.includes('risk')) cls += 'assessment-risk';
        else cls += 'assessment-insufficient';
        badge.className = cls;
      }

      const horBadge = document.getElementById('summary-horizon-badge');
      if (horBadge) {
        const horMap = { 'short_term': '1–3 Months', 'medium_term': '1–3 Years', 'long_term': '3–5 Years' };
        horBadge.textContent = `Horizon: ${horMap[data.horizon] || data.horizon}`;
      }

      const modelBadge = document.getElementById('summary-model-type-badge');
      if (modelBadge) {
        modelBadge.textContent = `Model: ${data.valuation_assessment?.model_type || 'Audited Multiple'}`;
      }

      const hlEl = document.getElementById('summary-headline');
      if (hlEl) hlEl.textContent = data.headline || '';

      // Valuation & Thesis
      const cmp = data.valuation_assessment?.current_price;
      const cmpEl = document.getElementById('summary-cmp');
      if (cmpEl) cmpEl.textContent = (cmp && cmp > 0) ? `₹${cmp.toFixed(2)}` : '--';

      const fv = data.valuation_assessment?.fair_value;
      const fvEl = document.getElementById('summary-fair-val');
      const valStatus = data.valuation_assessment?.valuation_status;
      const isInsuff = valStatus === 'INSUFFICIENT_DATA';
      if (fvEl) fvEl.textContent = (!isInsuff && fv && fv > 0) ? `₹${fv.toFixed(2)}` : '--';

      const mosEl = document.getElementById('summary-mos');
      if (mosEl) {
        if (isInsuff || !fv || !cmp || cmp <= 0) {
          mosEl.textContent = 'INSUFFICIENT DATA';
          mosEl.style.color = '#f59e0b';
        } else {
          const mos = data.valuation_assessment?.margin_of_safety_pct || 0;
          mosEl.textContent = `${mos > 0 ? '+' : ''}${mos.toFixed(1)}% (${valStatus})`;
          mosEl.style.color = mos >= 0 ? '#34d399' : '#f43f5e';
        }
      }

      const rangeEl = document.getElementById('summary-val-range');
      if (rangeEl) {
        const lo = data.valuation_assessment?.conservative_bound;
        const hi = data.valuation_assessment?.aggressive_bound;
        rangeEl.textContent = (lo && hi) ? `₹${lo.toFixed(0)} – ₹${hi.toFixed(0)}` : 'Single Estimate';
      }

      // Evidence & Counterarguments
      const evList = document.getElementById('summary-evidence-list');
      if (evList && data.evidence_points) {
        evList.innerHTML = data.evidence_points.map(e => `<li>${e}</li>`).join('');
      }

      const caList = document.getElementById('summary-counterargs-list');
      if (caList && data.counterarguments) {
        caList.innerHTML = data.counterarguments.map(c => `<li>${c}</li>`).join('');
      }

      // Business Quality & Catalysts
      const qScore = document.getElementById('summary-quality-score');
      if (qScore) qScore.textContent = `${data.business_quality?.quality_score || 0}/100`;

      const cTier = document.getElementById('summary-compounding-tier');
      if (cTier) cTier.textContent = data.business_quality?.compounding_tier || 'Standard';

      const solvEl = document.getElementById('summary-solvency-status');
      if (solvEl) solvEl.textContent = data.business_quality?.solvency_status || 'Adequate';

      const gdList = document.getElementById('summary-growth-drivers');
      if (gdList && data.growth_drivers) {
        gdList.innerHTML = data.growth_drivers.map(g => `<li>${g}</li>`).join('');
      }

      const rkList = document.getElementById('summary-risks');
      if (rkList && data.material_risks) {
        rkList.innerHTML = data.material_risks.map(r => `<li>${r}</li>`).join('');
      }

      // Data Grounding & Limitations
      const dfEl = document.getElementById('summary-data-freshness');
      if (dfEl) dfEl.textContent = data.data_freshness_statement || 'Verified';

      const limList = document.getElementById('summary-limitations');
      if (limList && data.confidence_limitations) {
        limList.innerHTML = data.confidence_limitations.map(l => `<li>${l}</li>`).join('');
      }

      const tbList = document.getElementById('summary-thesis-breakers');
      if (tbList && data.thesis_breakers) {
        tbList.innerHTML = data.thesis_breakers.map(t => `<li>${t}</li>`).join('');
      }

      // Educational Drawers
      const drawContainer = document.getElementById('summary-educational-drawers');
      if (drawContainer && data.educational_drawers) {
        drawContainer.innerHTML = data.educational_drawers.map((item, idx) => `
          <div class="metric-drawer-card">
            <div class="metric-drawer-header" onclick="App.toggleDrawer('drawer-body-${idx}')">
              <div class="metric-drawer-title">
                <span>📖</span> <span>${item.metric}</span>
              </div>
              <div class="metric-drawer-val">${item.company_specific_value}</div>
            </div>
            <div id="drawer-body-${idx}" class="metric-drawer-body" style="display: none;">
              <p style="margin: 0 0 6px;"><b>What it means:</b> ${item.definition}</p>
              <p style="margin: 0 0 6px;"><b>Why it matters:</b> ${item.why_it_matters}</p>
              <p style="margin: 0; color: #94a3b8;"><b>Limitations:</b> ${item.limitations}</p>
            </div>
          </div>
        `).join('');
      }

    } catch (e) {
      console.error('Error loading research summary:', e);
    }
  },

  // 4. Fundamental Analysis & DuPont
  async loadFundamentals() {
    const sym = this.currentSymbol;
    try {
      const [fundRes, dupontRes] = await Promise.all([
        fetch(`/api/fundamentals/${sym}`),
        fetch(`/api/fundamentals/dupont/${sym}`)
      ]);

      const fund = await fundRes.json();
      const dupont = await dupontRes.json();

      document.getElementById('fund-rev').textContent = (fund.revenue !== null && fund.revenue !== undefined && fund.revenue > 0) ? `₹${fund.revenue.toLocaleString('en-IN')} Cr` : 'N/A (Unverified)';
      document.getElementById('fund-pat').textContent = (fund.net_profit !== null && fund.net_profit !== undefined) ? `₹${fund.net_profit.toLocaleString('en-IN')} Cr` : 'N/A (Unverified)';
      document.getElementById('fund-ebitda-margin').textContent = fund.operating_margin_pct !== null ? `${fund.operating_margin_pct}%` : 'N/A (Financial)';
      document.getElementById('fund-net-margin').textContent = fund.net_margin_pct !== null ? `${fund.net_margin_pct}%` : 'N/A';
      document.getElementById('fund-roe').textContent = fund.roe_pct !== null ? `${fund.roe_pct}%` : 'N/A';
      document.getElementById('fund-roce').textContent = fund.roce_pct !== null ? `${fund.roce_pct}%` : 'N/A';
      document.getElementById('fund-dte').textContent = fund.debt_to_equity !== null ? `${fund.debt_to_equity}x` : 'N/A (Deposit Liabilities)';
      document.getElementById('fund-ic').textContent = fund.interest_coverage !== null ? `${fund.interest_coverage}x` : 'N/A (Banking NII)';
      document.getElementById('fund-ocf').textContent = fund.operating_cash_flow !== null ? `₹${fund.operating_cash_flow} Cr` : 'N/A (Banking Operating)';
      document.getElementById('fund-fcf').textContent = fund.free_cash_flow !== null ? `₹${fund.free_cash_flow} Cr` : 'N/A (Banking Operating)';
      document.getElementById('fund-ccc').textContent = fund.cash_conversion_cycle !== null ? `${fund.cash_conversion_cycle} Days` : 'N/A (Banking Operating)';
      document.getElementById('fund-altman').textContent = fund.altman_z_score !== null ? fund.altman_z_score : 'N/A (Basel Prudential)';

      document.getElementById('dupont-roe').textContent = `${dupont.roe_pct}%`;
      document.getElementById('dupont-npm').textContent = `${dupont.net_profit_margin_pct}%`;
      document.getElementById('dupont-at').textContent = `${dupont.asset_turnover}x`;
      document.getElementById('dupont-em').textContent = `${dupont.equity_multiplier}x`;
      document.getElementById('dupont-interpretation').textContent = dupont.interpretation;

      // Load Multi-Period Financial Statements Table
      await this.loadFinancialStatements();
    } catch (e) {
      console.error('Error loading fundamentals:', e);
    }
  },

  async loadFinancialStatements() {
    const sym = this.currentSymbol;
    const periodType = this.currentStatementsPeriod || 'annual';
    const view = this.currentStatementsView || 'consolidated';

    try {
      const res = await fetch(`/api/fundamentals/${sym}/statements?period_type=${periodType}&view=${view}`);
      const data = await res.json();

      const viewBadge = document.getElementById('statements-view-badge');
      if (viewBadge) viewBadge.textContent = data.view ? data.view.toUpperCase() : 'CONSOLIDATED';

      const secBadge = document.getElementById('statements-sector-badge');
      if (secBadge) {
        secBadge.textContent = data.is_financial ? 'BFSI / Banking Format' : 'Industrial / Non-Financial';
      }

      const thead = document.getElementById('statements-table-head');
      const tbody = document.getElementById('statements-table-body');
      if (!thead || !tbody) return;

      const periods = data.periods || [];
      thead.innerHTML = `
        <tr>
          <th style="min-width: 220px; text-align: left;">Financial Line Item</th>
          ${periods.map(p => `<th style="text-align: right; min-width: 110px;">${p}</th>`).join('')}
          <th style="text-align: center; width: 90px;">Unit</th>
        </tr>
      `;

      const rows = data.rows || [];
      if (rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${periods.length + 2}" style="text-align: center; color: var(--text-muted); padding: 18px;">No reported statements data for selected filters.</td></tr>`;
        return;
      }

      tbody.innerHTML = rows.map(r => {
        const isHeaderOrKey = [
          'Net Profit (PAT)', 'Revenue from Operations', 'Net Interest Income (NII)',
          'Operating Profit (PPOP)', 'Free Cash Flow', 'Advances', 'Deposits'
        ].includes(r.item);
        const rowStyle = isHeaderOrKey ? 'font-weight: 700; color: var(--text-primary); background: rgba(56, 189, 248, 0.05);' : '';

        const cells = periods.map(p => {
          const val = r.values ? r.values[p] : null;
          let formatted = '--';
          if (val !== null && val !== undefined) {
            if (typeof val === 'number') {
              formatted = val.toLocaleString('en-IN', { maximumFractionDigits: 2 });
            } else {
              formatted = val;
            }
          }
          return `<td style="text-align: right; ${rowStyle}">${formatted}</td>`;
        }).join('');

        return `
          <tr style="${rowStyle}">
            <td style="text-align: left;"><b>${r.item}</b></td>
            ${cells}
            <td style="text-align: center; color: var(--text-muted); font-size: 11px;">${r.unit || '₹ Cr'}</td>
          </tr>
        `;
      }).join('');
    } catch (e) {
      console.error('Error loading financial statements table:', e);
    }
  },

  // 5. Fair Value & DCF Sensitivity
  async loadValuation() {
    const sym = this.currentSymbol;
    try {
      const res = await fetch(`/api/valuation/${sym}`);
      const val = await res.json();

      const isInsuffVal = val.valuation_status === 'INSUFFICIENT_DATA';
      document.getElementById('val-cmp').textContent = val.current_price > 0 ? `₹${val.current_price.toFixed(2)}` : '--';
      document.getElementById('val-composite').textContent = (!isInsuffVal && val.composite_fair_value > 0) ? `₹${val.composite_fair_value.toFixed(2)}` : '--';
      document.getElementById('val-dcf').textContent = (!isInsuffVal && val.dcf_fair_value > 0) ? `₹${val.dcf_fair_value.toFixed(2)}` : '--';
      document.getElementById('val-pe').textContent = (!isInsuffVal && val.pe_fair_value > 0) ? `₹${val.pe_fair_value.toFixed(2)}` : '--';
      document.getElementById('val-ev').textContent = (!isInsuffVal && val.ev_ebitda_fair_value > 0) ? `₹${val.ev_ebitda_fair_value.toFixed(2)}` : '--';

      const mosBadge = document.getElementById('val-mos-badge');
      if (isInsuffVal || !val.current_price || val.current_price <= 0) {
        mosBadge.textContent = 'INSUFFICIENT DATA';
        mosBadge.className = 'badge badge-warning';
      } else {
        mosBadge.textContent = `${val.margin_of_safety_pct > 0 ? '+' : ''}${val.margin_of_safety_pct.toFixed(1)}% (${val.valuation_status})`;
        mosBadge.className = `badge ${val.valuation_status === 'UNDERVALUED' ? 'badge-success' : (val.valuation_status === 'OVERVALUED' ? 'badge-danger' : 'badge-warning')}`;
      }

      document.getElementById('val-bear').textContent = (!isInsuffVal && val.bear_case_value > 0) ? `₹${val.bear_case_value.toFixed(2)}` : '--';
      document.getElementById('val-base').textContent = (!isInsuffVal && val.base_case_value > 0) ? `₹${val.base_case_value.toFixed(2)}` : '--';
      document.getElementById('val-bull').textContent = (!isInsuffVal && val.bull_case_value > 0) ? `₹${val.bull_case_value.toFixed(2)}` : '--';

      // Sync Sliders
      const g = val.assumptions.revenue_growth_rate ?? val.assumptions.revenue_growth ?? 0.15;
      const w = val.assumptions.discount_rate_wacc ?? val.assumptions.wacc ?? 0.12;
      const t = val.assumptions.terminal_growth_rate ?? val.assumptions.terminal_growth ?? 0.05;

      document.getElementById('dcf-growth-slider').value = g;
      document.getElementById('dcf-growth-val').textContent = `${(g * 100).toFixed(1)}%`;
      document.getElementById('dcf-wacc-slider').value = w;
      document.getElementById('dcf-wacc-val').textContent = `${(w * 100).toFixed(1)}%`;
      document.getElementById('dcf-terminal-slider').value = t;
      document.getElementById('dcf-terminal-val').textContent = `${(t * 100).toFixed(1)}%`;

      ChartRenderer.renderSensitivityHeatmap('dcf-sensitivity-chart', val.sensitivity_matrix, val.sensitivity_wacc_labels, val.sensitivity_growth_labels);

      // Populate Step-by-Step Waterfall
      const wfTitle = document.getElementById('waterfall-title');
      const wfModelBadge = document.getElementById('val-model-badge');
      const isBank = val.model_type === 'BANK_RESIDUAL_INCOME_PB';
      const container = document.getElementById('waterfall-steps-container');

      if (container) {
        if (isBank) {
          if (wfTitle) wfTitle.textContent = 'Banking Residual Income (RIM) & Justified P/B Waterfall';
          if (wfModelBadge) wfModelBadge.textContent = 'Banking RIM / Justified P/B';
          const bvps = val.assumptions.book_value_per_share || (val.current_price / 3.0);
          const rim = val.residual_income_fair_value || val.dcf_fair_value;
          const jpb = val.justified_pb_fair_value || val.ev_ebitda_fair_value;

          container.innerHTML = `
            <div class="waterfall-step-row">
              <span>1. Audited Book Value per Share (BVPS)</span>
              <b>₹${bvps.toFixed(2)}</b>
            </div>
            <div class="waterfall-step-row">
              <span>2. Present Value of 5-Year Explicit Residual Income (Excess ROE over Ke)</span>
              <b style="color: #38bdf8;">+₹${Math.max(0, (rim - bvps) * 0.4).toFixed(2)}</b>
            </div>
            <div class="waterfall-step-row">
              <span>3. Present Value of Terminal Residual Income (Gordon Growth RIM)</span>
              <b style="color: #34d399;">+₹${Math.max(0, (rim - bvps) * 0.6).toFixed(2)}</b>
            </div>
            <div class="waterfall-step-row" style="background: rgba(56, 189, 248, 0.05); padding: 8px 6px;">
              <span><b>= Residual Income Model Fair Value per Share</b></span>
              <b style="color: var(--primary);">₹${rim.toFixed(2)}</b>
            </div>
            <div class="waterfall-step-row">
              <span>4. Relative Justified Price-to-Book (P/B) Multiplier Target</span>
              <b>₹${jpb.toFixed(2)}</b>
            </div>
            <div class="waterfall-step-row" style="background: rgba(16, 185, 129, 0.05); padding: 8px 6px;">
              <span><b>= Composite Banking Fair Value per Share (40% RIM + 40% Justified PB + 20% PE)</b></span>
              <b style="color: #34d399;">₹${val.composite_fair_value.toFixed(2)}</b>
            </div>
          `;
        } else {
          if (wfTitle) wfTitle.textContent = 'Enterprise Value to Per-Share Equity Waterfall';
          if (wfModelBadge) wfModelBadge.textContent = 'Industrial FCF DCF';
          const pvFcf = val.assumptions.pv_explicit_fcf_cr || 0;
          const pvTv = val.assumptions.pv_terminal_value_cr || 0;
          const ev = val.assumptions.enterprise_value_cr || (pvFcf + pvTv);
          const netDebt = val.assumptions.net_debt_cr || 0;
          const eqVal = val.assumptions.equity_value_cr || (ev - netDebt);
          const shares = val.assumptions.shares_outstanding_cr || 1;
          const perShare = val.dcf_fair_value || 0;

          container.innerHTML = `
            <div class="waterfall-step-row">
              <span>1. Present Value of 5-Year Explicit Cash Flows (PV of FCF)</span>
              <b>₹${pvFcf.toLocaleString('en-IN', {maximumFractionDigits: 2})} Cr</b>
            </div>
            <div class="waterfall-step-row">
              <span>2. Present Value of Terminal Value (Gordon Growth Model)</span>
              <b>₹${pvTv.toLocaleString('en-IN', {maximumFractionDigits: 2})} Cr</b>
            </div>
            <div class="waterfall-step-row" style="background: rgba(56, 189, 248, 0.05); padding: 8px 6px;">
              <span><b>= Enterprise Value (EV)</b></span>
              <b style="color: var(--primary);">₹${ev.toLocaleString('en-IN', {maximumFractionDigits: 2})} Cr</b>
            </div>
            <div class="waterfall-step-row">
              <span>3. Less Net Debt (Total Debt minus Cash & Liquid Equivalents)</span>
              <b style="color: ${netDebt > 0 ? '#fb7185' : '#34d399'};">₹${netDebt.toLocaleString('en-IN', {maximumFractionDigits: 2})} Cr</b>
            </div>
            <div class="waterfall-step-row" style="background: rgba(16, 185, 129, 0.05); padding: 8px 6px;">
              <span><b>= Implied Total Equity Value</b></span>
              <b style="color: #34d399;">₹${eqVal.toLocaleString('en-IN', {maximumFractionDigits: 2})} Cr</b>
            </div>
            <div class="waterfall-step-row">
              <span>4. Divided by Diluted Shares Outstanding</span>
              <b>${shares} Cr shares</b>
            </div>
            <div class="waterfall-step-row" style="background: rgba(56, 189, 248, 0.08); padding: 8px 6px;">
              <span><b>= DCF Intrinsic Value per Share</b></span>
              <b style="color: var(--primary); font-size: 15px;">₹${perShare.toFixed(2)}</b>
            </div>
          `;
        }
      }

    } catch (e) {
      console.error('Error loading valuation:', e);
    }
  },

  async updateCustomDCF() {
    const sym = this.currentSymbol;
    const growth = parseFloat(document.getElementById('dcf-growth-slider').value);
    const wacc = parseFloat(document.getElementById('dcf-wacc-slider').value);
    const terminal = parseFloat(document.getElementById('dcf-terminal-slider').value);

    document.getElementById('dcf-growth-val').textContent = `${(growth * 100).toFixed(1)}%`;
    document.getElementById('dcf-wacc-val').textContent = `${(wacc * 100).toFixed(1)}%`;
    document.getElementById('dcf-terminal-val').textContent = `${(terminal * 100).toFixed(1)}%`;

    if (wacc <= terminal) {
      alert('Discount rate (WACC) must be strictly greater than terminal growth rate.');
      return;
    }

    try {
      const res = await fetch('/api/valuation/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: sym,
          forecast_years: 5,
          revenue_growth_rate: growth,
          discount_rate_wacc: wacc,
          terminal_growth_rate: terminal
        })
      });
      const val = await res.json();

      document.getElementById('val-composite').textContent = `₹${val.composite_fair_value.toFixed(2)}`;
      document.getElementById('val-dcf').textContent = `₹${val.dcf_fair_value.toFixed(2)}`;
      const mosBadge = document.getElementById('val-mos-badge');
      mosBadge.textContent = `${val.margin_of_safety_pct > 0 ? '+' : ''}${val.margin_of_safety_pct.toFixed(1)}% (${val.valuation_status})`;
      mosBadge.className = `badge ${val.valuation_status === 'UNDERVALUED' ? 'badge-success' : (val.valuation_status === 'OVERVALUED' ? 'badge-danger' : 'badge-warning')}`;

      ChartRenderer.renderSensitivityHeatmap('dcf-sensitivity-chart', val.sensitivity_matrix, val.sensitivity_wacc_labels, val.sensitivity_growth_labels);
    } catch (e) {
      console.error('Error updating custom DCF:', e);
    }
  },

  // 6. Business Quality & Compounding
  async loadQualityGrowth() {
    const sym = this.currentSymbol;
    try {
      const res = await fetch(`/api/growth/quality/${sym}`);
      const qual = await res.json();

      document.getElementById('qual-composite').textContent = `${qual.composite_score}/100`;
      document.getElementById('qual-tier').textContent = qual.multibagger_potential_tier;
      document.getElementById('qual-moat').textContent = `${qual.business_quality_score}/100`;
      document.getElementById('qual-fin').textContent = `${qual.financial_strength_score}/100`;
      document.getElementById('qual-growth').textContent = `${qual.growth_potential_score}/100`;
      document.getElementById('qual-val').textContent = `${qual.valuation_attractiveness_score}/100`;
      document.getElementById('qual-gov').textContent = `${qual.governance_score}/100`;

      const limitsList = document.getElementById('qual-limitations-list');
      if (limitsList && qual.limitations) {
        limitsList.innerHTML = qual.limitations.map(l => `<li>${l}</li>`).join('');
      }

      // Render 5 Institutional Pillar Cards (Phase 6)
      const container = document.getElementById('qual-pillars-container');
      if (container && qual.pillars) {
        container.innerHTML = qual.pillars.map(p => `
          <div class="pillar-card">
            <div class="pillar-header">
              <div class="pillar-title">
                ${p.pillar_name}
                <span style="font-size: 11px; color: var(--text-muted); font-weight: normal; margin-left: 6px;">(Weight: ${p.weight_pct}%)</span>
              </div>
              <span class="pillar-score-badge">${p.score}/100</span>
            </div>
            <p style="font-size: 12px; color: var(--text-primary); margin-bottom: 8px;"><b>Definition:</b> ${p.definition}</p>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 12px; border-radius: 4px; margin-bottom: 10px; font-size: 12px;">
              <div><b>Audited Evidence:</b> <span style="color: var(--primary); font-weight: 600;">${p.evidence}</span></div>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;"><b>Source Period:</b> ${p.source_period} • <b>Method:</b> ${p.calculation_method}</div>
              ${p.penalties_or_limitations ? `<div style="font-size: 11px; color: #fbbf24; margin-top: 3px;">⚠️ <b>Confidence & Penalties:</b> ${p.penalties_or_limitations}</div>` : ''}
            </div>
            <div class="grid-2" style="font-size: 11px; gap: 12px;">
              <div>
                <b style="color: #34d399;">Key Strengths:</b>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-secondary); line-height: 1.5;">
                  ${(p.main_strengths || []).map(s => `<li>${s}</li>`).join('')}
                </ul>
              </div>
              <div>
                <b style="color: #fb7185;">Counterarguments & Risks:</b>
                <ul style="padding-left: 16px; margin-top: 4px; color: var(--text-secondary); line-height: 1.5;">
                  ${(p.counterarguments || []).map(c => `<li>${c}</li>`).join('')}
                </ul>
              </div>
            </div>
          </div>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading quality growth:', e);
    }
  },

  // 7. News Feed
  async loadNewsFeed() {
    try {
      const res = await fetch('/api/news/latest?limit=25');
      const news = await res.json();
      const container = document.getElementById('news-feed-container');
      if (container) {
        container.innerHTML = news.map(item => `
          <div class="card" style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 8px;">
              <div>
                <span class="badge badge-primary">${item.publisher}</span>
                <span class="badge ${item.sentiment_label === 'POSITIVE' ? 'badge-success' : (item.sentiment_label === 'NEGATIVE' ? 'badge-danger' : 'badge-warning')}">${item.sentiment_label}</span>
                <span class="badge badge-purple">${item.event_category}</span>
                ${item.matching_symbols.map(s => `<span class="badge" style="background-color: rgba(56, 189, 248, 0.2); cursor: pointer;" onclick="App.selectSymbol('${s}')">${s}</span>`).join(' ')}
              </div>
              <span style="font-size: 11px; color: var(--text-muted);">${new Date(item.published_at).toLocaleString('en-IN')}</span>
            </div>
            <h4 style="font-size: 14px; margin-bottom: 6px;">
              <a href="${item.canonical_url}" target="_blank" style="color: var(--text-primary); text-decoration: none;">${item.title}</a>
            </h4>
            <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.5;">${item.summary || ''}</p>
            <div style="margin-top: 10px; font-size: 11px; color: var(--text-muted); display: flex; gap: 16px;">
              <span>Materiality: <b>${(item.materiality_score * 100).toFixed(0)}%</b></span>
              <span>Cluster: <code>${item.duplicate_cluster_id}</code></span>
            </div>
          </div>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading news feed:', e);
    }
  },

  // 8. Event Studies Timeline
  async loadEventTimeline() {
    try {
      const res = await fetch('/api/news/events');
      const events = await res.json();
      const container = document.getElementById('event-timeline-container');
      if (container) {
        container.innerHTML = events.map(ev => `
          <div class="card" style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
              <div>
                <b style="color: var(--primary); cursor: pointer;" onclick="App.selectSymbol('${ev.symbol}')">${ev.symbol}</b>
                <span class="badge badge-purple" style="margin-left: 8px;">${ev.event_category}</span>
                <span class="badge ${ev.reaction_window_status === 'COMPLETED' ? 'badge-success' : 'badge-warning'}" style="margin-left: 6px;">${ev.reaction_window_status || 'COMPLETED'}</span>
              </div>
              <span style="font-size: 11px; color: var(--text-muted);">
                Event: <b>${new Date(ev.event_date).toLocaleDateString('en-IN')}</b> • Disclosed: <b>${ev.publication_time ? new Date(ev.publication_time).toLocaleTimeString('en-IN', {hour: '2-digit', minute:'2-digit'}) : 'Market Hours'}</b>
              </span>
            </div>
            <p style="font-size: 13px; font-weight: 600; margin-bottom: 10px;">${ev.title}</p>
            <div class="grid-4" style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: var(--radius-sm); margin-bottom: 8px;">
              <div>
                <small style="color: var(--text-muted);">1-Day Excess Alpha</small><br/>
                <b class="${(ev.benchmark_adjusted_return_1d_pct != null ? ev.benchmark_adjusted_return_1d_pct : ev.abnormal_return_1d_pct) >= 0 ? 'positive' : 'negative'}">
                  ${(ev.benchmark_adjusted_return_1d_pct != null ? ev.benchmark_adjusted_return_1d_pct : ev.abnormal_return_1d_pct) >= 0 ? '+' : ''}${ev.benchmark_adjusted_return_1d_pct != null ? ev.benchmark_adjusted_return_1d_pct : ev.abnormal_return_1d_pct}%
                </b>
              </div>
              <div>
                <small style="color: var(--text-muted);">5-Day Reaction</small><br/>
                <b class="${(ev.benchmark_adjusted_return_5d_pct || ev.reaction_5d_pct || 0) >= 0 ? 'positive' : 'negative'}">
                  ${(ev.benchmark_adjusted_return_5d_pct || ev.reaction_5d_pct || 0) >= 0 ? '+' : ''}${ev.benchmark_adjusted_return_5d_pct || ev.reaction_5d_pct || 0.0}%
                </b>
              </div>
              <div>
                <small style="color: var(--text-muted);">20-Day Drift</small><br/>
                <b class="${(ev.reaction_20d_pct || 0) >= 0 ? 'positive' : 'negative'}">
                  ${(ev.reaction_20d_pct || 0) >= 0 ? '+' : ''}${ev.reaction_20d_pct || 0.0}%
                </b>
              </div>
              <div>
                <small style="color: var(--text-muted);">Volume / Sample</small><br/>
                <b>${ev.volume_shock_ratio || 1.0}x Avg</b> <span style="font-size: 10px; color: var(--text-muted);">(${ev.sample_size_days || 21}d)</span>
              </div>
            </div>
            <div style="font-size: 11px; color: var(--text-muted);">
              ${ev.causality_disclaimer || '⚠️ Observed historical association, not proof of sole causal impact.'}
            </div>
          </div>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading event timeline:', e);
    }
  },

  // 9. NLP Tester
  async runCustomNLP() {
    const input = document.getElementById('nlp-custom-input');
    const text = input ? input.value.trim() : '';
    if (!text) return;

    try {
      const res = await fetch('/api/nlp/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      const resultBox = document.getElementById('nlp-results-box');
      if (resultBox) {
        resultBox.style.display = 'block';
        document.getElementById('nlp-res-sentiment').textContent = `${data.sentiment.sentiment_label} (Score: ${data.sentiment.sentiment_score})`;
        document.getElementById('nlp-res-probabilities').textContent = `Pos: ${(data.sentiment.probabilities.positive*100).toFixed(1)}% | Neg: ${(data.sentiment.probabilities.negative*100).toFixed(1)}% | Neu: ${(data.sentiment.probabilities.neutral*100).toFixed(1)}%`;
        document.getElementById('nlp-res-event').textContent = `${data.event_classification.event_category} (${data.event_classification.description})`;
        document.getElementById('nlp-res-materiality').textContent = `${(data.materiality_score * 100).toFixed(0)}%`;
        document.getElementById('nlp-res-entities').textContent = JSON.stringify(data.entities, null, 2);
      }
    } catch (e) {
      console.error('Error running NLP:', e);
    }
  },

  async loadNLPOverview(force = false) {
    await this.loadNLPEvaluation(force);
  },

  async loadNLPEvaluation(force = false) {
    try {
      const res = await fetch('/api/nlp/evaluation');
      const data = await res.json();
      const accEl = document.getElementById('nlp-eval-acc');
      if (accEl) accEl.textContent = `${(data.sentiment_accuracy * 100).toFixed(1)}%`;
      const f1El = document.getElementById('nlp-eval-macro-f1');
      if (f1El) f1El.textContent = `${(data.macro_f1 * 100).toFixed(1)}%`;
      const calibEl = document.getElementById('nlp-eval-calib');
      if (calibEl) calibEl.textContent = `${data.brier_score.toFixed(3)} / ${data.expected_calibration_error.toFixed(3)}`;
      const liftEl = document.getElementById('nlp-eval-lift');
      if (liftEl) liftEl.textContent = `+${(data.lift_over_majority_baseline * 100).toFixed(1)}%`;
    } catch (e) {
      console.warn('Failed to load NLP evaluation:', e);
    }
  },

  downloadNLPEvalReport() {
    window.open('/api/nlp/evaluation/report', '_blank');
  },

  // 10. RAG Research Assistant
  async loadRAGStats() {
    try {
      const res = await fetch('/api/rag/stats');
      const stats = await res.json();
      document.getElementById('rag-chunks-indexed-badge').textContent = `${stats.indexed_chunks_count} Documents Indexed`;
    } catch (e) {}
  },

  async sendRAGQuery() {
    const input = document.getElementById('rag-query-input');
    const query = input ? input.value.trim() : '';
    if (!query) return;

    const messages = document.getElementById('rag-chat-messages');
    messages.innerHTML += `<div class="chat-message user"><b>You:</b> ${query}</div>`;
    input.value = '';

    messages.innerHTML += `<div class="chat-message assistant" id="rag-loading-msg"><i style="color: var(--text-muted);">Consulting indexed filings and regulatory disclosures...</i></div>`;
    messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, symbol: this.currentSymbol, top_k: 4 })
      });
      const data = await res.json();

      const loadingMsg = document.getElementById('rag-loading-msg');
      if (loadingMsg) loadingMsg.remove();

      let citationsHtml = '';
      if (data.citations && data.citations.length > 0) {
        citationsHtml = '<div style="margin-top: 10px; border-top: 1px solid var(--border-light); padding-top: 8px;"><b>Sources Cited:</b><br/>' +
          data.citations.map((c, i) => `
            <span class="citation-pill" onclick="App.showEvidenceModal('${encodeURIComponent(JSON.stringify(c))}')">
              📄 ${c.document_title} (${c.reporting_period || 'N/A'}) [Sim: ${(c.relevance_score*100).toFixed(0)}%]
            </span>
          `).join('') + '</div>';
      }

      messages.innerHTML += `
        <div class="chat-message assistant">
          <div style="margin-bottom: 6px;"><span class="badge badge-purple">${data.model_used}</span></div>
          <div>${data.answer.replace(/\n/g, '<br/>')}</div>
          ${citationsHtml}
        </div>
      `;
      messages.scrollTop = messages.scrollHeight;
    } catch (e) {
      console.error('Error querying RAG:', e);
      const loadingMsg = document.getElementById('rag-loading-msg');
      if (loadingMsg) loadingMsg.remove();
      messages.innerHTML += `<div class="chat-message assistant negative">Error connecting to financial research assistant.</div>`;
    }
  },

  showEvidenceModal(citationJsonStr) {
    const c = JSON.parse(decodeURIComponent(citationJsonStr));
    const modal = document.getElementById('evidence-modal');
    if (modal) {
      document.getElementById('evidence-modal-title').textContent = `${c.document_title} (${c.reporting_period || ''})`;
      document.getElementById('evidence-modal-body').innerHTML = `
        <p><b>Publication Date:</b> ${c.publication_date || 'N/A'}</p>
        <p><b>Section:</b> ${c.section_title || 'General'}</p>
        <p><b>Source Reference:</b> <a href="${c.source_url}" target="_blank" style="color: var(--primary);">${c.source_url || 'Audited Filing'}</a></p>
        <hr style="margin: 12px 0; border: 0; border-top: 1px solid var(--border-light);"/>
        <p style="font-size: 13px; line-height: 1.6; color: var(--text-primary); background: rgba(0,0,0,0.3); padding: 12px; border-radius: var(--radius-sm);">${c.snippet}</p>
      `;
      modal.classList.add('active');
    }
  },

  closeEvidenceModal() {
    const modal = document.getElementById('evidence-modal');
    if (modal) modal.classList.remove('active');
  },

  // 11. Multi-Agent Research Orchestrator
  async loadMultiAgentView() {
    // Initial view setup
  },

  async runMultiAgentWorkflow() {
    const sym = this.currentSymbol;
    const btn = document.getElementById('btn-run-agents');
    btn.disabled = true;
    btn.innerHTML = '⚡ Orchestrating 6 Agents...';

    try {
      const res = await fetch(`/api/agents/research/${sym}`);
      const data = await res.json();

      document.getElementById('agents-results-container').style.display = 'block';
      document.getElementById('agents-synthesis-text').innerHTML = data.synthesis_report.replace(/\n/g, '<br/>');

      const agentsGrid = document.getElementById('agents-cards-grid');
      agentsGrid.innerHTML = data.agents.map(a => `
        <div class="card">
          <div class="card-title">
            <span>${a.agent_name}</span>
            <span class="badge badge-success">OK</span>
          </div>
          <p style="font-size: 11px; color: var(--primary); margin-bottom: 8px;">${a.role}</p>
          <pre style="font-size: 11px; background: rgba(0,0,0,0.4); padding: 8px; border-radius: 4px; overflow-x: auto; color: #cbd5e1;">${JSON.stringify(a.findings, null, 2)}</pre>
        </div>
      `).join('');

      const auditList = document.getElementById('agents-audit-trail');
      auditList.innerHTML = data.audit_trail.map(line => `<li style="font-size: 11px; color: var(--text-muted); font-family: monospace;">${line}</li>`).join('');
    } catch (e) {
      console.error('Error running multi-agent:', e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '⚡ Run Multi-Agent Research';
    }
  },

  // 12. Quantitative ML Lab
  async loadMLResearch() {
    try {
      const res = await fetch('/api/ml/rank?horizon_days=60');
      const data = await res.json();

      const badgeEl = document.getElementById('ml-spearman-badge');
      if (badgeEl) {
        badgeEl.textContent = `Spearman Rho: +${data.spearman_rank_correlation}`;
      }
      const modelVerBadge = document.getElementById('ml-model-version-badge');
      if (modelVerBadge && data.model_version) {
        modelVerBadge.textContent = data.model_version;
      }

      const topTbody = document.getElementById('ml-top-ranked-body');
      if (topTbody) {
        topTbody.innerHTML = data.top_ranked.map((item, idx) => `
          <tr onclick="App.selectSymbol('${item.symbol}')" style="cursor: pointer;">
            <td>#${idx+1} <b>${item.symbol}</b></td>
            <td><b class="positive">${item.predicted_return_range || ('+' + item.predicted_excess_return_pct + '%')}</b></td>
            <td>${item.roce_pct}%</td>
            <td>${item.pe_ratio}x</td>
          </tr>
        `).join('');
      }

      ChartRenderer.renderFeatureImportanceChart('ml-feature-importance-chart', data.feature_importance);

      // Baseline Comparisons and Portfolio Simulation (Phase 6)
      if (data.top_k_performance) {
        const topRetEl = document.getElementById('ml-top-ann-ret');
        if (topRetEl) topRetEl.textContent = `+${data.top_k_performance.top_quintile_annualized_return_pct}%`;
      }
      if (data.baseline_comparison) {
        const rRho = document.getElementById('ml-ridge-rho');
        if (rRho) rRho.textContent = `Rho: +${data.baseline_comparison.ridge_linear_spearman_rho}`;
        const rLift = document.getElementById('ml-ridge-lift');
        if (rLift) rLift.textContent = `+${data.baseline_comparison.rank_correlation_lift_over_linear}`;
        const hRho = document.getElementById('ml-heuristic-rho');
        if (hRho) hRho.textContent = `Rho: +${data.baseline_comparison.heuristic_quality_spearman_rho}`;
      }
      if (data.coverage_diagnostics) {
        const diagEl = document.getElementById('ml-cov-diag');
        if (diagEl) {
          diagEl.innerHTML = `
            • <b>Universe Tested:</b> ${data.coverage_diagnostics.total_universe_tested} Stocks<br/>
            • <b>Rebalance Splits:</b> ${data.coverage_diagnostics.rebalance_periods_count} Quarters<br/>
            • <b>Leakage Guard:</b> ${data.coverage_diagnostics.coverage_verification_status}
          `;
        }
      }
    } catch (e) {
      console.error('Error loading ML research:', e);
    }
  },

  async retrainMLModel() {
    const btn = document.getElementById('btn-ml-retrain');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ Retraining...';
    }
    try {
      const res = await fetch('/api/ml/retrain', { method: 'POST' });
      const data = await res.json();
      alert(`Model Retraining ${data.status}: Version ${data.model_version}, Spearman Rho: +${data.spearman_rho}, Ranked Universe: ${data.top_stocks_count} securities.`);
      await this.loadMLResearch();
    } catch (e) {
      alert('Error triggering model retraining: ' + e);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '⚡ Retrain Model';
      }
    }
  },

  async rollbackMLModel() {
    if (!confirm('Roll back active model to the previous validated checkpoint?')) return;
    try {
      const res = await fetch('/api/ml/rollback', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        alert(`Model successfully rolled back to: ${data.current_active}`);
        await this.loadMLResearch();
      } else {
        alert('Rollback notice: ' + (data.message || data.status));
      }
    } catch (e) {
      alert('Error rolling back model: ' + e);
    }
  },

  // 13. Backtesting
  async loadBacktestView() {
    await this.runBacktestSimulation();
  },

  async runBacktestSimulation() {
    try {
      const res = await fetch('/api/ml/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_name: "Quality_Value_Momentum",
          start_date: "2021-01-01",
          end_date: "2024-06-01",
          include_costs: true,
          brokerage_pct: 0.0005,
          stt_pct: 0.001,
          slippage_pct: 0.0005
        })
      });
      const data = await res.json();

      const cagrEl = document.getElementById('bt-cagr');
      if (cagrEl) cagrEl.textContent = `+${data.cagr_pct}%`;
      const sharpeEl = document.getElementById('bt-sharpe');
      if (sharpeEl) sharpeEl.textContent = `${data.sharpe_ratio}x`;
      const sortinoEl = document.getElementById('bt-sortino');
      if (sortinoEl) sortinoEl.textContent = `${data.sortino_ratio}x`;
      const maxddEl = document.getElementById('bt-maxdd');
      if (maxddEl) maxddEl.textContent = `-${data.max_drawdown_pct}%`;
      const benchEl = document.getElementById('bt-bench-cagr');
      if (benchEl) benchEl.textContent = `+${((data.benchmark_return_pct / 3.5)).toFixed(1)}%`;
      const alphaEl = document.getElementById('bt-alpha');
      if (alphaEl) alphaEl.textContent = `+${data.alpha_pct}%`;

      ChartRenderer.renderBacktestEquityCurve('backtest-chart', data.equity_curve);
      setTimeout(() => {
        if (window.Plotly && document.getElementById('backtest-chart')) {
          Plotly.Plots.resize('backtest-chart');
        }
      }, 60);
    } catch (e) {
      console.error('Error running backtest:', e);
    }
  },

  // 14. Risk & Governance
  async loadRiskFlags() {
    const sym = this.currentSymbol;
    try {
      const [matrixRes, flagsRes] = await Promise.all([
        fetch(`/api/risk/matrix/${sym}`),
        fetch(`/api/risk/flags/${sym}`)
      ]);
      const matrix = await matrixRes.json();
      const flags = await flagsRes.json();

      // Summary Banner (Phase 7)
      const ratingEl = document.getElementById('risk-overall-rating');
      if (ratingEl) {
        ratingEl.textContent = matrix.overall_risk_rating;
        const colMap = {
          'LOW': 'badge-success',
          'MODERATE': 'badge-warning',
          'ELEVATED': 'badge-danger',
          'HIGH': 'badge-danger'
        };
        ratingEl.className = `badge ${colMap[matrix.overall_risk_rating] || 'badge-warning'}`;
      }

      const issuesEl = document.getElementById('risk-issues-count');
      if (issuesEl) issuesEl.textContent = matrix.issues_detected_count;

      const insuffEl = document.getElementById('risk-insufficient-count');
      if (insuffEl) insuffEl.textContent = matrix.insufficient_data_count;

      // 8 Dimensions Grid (Phase 7)
      const matrixContainer = document.getElementById('risk-matrix-container');
      if (matrixContainer && matrix.dimensions) {
        matrixContainer.innerHTML = matrix.dimensions.map(d => {
          let statusCls = 'status-no-issue';
          let badgeCls = 'risk-status-no-issue';
          let icon = '✓';

          if (d.status === 'Issue detected') {
            statusCls = 'status-issue';
            badgeCls = 'risk-status-issue';
            icon = '⚠️';
          } else if (d.status === 'Insufficient data') {
            statusCls = 'status-insufficient';
            badgeCls = 'risk-status-insufficient';
            icon = '❓';
          } else if (d.status === 'Not checked') {
            statusCls = 'status-not-checked';
            badgeCls = 'risk-status-not-checked';
            icon = '🔍';
          }

          return `
            <div class="risk-matrix-card ${statusCls}">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 8px;">
                <b style="font-size: 14px; color: var(--text-primary);">${d.dimension_name}</b>
                <span class="risk-status-badge ${badgeCls}">${icon} ${d.status}</span>
              </div>
              <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; line-height: 1.5;">${d.explanation}</p>
              <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 10px; border-radius: 4px; font-size: 11px; margin-bottom: 8px;">
                <div><b>Audited Evidence:</b> <span style="color: var(--text-primary);">${d.evidence}</span></div>
                <div style="color: var(--text-muted); margin-top: 2px;"><b>Source Date:</b> ${d.source_date} • <b>Severity:</b> ${d.severity}</div>
              </div>
              <div style="font-size: 11px; color: #38bdf8;">
                <b>Recommended Investigation:</b> ${d.recommended_investigation}
              </div>
            </div>
          `;
        }).join('');
      }

      // Granular Red Flags Container
      const container = document.getElementById('risk-flags-container');
      if (container) {
        if (flags.length === 0) {
          container.innerHTML = `<div class="card" style="border-left: 4px solid var(--success);"><p class="positive" style="margin: 0;"><b>No critical forensic governance red flags detected for ${sym}.</b></p></div>`;
        } else {
          container.innerHTML = flags.map(f => `
            <div class="card" style="margin-bottom: 12px; border-left: 4px solid ${f.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)'};">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div>
                  <span class="badge ${f.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${f.severity}</span>
                  <span class="badge badge-purple">${f.category}</span>
                  <b style="margin-left: 8px;">${f.title}</b>
                </div>
                <span style="font-size: 11px; color: var(--text-muted);">${f.evidence_source || 'Audited Accounts'}</span>
              </div>
              <p style="font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin: 0;">${f.description}</p>
            </div>
          `).join('');
        }
      }
    } catch (e) {
      console.error('Error loading risk flags and matrix:', e);
    }
  },

  // 15. Reports View
  loadReportsView() {
    document.getElementById('report-current-symbol').textContent = this.currentSymbol;
  },

  downloadReport(format) {
    const sym = this.currentSymbol;
    const url = format === 'pdf' ? `/api/reports/pdf/${sym}` : `/api/reports/csv/${sym}`;
    window.open(url, '_blank');
  },

  // 16. Health & Settings
  async loadHealthStatus() {
    try {
      const res = await fetch('/api/health');
      const health = await res.json();

      document.getElementById('health-db').textContent = health.database;
      document.getElementById('health-cached-symbols').textContent = health.cached_symbols;
      document.getElementById('health-indexed-docs').textContent = health.documents_indexed;
      document.getElementById('health-providers-json').textContent = JSON.stringify(health.active_providers, null, 2);

      const diagBody = document.getElementById('health-diagnostics-body');
      if (diagBody && health.diagnostics) {
        diagBody.innerHTML = health.diagnostics.map(d => {
          let badgeClass = 'badge-success';
          if (d.status === 'DEGRADED' || d.status.includes('STANDBY')) badgeClass = 'badge-warning';
          if (d.status === 'OFFLINE' || d.status === 'EMPTY') badgeClass = 'badge-danger';
          if (d.status === 'CONFIGURED') badgeClass = 'badge-primary';

          return `
            <tr id="diag-row-${d.id}">
              <td><b>${d.name}</b><br/><span style="font-size: 11px; color: var(--text-muted);">${d.id}</span></td>
              <td style="font-size: 11px; max-width: 260px;">${d.capability}</td>
              <td><span class="badge ${badgeClass}" id="diag-badge-${d.id}">${d.status}</span></td>
              <td id="diag-latency-${d.id}">${d.latency_ms} ms</td>
              <td style="font-size: 11px; color: var(--text-secondary);">${d.data_freshness}</td>
              <td style="font-size: 11px; color: var(--text-muted);">${d.credentials}</td>
              <td><button class="btn btn-outline btn-sm" onclick="App.testProviderConnection('${d.id}')">Test</button></td>
            </tr>
          `;
        }).join('');
      }
    } catch (e) {
      console.error('Error loading health status:', e);
    }
  },

  async testProviderConnection(providerId) {
    const resultBox = document.getElementById('health-probe-result');
    if (resultBox) {
      resultBox.style.display = 'block';
      resultBox.innerHTML = `<i>Probing ${providerId}...</i>`;
    }
    try {
      const res = await fetch(`/api/health/test-connection/${providerId}`);
      const data = await res.json();
      if (resultBox) {
        const color = (data.status === 'HEALTHY' || data.status === 'CONFIGURED') ? '#38bdf8' : '#f59e0b';
        resultBox.innerHTML = `<b>${data.name} Probe Result:</b> Status: <span style="color:${color};">${data.status}</span> | Latency: <b>${data.latency_ms} ms</b> | Message: ${data.message}`;
      }
      const latEl = document.getElementById(`diag-latency-${providerId}`);
      if (latEl) latEl.textContent = `${data.latency_ms} ms`;
      const badgeEl = document.getElementById(`diag-badge-${providerId}`);
      if (badgeEl) {
        badgeEl.textContent = data.status;
        badgeEl.className = `badge ${(data.status === 'HEALTHY' || data.status === 'CONFIGURED') ? 'badge-success' : 'badge-warning'}`;
      }
    } catch (e) {
      if (resultBox) {
        resultBox.innerHTML = `<span style="color: #ef4444;">Error probing ${providerId}: ${e.message}</span>`;
      }
    }
  },

  async loadSettings() {
    try {
      const res = await fetch('/api/settings');
      const cfg = await res.json();
      const statusEl = document.getElementById('setting-gemini-status');
      const keyInput = document.getElementById('setting-gemini-key');
      if (statusEl) {
        statusEl.textContent = cfg.gemini_api_configured ? "Configured & Active" : "Unset (Using Local Evidence Engine)";
        statusEl.className = cfg.gemini_api_configured ? "positive" : "";
      }
      if (keyInput) {
        if (cfg.gemini_api_configured) {
          keyInput.placeholder = "•••••••••••••••• (Configured in Settings)";
          keyInput.value = "";
        } else {
          keyInput.placeholder = "Enter Gemini API key to configure...";
          keyInput.value = "";
        }
      }
      const exchSelect = document.getElementById('setting-exchange');
      if (exchSelect && cfg.default_exchange) {
        exchSelect.value = cfg.default_exchange;
      }
    } catch (e) {}
  },

  async saveSettings() {
    const keyInput = document.getElementById('setting-gemini-key');
    const exchSelect = document.getElementById('setting-exchange');
    const payload = {};
    if (keyInput && keyInput.value.trim()) {
      payload.gemini_api_key = keyInput.value.trim();
    }
    if (exchSelect) {
      payload.default_exchange = exchSelect.value;
    }
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert('Settings updated successfully.');
      this.loadSettings();
    } catch (e) {
      alert('Failed to update settings.');
    }
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
