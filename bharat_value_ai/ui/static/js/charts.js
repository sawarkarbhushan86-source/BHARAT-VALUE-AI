/**
 * Bharat Value AI - Interactive Plotly.js Financial Visualizations
 */

const ChartRenderer = {
  themeLayout: {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', color: '#94a3b8', size: 11 },
    margin: { t: 30, r: 20, l: 45, b: 35 },
    xaxis: { gridcolor: 'rgba(51, 65, 85, 0.4)', zerolinecolor: 'rgba(51, 65, 85, 0.6)' },
    yaxis: { gridcolor: 'rgba(51, 65, 85, 0.4)', zerolinecolor: 'rgba(51, 65, 85, 0.6)' }
  },

  renderCandlestickChart(containerId, candles, symbol, period = '3mo') {
    if (!candles || candles.length === 0) {
      const container = document.getElementById(containerId);
      if (container) {
        container.innerHTML = `<div style="display: flex; height: 100%; align-items: center; justify-content: center; color: var(--text-muted); font-size: 13px;">No historical trading candles available for ${symbol} in selected period.</div>`;
      }
      return;
    }

    const dates = candles.map(c => c.timestamp);
    const opens = candles.map(c => c.open);
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);
    const closes = candles.map(c => c.close);
    const volumes = candles.map(c => c.volume);

    // Compute period extremes
    const maxHigh = Math.max(...highs);
    const minLow = Math.min(...lows);
    const maxHighIdx = highs.indexOf(maxHigh);
    const minLowIdx = lows.indexOf(minLow);
    const startPrice = opens[0] || closes[0];
    const endPrice = closes[closes.length - 1];
    const periodChange = endPrice - startPrice;
    const periodChangePct = startPrice > 0 ? (periodChange / startPrice) * 100 : 0.0;
    const totalVolume = volumes.reduce((a, b) => a + b, 0);

    // Update stats bar if DOM elements exist
    const hiEl = document.getElementById('chart-period-high');
    const loEl = document.getElementById('chart-period-low');
    const chgEl = document.getElementById('chart-period-change');
    const volEl = document.getElementById('chart-period-volume');
    if (hiEl) hiEl.textContent = `₹${maxHigh.toFixed(2)}`;
    if (loEl) loEl.textContent = `₹${minLow.toFixed(2)}`;
    if (chgEl) {
      chgEl.textContent = `${periodChange >= 0 ? '+' : ''}${periodChange.toFixed(2)} (${periodChangePct >= 0 ? '+' : ''}${periodChangePct.toFixed(2)}%)`;
      chgEl.className = periodChange >= 0 ? 'positive' : 'negative';
    }
    if (volEl) {
      volEl.textContent = totalVolume > 1e7 ? `${(totalVolume / 1e7).toFixed(2)} Cr` : (totalVolume > 1e5 ? `${(totalVolume / 1e5).toFixed(2)} L` : totalVolume.toLocaleString('en-IN'));
    }

    const isIntraday = ['1d', '1w', '5d'].includes(period.toLowerCase());

    const candleTrace = {
      type: 'candlestick',
      x: dates,
      open: opens,
      high: highs,
      low: lows,
      close: closes,
      increasing: { line: { color: '#10b981', width: 1.2 }, fillcolor: '#10b981' },
      decreasing: { line: { color: '#f43f5e', width: 1.2 }, fillcolor: '#f43f5e' },
      name: `${symbol} (NSE)`,
      yaxis: 'y1',
      hoverlabel: { bgcolor: '#0f172a', bordercolor: '#38bdf8', font: { color: '#f8fafc', size: 12 } }
    };

    const volumeColors = closes.map((c, i) => (i > 0 && c >= closes[i-1]) ? 'rgba(16, 185, 129, 0.6)' : 'rgba(244, 63, 94, 0.6)');
    const volumeTrace = {
      type: 'bar',
      x: dates,
      y: volumes,
      marker: { color: volumeColors },
      name: 'Volume',
      yaxis: 'y2',
      hoverinfo: 'x+y'
    };

    const annotations = [];
    if (maxHighIdx >= 0) {
      annotations.push({
        x: dates[maxHighIdx],
        y: maxHigh,
        xref: 'x',
        yref: 'y',
        text: `H: ₹${maxHigh.toFixed(2)}`,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 1,
        arrowcolor: '#38bdf8',
        ax: 0,
        ay: -22,
        font: { size: 10, color: '#38bdf8' },
        bgcolor: 'rgba(15, 23, 42, 0.85)',
        bordercolor: '#0284c7',
        borderwidth: 1
      });
    }
    if (minLowIdx >= 0 && minLowIdx !== maxHighIdx) {
      annotations.push({
        x: dates[minLowIdx],
        y: minLow,
        xref: 'x',
        yref: 'y',
        text: `L: ₹${minLow.toFixed(2)}`,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 1,
        arrowcolor: '#fbbf24',
        ax: 0,
        ay: 22,
        font: { size: 10, color: '#fbbf24' },
        bgcolor: 'rgba(15, 23, 42, 0.85)',
        bordercolor: '#d97706',
        borderwidth: 1
      });
    }

    const layout = {
      ...this.themeLayout,
      title: false,
      margin: { t: 20, r: 25, l: 55, b: 35 },
      yaxis: {
        domain: [0.28, 1],
        gridcolor: 'rgba(51, 65, 85, 0.35)',
        tickprefix: '₹',
        tickformat: ',.2f',
        showspikes: true,
        spikemode: 'across',
        spikesnap: 'cursor',
        spikethickness: 1,
        spikedash: 'dot',
        spikecolor: '#38bdf8',
        side: 'right'
      },
      yaxis2: {
        domain: [0, 0.22],
        gridcolor: 'rgba(51, 65, 85, 0.2)',
        showgrid: false,
        tickformat: '.2s',
        side: 'right'
      },
      xaxis: {
        rangeslider: { visible: false },
        gridcolor: 'rgba(51, 65, 85, 0.35)',
        showspikes: true,
        spikemode: 'across',
        spikesnap: 'cursor',
        spikethickness: 1,
        spikedash: 'dot',
        spikecolor: '#38bdf8',
        rangebreaks: isIntraday ? [] : [{ bounds: ['sat', 'mon'] }]
      },
      showlegend: false,
      hovermode: 'x unified',
      annotations: annotations
    };

    Plotly.newPlot(containerId, [candleTrace, volumeTrace], layout, { responsive: true, displayModeBar: false });
  },

  renderSensitivityHeatmap(containerId, matrix, waccLabels, growthLabels) {
    if (!matrix || matrix.length === 0) return;

    const trace = {
      z: matrix,
      x: growthLabels.map(g => `${g}% Growth`),
      y: waccLabels.map(w => `${w}% WACC`),
      type: 'heatmap',
      colorscale: [
        [0, '#0f172a'],
        [0.5, '#0284c7'],
        [1, '#38bdf8']
      ],
      hoverongaps: false
    };

    const layout = {
      ...this.themeLayout,
      title: 'DCF Fair Value Sensitivity Matrix (₹ per share)',
      margin: { t: 40, r: 30, l: 80, b: 40 }
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true, displayModeBar: false });
  },

  renderBacktestEquityCurve(containerId, equityCurve) {
    if (!equityCurve || equityCurve.length === 0) return;

    const dates = equityCurve.map(p => p.date);
    const strategy = equityCurve.map(p => p.strategy);
    const benchmark = equityCurve.map(p => p.benchmark);

    const stratTrace = {
      type: 'scatter',
      mode: 'lines',
      x: dates,
      y: strategy,
      name: 'Quality-Value Strategy (Net of Friction)',
      line: { color: '#38bdf8', width: 2.8 },
      hovertemplate: 'Strategy: ₹%{y:.2f}<extra></extra>'
    };

    const benchTrace = {
      type: 'scatter',
      mode: 'lines',
      x: dates,
      y: benchmark,
      name: 'Nifty Smallcap 100 Index',
      line: { color: '#94a3b8', width: 1.8, dash: 'dot' },
      hovertemplate: 'Benchmark: ₹%{y:.2f}<extra></extra>'
    };

    const layout = {
      ...this.themeLayout,
      title: 'Walk-Forward Equity Curve (Rebased to ₹100 with Brokerage, STT, GST & Slippage)',
      hovermode: 'x unified',
      xaxis: {
        title: 'Rebalance Date',
        type: 'date',
        tickformat: '%b %Y',
        gridcolor: 'rgba(255, 255, 255, 0.06)',
        color: '#94a3b8'
      },
      yaxis: {
        title: 'Portfolio Value (₹)',
        gridcolor: 'rgba(255, 255, 255, 0.06)',
        color: '#94a3b8'
      },
      legend: {
        orientation: 'h',
        y: -0.22,
        font: { color: '#f8fafc', size: 12 }
      },
      margin: { t: 40, r: 25, l: 60, b: 50 }
    };

    Plotly.newPlot(containerId, [stratTrace, benchTrace], layout, { responsive: true, displayModeBar: false });
  },

  renderFeatureImportanceChart(containerId, featDict) {
    if (!featDict) return;

    const keys = Object.keys(featDict);
    const vals = Object.values(featDict);

    const trace = {
      type: 'bar',
      orientation: 'h',
      x: vals,
      y: keys,
      marker: { color: '#a855f7' }
    };

    const layout = {
      ...this.themeLayout,
      title: 'XGBoost Feature Importance (Cross-Sectional Alpha Signal)',
      margin: { t: 30, r: 20, l: 150, b: 35 }
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true, displayModeBar: false });
  }
};
