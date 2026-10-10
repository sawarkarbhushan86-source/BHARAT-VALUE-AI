/**
 * Bharat Value AI - Single Page Application Core Controller
 */

const App = {
  currentSymbol: 'CDSL',
  universe: [],

  async init() {
    this.bindEvents();
    await this.fetchMarketStatus();
    await this.fetchUniverse();
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
    this.currentSymbol = symbol.toUpperCase();
    const dropdown = document.getElementById('search-dropdown');
    if (dropdown) dropdown.style.display = 'none';

    // Update UI headers
    document.querySelectorAll('.active-symbol-badge').forEach(el => {
      el.textContent = this.currentSymbol;
    });

    this.navigate('details');
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
            <td>${item.pe_ratio.toFixed(1)}</td>
            <td class="${item.roce_pct >= 20 ? 'positive' : ''}"><b>${item.roce_pct.toFixed(1)}%</b></td>
            <td>${item.roe_pct.toFixed(1)}%</td>
            <td>${item.debt_to_equity.toFixed(2)}x</td>
            <td><span class="badge ${item.quality_score >= 70 ? 'badge-success' : 'badge-primary'}">${item.quality_score}</span></td>
            <td>₹${item.fair_value.toFixed(2)}</td>
            <td><span class="badge ${item.valuation_status === 'UNDERVALUED' ? 'badge-success' : (item.valuation_status === 'OVERVALUED' ? 'badge-danger' : 'badge-warning')}">${item.margin_of_safety_pct > 0 ? '+' : ''}${item.margin_of_safety_pct.toFixed(1)}%</span></td>
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
    try {
      const [quoteRes, candleRes, fundRes] = await Promise.all([
        fetch(`/api/market/quote/${sym}`),
        fetch(`/api/market/candles/${sym}?period=3mo`),
        fetch(`/api/fundamentals/${sym}`)
      ]);

      const quote = await quoteRes.json();
      const candles = await candleRes.json();
      const fund = await fundRes.json();

      document.getElementById('details-symbol-title').textContent = `${sym} — ${quote.exchange}`;
      document.getElementById('details-price').textContent = `₹${quote.price.toFixed(2)}`;
      const chgEl = document.getElementById('details-change');
      chgEl.textContent = `${quote.change >= 0 ? '+' : ''}${quote.change.toFixed(2)} (${quote.change_percent >= 0 ? '+' : ''}${quote.change_percent.toFixed(2)}%)`;
      chgEl.className = quote.change >= 0 ? 'positive' : 'negative';

      document.getElementById('details-volume').textContent = quote.volume.toLocaleString('en-IN');
      document.getElementById('details-turnover').textContent = `₹${quote.turnover_cr || 0} Cr`;
      document.getElementById('details-52w').textContent = `₹${quote.week_52_low} - ₹${quote.week_52_high}`;
      document.getElementById('details-pe').textContent = `${fund.pe_ratio}x`;

      ChartRenderer.renderCandlestickChart('stock-candle-chart', candles, sym);
    } catch (e) {
      console.error('Error loading stock details:', e);
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

      document.getElementById('fund-rev').textContent = `₹${fund.revenue.toLocaleString('en-IN')} Cr`;
      document.getElementById('fund-pat').textContent = `₹${fund.net_profit.toLocaleString('en-IN')} Cr`;
      document.getElementById('fund-ebitda-margin').textContent = `${fund.operating_margin_pct}%`;
      document.getElementById('fund-net-margin').textContent = `${fund.net_margin_pct}%`;
      document.getElementById('fund-roe').textContent = `${fund.roe_pct}%`;
      document.getElementById('fund-roce').textContent = `${fund.roce_pct}%`;
      document.getElementById('fund-dte').textContent = `${fund.debt_to_equity}x`;
      document.getElementById('fund-ic').textContent = `${fund.interest_coverage}x`;
      document.getElementById('fund-ocf').textContent = `₹${fund.operating_cash_flow} Cr`;
      document.getElementById('fund-fcf').textContent = `₹${fund.free_cash_flow} Cr`;
      document.getElementById('fund-ccc').textContent = `${fund.cash_conversion_cycle} Days`;
      document.getElementById('fund-altman').textContent = fund.altman_z_score;

      document.getElementById('dupont-roe').textContent = `${dupont.roe_pct}%`;
      document.getElementById('dupont-npm').textContent = `${dupont.net_profit_margin_pct}%`;
      document.getElementById('dupont-at').textContent = `${dupont.asset_turnover}x`;
      document.getElementById('dupont-em').textContent = `${dupont.equity_multiplier}x`;
      document.getElementById('dupont-interpretation').textContent = dupont.interpretation;
    } catch (e) {
      console.error('Error loading fundamentals:', e);
    }
  },

  // 5. Fair Value & DCF Sensitivity
  async loadValuation() {
    const sym = this.currentSymbol;
    try {
      const res = await fetch(`/api/valuation/${sym}`);
      const val = await res.json();

      document.getElementById('val-cmp').textContent = `₹${val.current_price.toFixed(2)}`;
      document.getElementById('val-composite').textContent = `₹${val.composite_fair_value.toFixed(2)}`;
      document.getElementById('val-dcf').textContent = `₹${val.dcf_fair_value.toFixed(2)}`;
      document.getElementById('val-pe').textContent = `₹${val.pe_fair_value.toFixed(2)}`;
      document.getElementById('val-ev').textContent = `₹${val.ev_ebitda_fair_value.toFixed(2)}`;

      const mosBadge = document.getElementById('val-mos-badge');
      mosBadge.textContent = `${val.margin_of_safety_pct > 0 ? '+' : ''}${val.margin_of_safety_pct.toFixed(1)}% (${val.valuation_status})`;
      mosBadge.className = `badge ${val.valuation_status === 'UNDERVALUED' ? 'badge-success' : (val.valuation_status === 'OVERVALUED' ? 'badge-danger' : 'badge-warning')}`;

      document.getElementById('val-bear').textContent = `₹${val.bear_case_value.toFixed(2)}`;
      document.getElementById('val-base').textContent = `₹${val.base_case_value.toFixed(2)}`;
      document.getElementById('val-bull').textContent = `₹${val.bull_case_value.toFixed(2)}`;

      // Sync Sliders
      document.getElementById('dcf-growth-slider').value = val.assumptions.revenue_growth;
      document.getElementById('dcf-growth-val').textContent = `${(val.assumptions.revenue_growth * 100).toFixed(1)}%`;
      document.getElementById('dcf-wacc-slider').value = val.assumptions.wacc;
      document.getElementById('dcf-wacc-val').textContent = `${(val.assumptions.wacc * 100).toFixed(1)}%`;
      document.getElementById('dcf-terminal-slider').value = val.assumptions.terminal_growth;
      document.getElementById('dcf-terminal-val').textContent = `${(val.assumptions.terminal_growth * 100).toFixed(1)}%`;

      ChartRenderer.renderSensitivityHeatmap('dcf-sensitivity-chart', val.sensitivity_matrix, val.sensitivity_wacc_labels, val.sensitivity_growth_labels);
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
      if (limitsList) {
        limitsList.innerHTML = qual.limitations.map(l => `<li>${l}</li>`).join('');
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
          <div class="card" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <div>
                <b style="color: var(--primary); cursor: pointer;" onclick="App.selectSymbol('${ev.symbol}')">${ev.symbol}</b>
                <span class="badge badge-purple" style="margin-left: 8px;">${ev.event_category}</span>
              </div>
              <span style="font-size: 11px; color: var(--text-muted);">${new Date(ev.event_date).toLocaleDateString('en-IN')}</span>
            </div>
            <p style="font-size: 13px; font-weight: 600; margin-bottom: 10px;">${ev.title}</p>
            <div class="grid-4" style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: var(--radius-sm);">
              <div><small style="color: var(--text-muted);">1-Day Return</small><br/><b class="${ev.reaction_1d_pct >= 0 ? 'positive' : 'negative'}">${ev.reaction_1d_pct >= 0 ? '+' : ''}${ev.reaction_1d_pct}%</b></div>
              <div><small style="color: var(--text-muted);">Abnormal Alpha</small><br/><b class="${ev.abnormal_return_1d_pct >= 0 ? 'positive' : 'negative'}">${ev.abnormal_return_1d_pct >= 0 ? '+' : ''}${ev.abnormal_return_1d_pct}%</b></div>
              <div><small style="color: var(--text-muted);">Volume Shock</small><br/><b>${ev.volume_shock_ratio}x Avg</b></div>
              <div><small style="color: var(--text-muted);">20-Day Drift</small><br/><b class="${ev.reaction_20d_pct >= 0 ? 'positive' : 'negative'}">${ev.reaction_20d_pct >= 0 ? '+' : ''}${ev.reaction_20d_pct}%</b></div>
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

  loadNLPOverview() {
    // Ready state
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

      document.getElementById('ml-spearman-badge').textContent = `Spearman Rho: +${data.spearman_rank_correlation}`;

      const topTbody = document.getElementById('ml-top-ranked-body');
      if (topTbody) {
        topTbody.innerHTML = data.top_ranked.map((item, idx) => `
          <tr onclick="App.selectSymbol('${item.symbol}')" style="cursor: pointer;">
            <td>#${idx+1} <b>${item.symbol}</b></td>
            <td><b class="positive">+${item.predicted_excess_return_pct}%</b></td>
            <td>${item.roce_pct}%</td>
            <td>${item.pe_ratio}x</td>
          </tr>
        `).join('');
      }

      ChartRenderer.renderFeatureImportanceChart('ml-feature-importance-chart', data.feature_importance);
    } catch (e) {
      console.error('Error loading ML research:', e);
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

      document.getElementById('bt-cagr').textContent = `+${data.cagr_pct}%`;
      document.getElementById('bt-sharpe').textContent = `${data.sharpe_ratio}x`;
      document.getElementById('bt-sortino').textContent = `${data.sortino_ratio}x`;
      document.getElementById('bt-maxdd').textContent = `-${data.max_drawdown_pct}%`;
      document.getElementById('bt-bench-cagr').textContent = `+${((data.benchmark_return_pct / 3.5)).toFixed(1)}%`;
      document.getElementById('bt-alpha').textContent = `+${data.alpha_pct}%`;

      ChartRenderer.renderBacktestEquityCurve('backtest-chart', data.equity_curve);
    } catch (e) {
      console.error('Error running backtest:', e);
    }
  },

  // 14. Risk & Governance
  async loadRiskFlags() {
    const sym = this.currentSymbol;
    try {
      const res = await fetch(`/api/risk/flags/${sym}`);
      const flags = await res.json();
      const container = document.getElementById('risk-flags-container');
      if (container) {
        if (flags.length === 0) {
          container.innerHTML = `<div class="card" style="border-left: 4px solid var(--success);"><p class="positive"><b>No critical forensic governance red flags detected for ${sym}.</b></p></div>`;
          return;
        }

        container.innerHTML = flags.map(f => `
          <div class="card" style="margin-bottom: 14px; border-left: 4px solid ${f.severity === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)'};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <div>
                <span class="badge ${f.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${f.severity}</span>
                <span class="badge badge-purple">${f.category}</span>
                <b style="margin-left: 8px;">${f.title}</b>
              </div>
              <span style="font-size: 11px; color: var(--text-muted);">${f.evidence_source || 'Audited Accounts'}</span>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${f.description}</p>
          </div>
        `).join('');
      }
    } catch (e) {
      console.error('Error loading risk flags:', e);
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
    } catch (e) {
      console.error('Error loading health status:', e);
    }
  },

  async loadSettings() {
    try {
      const res = await fetch('/api/settings');
      const cfg = await res.json();
      document.getElementById('setting-gemini-status').textContent = cfg.gemini_api_configured ? "Configured & Active" : "Unset (Using Local Evidence Engine)";
    } catch (e) {}
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
