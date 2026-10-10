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

  renderCandlestickChart(containerId, candles, symbol) {
    if (!candles || candles.length === 0) return;

    const dates = candles.map(c => c.timestamp);
    const opens = candles.map(c => c.open);
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);
    const closes = candles.map(c => c.close);
    const volumes = candles.map(c => c.volume);

    const candleTrace = {
      type: 'candlestick',
      x: dates,
      open: opens,
      high: highs,
      low: lows,
      close: closes,
      increasing: { line: { color: '#10b981' } },
      decreasing: { line: { color: '#f43f5e' } },
      name: symbol,
      yaxis: 'y1'
    };

    const volumeColors = closes.map((c, i) => (i > 0 && c >= closes[i-1]) ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)');
    const volumeTrace = {
      type: 'bar',
      x: dates,
      y: volumes,
      marker: { color: volumeColors },
      name: 'Volume',
      yaxis: 'y2'
    };

    const layout = {
      ...this.themeLayout,
      title: `${symbol} — Historical Price & Volume (NSE)`,
      yaxis: { domain: [0.25, 1], gridcolor: 'rgba(51, 65, 85, 0.4)' },
      yaxis2: { domain: [0, 0.20], gridcolor: 'rgba(51, 65, 85, 0.4)', showgrid: false },
      xaxis: { rangeslider: { visible: false }, gridcolor: 'rgba(51, 65, 85, 0.4)' },
      showlegend: false
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
      name: 'Quality-Value Strategy',
      line: { color: '#38bdf8', width: 2.5 }
    };

    const benchTrace = {
      type: 'scatter',
      mode: 'lines',
      x: dates,
      y: benchmark,
      name: 'Nifty Smallcap 100 Index',
      line: { color: '#94a3b8', width: 1.5, dash: 'dot' }
    };

    const layout = {
      ...this.themeLayout,
      title: 'Walk-Forward Equity Curve (Rebased to 100 with STT & Costs)',
      legend: { orientation: 'h', y: -0.2, font: { color: '#f8fafc' } }
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
