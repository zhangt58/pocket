#!/usr/bin/env python3
"""Systematic market monitoring HTML report generator with trend charts."""

import yfinance as yf
import json
import os
import glob
import base64
import io
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np


# ─── Configuration ───────────────────────────────────────────────────────────

INDICES = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'DOW': '^DJI',
    'Russell 2000': '^RUT',
}

ETFs = {
    'SPY (S&P 500)': 'SPY',
    'QQQ (Nasdaq 100)': 'QQQ',
    'IWM (Russell 2000)': 'IWM',
    'EFA (Intl Dev)': 'EFA',
    'EEM (Emerging Mkt)': 'EEM',
    'AGG (Bonds)': 'AGG',
    'TLT (Long Bonds)': 'TLT',
    'GLD (Gold)': 'GLD',
    'VNQ (REITs)': 'VNQ',
    'XLF (Financials)': 'XLF',
    'XLK (Tech)': 'XLK',
    'XLE (Energy)': 'XLE',
    'XLV (Healthcare)': 'XLV',
    'IEMG (Emerg Mk ETF)': 'IEMG',
}

SECTOR_LABELS = {
    'XLK': 'Technology',
    'XLF': 'Financials',
    'XLE': 'Energy',
    'XLV': 'Healthcare',
    'VNQ': 'Real Estate',
    'GLD': 'Gold',
    'XLI': 'Industrials',
    'XLP': 'Consumer Staples',
    'XLY': 'Consumer Discretionary',
    'XLU': 'Utilities',
    'XLRE': 'Real Estate',
    'XLB': 'Materials',
    'XLME': 'Materials',
}

OUTPUT_DIR = '/home/tong/workspace/pocket/market'
JSON_DIR = '/home/tong/workspace/pocket/market'

# ─── Colors ──────────────────────────────────────────────────────────────────

DARK_BG = '#0f172a'
DARK_CARD = '#1e293b'
DARK_GRID = '#334155'
TEXT_PRIMARY = '#e2e8f0'
TEXT_SECONDARY = '#94a3b8'
POSITIVE = '#10b981'
NEGATIVE = '#ef4444'
NEUTRAL = '#f59e0b'
CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4',
                '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16', '#a855f7',
                '#0ea5e9', '#e11d48']


# ─── Historical Data ─────────────────────────────────────────────────────────

def load_historical_data():
    """Load all historical JSON files and return sorted list of records."""
    records = []
    json_files = sorted(glob.glob(os.path.join(JSON_DIR, '*.json')))
    for fpath in json_files:
        try:
            with open(fpath) as f:
                data = json.load(f)
            records.append(data)
        except Exception as e:
            print(f'Warning: Failed to load {fpath}: {e}')
    return records


def build_time_series(records, section='indices'):
    """Build time series dicts from historical records.
    
    Returns {name: {'dates': [...], 'prices': [...], 'changes': [...]}}
    """
    series = {}
    for rec in records:
        ts = rec.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        
        data_block = rec.get(section, {})
        for name, d in data_block.items():
            if name not in series:
                series[name] = {'dates': [], 'prices': [], 'changes': []}
            series[name]['dates'].append(dt)
            series[name]['prices'].append(d.get('price', 0))
            series[name]['changes'].append(d.get('change_pct', 0))
    return series


def build_vix_time_series(records):
    """Build VIX time series from historical records."""
    dates = []
    values = []
    for rec in records:
        ts = rec.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        vix = rec.get('vix')
        if vix:
            dates.append(dt)
            values.append(vix.get('current', 0))
    return {'dates': dates, 'values': values}


# ─── Chart Generation ────────────────────────────────────────────────────────

def setup_dark_style(fig):
    """Apply dark theme to a matplotlib figure."""
    fig.patch.set_facecolor(DARK_BG)
    for ax in fig.get_axes():
        ax.set_facecolor(DARK_BG)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(DARK_GRID)
        ax.spines['bottom'].set_color(DARK_GRID)
        ax.tick_params(colors=TEXT_SECONDARY)
        ax.grid(True, color=DARK_GRID, alpha=0.3, linestyle='--')


def fig_to_base64(fig, dpi=150):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('ascii')
    plt.close(fig)
    return b64


def chart_index_trends(index_series):
    """Chart 1: Normalized index trends (all indices to 100 baseline)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    setup_dark_style(fig)
    
    names = ['S&P 500', 'NASDAQ', 'DOW', 'Russell 2000']
    for i, name in enumerate(names):
        if name not in index_series or len(index_series[name]['dates']) < 2:
            continue
        s = index_series[name]
        # Normalize to 100
        prices = np.array(s['prices'])
        normalized = prices / prices[0] * 100
        ax.plot(s['dates'], normalized, label=name, color=CHART_COLORS[i],
                linewidth=2, zorder=3)
    
    ax.set_title('Index Trends (Normalized to 100)', fontsize=14, color=TEXT_PRIMARY, fontweight='bold')
    ax.set_ylabel('Relative Performance', color=TEXT_SECONDARY)
    ax.legend(loc='upper left', fontsize=10, facecolor=DARK_BG, 
              edgecolor=DARK_GRID, labelcolor=TEXT_SECONDARY)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=0)
    return fig_to_base64(fig)


def chart_vix_trend(vix_series):
    """Chart 2: VIX trend with fear/greed zones."""
    if not vix_series['dates'] or len(vix_series['values']) < 2:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 4))
    setup_dark_style(fig)
    
    values = np.array(vix_series['values'])
    dates = vix_series['dates']
    
    # Fear/greed zones
    ax.axhspan(0, 15, alpha=0.08, color=POSITIVE)
    ax.axhspan(15, 20, alpha=0.05, color=NEUTRAL)
    ax.axhspan(20, max(values.max() + 5, 35), alpha=0.08, color=NEGATIVE)
    
    ax.axhline(y=15, color=POSITIVE, linestyle=':', alpha=0.5, linewidth=1)
    ax.axhline(y=20, color=NEUTRAL, linestyle=':', alpha=0.5, linewidth=1)
    
    # Color segments
    for i in range(len(values) - 1):
        color = POSITIVE if values[i] < 15 else (NEGATIVE if values[i] >= 20 else NEUTRAL)
        ax.plot(dates[i:i+2], values[i:i+2], color=color, linewidth=2, zorder=3)
    
    ax.fill_between(dates, values, alpha=0.15, color=TEXT_SECONDARY)
    ax.set_title('VIX Volatility Index', fontsize=14, color=TEXT_PRIMARY, fontweight='bold')
    ax.set_ylabel('VIX', color=TEXT_SECONDARY)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate(rotation=0)
    
    # Zone labels
    ax.text(dates[0], 12, 'Low Fear', fontsize=8, color=POSITIVE, alpha=0.7)
    ax.text(dates[0], 17, 'Normal', fontsize=8, color=NEUTRAL, alpha=0.7)
    ax.text(dates[0], 23, 'Elevated', fontsize=8, color=NEGATIVE, alpha=0.7)
    
    return fig_to_base64(fig)


def chart_etf_performance(etf_series):
    """Chart 3: ETF daily change % bar chart (latest day)."""
    fig, ax = plt.subplots(figsize=(12, 5))
    setup_dark_style(fig)
    
    # Sort by latest change
    etf_names = []
    changes = []
    for name, s in sorted(etf_series.items(), key=lambda x: x[1]['changes'][-1] if x[1]['changes'] else 0):
        if s['changes']:
            etf_names.append(name.replace(' (', '\n').replace(')', ''))
            changes.append(s['changes'][-1])
    
    colors = [POSITIVE if c >= 0 else NEGATIVE for c in changes]
    bars = ax.barh(etf_names, changes, color=colors, alpha=0.8, edgecolor='none', height=0.6)
    
    ax.axvline(x=0, color=TEXT_SECONDARY, linewidth=0.5)
    ax.set_title('ETF Daily Performance', fontsize=14, color=TEXT_PRIMARY, fontweight='bold')
    ax.set_xlabel('Change %', color=TEXT_SECONDARY)
    ax.invert_yaxis()
    ax.xaxis.set_label_coords(0.5, -0.15)
    
    # Value labels on bars
    for bar, val in zip(bars, changes):
        label_x = val + (0.1 if val >= 0 else -0.1)
        ax.text(label_x, bar.get_y() + bar.get_height()/2, f'{val:+.2f}%',
                va='center', ha='left' if val >= 0 else 'right',
                fontsize=8, color=POSITIVE if val >= 0 else NEGATIVE)
    
    fig.autofmt_xdate(rotation=0)
    return fig_to_base64(fig)


def chart_sector_rotation(etf_series):
    """Chart 4: Sector change comparison (latest vs average)."""
    sector_names = ['XLK (Tech)', 'XLF (Financials)', 'XLE (Energy)', 
                    'XLV (Healthcare)', 'VNQ (REITs)', 'GLD (Gold)']
    
    fig, ax = plt.subplots(figsize=(8, 5))
    setup_dark_style(fig)
    
    latest = []
    avgs = []
    labels = []
    
    for name in sector_names:
        if name in etf_series and len(etf_series[name]['changes']) >= 2:
            s = etf_series[name]
            latest.append(s['changes'][-1])
            avgs.append(np.mean(s['changes']))
            labels.append(name.split('(')[0].strip())
    
    if not labels:
        return None
    
    x = np.arange(len(labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, latest, width, label='Today', 
                   color=[POSITIVE if v >= 0 else NEGATIVE for v in latest],
                   alpha=0.85, edgecolor='none')
    bars2 = ax.bar(x + width/2, avgs, width, label='Avg (period)',
                   color=[POSITIVE if v >= 0 else NEGATIVE for v in avgs],
                   alpha=0.5, edgecolor='none')
    
    ax.set_title('Sector Rotation: Today vs Period Average',
                 fontsize=13, color=TEXT_PRIMARY, fontweight='bold')
    ax.set_ylabel('Change %', color=TEXT_SECONDARY)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, color=TEXT_SECONDARY)
    ax.legend(fontsize=10, facecolor=DARK_BG, edgecolor=DARK_GRID, labelcolor=TEXT_SECONDARY)
    ax.axhline(y=0, color=TEXT_SECONDARY, linewidth=0.5)
    
    fig.autofmt_xdate(rotation=0)
    return fig_to_base64(fig)


def generate_all_charts(records):
    """Generate all charts from historical data. Returns dict of base64 strings."""
    charts = {}
    
    # Build time series
    index_series = build_time_series(records, 'indices')
    etf_series = build_time_series(records, 'etfs')
    vix_series = build_vix_time_series(records)
    
    # Generate charts
    idx_chart = chart_index_trends(index_series)
    if idx_chart:
        charts['indices'] = idx_chart
    
    vix_chart = chart_vix_trend(vix_series)
    if vix_chart:
        charts['vix'] = vix_chart
    
    etf_chart = chart_etf_performance(etf_series)
    if etf_chart:
        charts['etf_performance'] = etf_chart
    
    sector_chart = chart_sector_rotation(etf_series)
    if sector_chart:
        charts['sectors'] = sector_chart
    
    return charts


def chart_html_section(b64_img, caption):
    """Generate HTML for a chart section."""
    return f"""
    <div style="background:{DARK_CARD};border-radius:12px;padding:20px;margin:20px 0">
        <h2 style="margin:0 0 16px;color:{TEXT_PRIMARY};font-size:1.2rem">{caption}</h2>
        <div style="text-align:center">
            <img src="data:image/png;base64,{b64_img}" 
                 style="max-width:100%;border-radius:8px;background:{DARK_BG}"/>
        </div>
    </div>"""


# ─── Data Fetching ───────────────────────────────────────────────────────────

def fetch_ticker_data(ticker_sym):
    """Fetch current price, change, and moving averages for a ticker."""
    try:
        t = yf.Ticker(ticker_sym)
        hist = t.history(period='5d')
        if hist.empty:
            return None
        last = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else last
        price = last['Close']
        chg = price - prev['Close']
        chg_pct = (chg / prev['Close']) * 100 if prev['Close'] else 0
        hist_long = t.history(period='250d')
        ma50 = hist_long['Close'].tail(50).mean() if len(hist_long) >= 50 else None
        ma200 = hist_long['Close'].tail(200).mean() if len(hist_long) >= 200 else None
        return {
            'price': round(price, 2),
            'change': round(chg, 2),
            'change_pct': round(chg_pct, 2),
            'high': round(last['High'], 2),
            'low': round(last['Low'], 2),
            'volume': int(last['Volume']),
            'ma50': round(ma50, 2) if ma50 else None,
            'ma200': round(ma200, 2) if ma200 else None,
        }
    except Exception as e:
        print(f'Error fetching {ticker_sym}: {e}')
        return None


def fetch_all_data():
    """Fetch all index and ETF data."""
    indices = {}
    for name, sym in INDICES.items():
        data = fetch_ticker_data(sym)
        if data:
            indices[name] = data

    etfs = {}
    for name, sym in ETFs.items():
        data = fetch_ticker_data(sym)
        if data:
            etfs[name] = data

    # VIX
    vix_data = None
    try:
        vix = yf.Ticker('^VIX')
        vix_hist = vix.history(period='5d')
        if not vix_hist.empty:
            vix_now = vix_hist.iloc[-1]['Close']
            vix_prev = vix_hist.iloc[-2]['Close'] if len(vix_hist) >= 2 else vix_now
            vix_data = {'current': round(vix_now, 2), 'change': round(vix_now - vix_prev, 2)}
    except Exception:
        pass

    return indices, etfs, vix_data


# ─── Analysis ────────────────────────────────────────────────────────────────

def analyze_market(indices, etfs, vix_data):
    """Generate market analysis and investment suggestions."""
    # Overall sentiment
    bull_count = sum(1 for d in indices.values() if d.get('change_pct', 0) > 0)
    if bull_count >= 3:
        sentiment = 'Bullish'
        sentiment_color = POSITIVE
    elif bull_count <= 1:
        sentiment = 'Bearish'
        sentiment_color = NEGATIVE
    else:
        sentiment = 'Mixed'
        sentiment_color = NEUTRAL

    # Risk level
    if vix_data and vix_data['current'] < 15:
        risk = 'Low'
        risk_color = POSITIVE
        risk_comment = 'VIX below 15 — low fear, complacent market'
    elif vix_data and vix_data['current'] < 20:
        risk = 'Moderate'
        risk_color = NEUTRAL
        risk_comment = 'VIX in normal range — moderate uncertainty'
    else:
        risk = 'Elevated'
        risk_color = NEGATIVE
        risk_comment = 'VIX elevated — defensive positioning recommended'

    # Sector performance
    sector_etfs = {
        'Tech (XLK)': etfs.get('XLK (Tech)', {}),
        'Financials (XLF)': etfs.get('XLF (Financials)', {}),
        'Energy (XLE)': etfs.get('XLE (Energy)', {}),
        'Healthcare (XLV)': etfs.get('XLV (Healthcare)', {}),
        'REITs (VNQ)': etfs.get('VNQ (REITs)', {}),
        'Gold (GLD)': etfs.get('GLD (Gold)', {}),
    }
    top_sectors = sorted(
        sector_etfs.items(),
        key=lambda x: x[1].get('change_pct', 0),
        reverse=True,
    )

    # MA signals
    ma_signals = []
    for name, data in etfs.items():
        if data.get('ma50') and data.get('ma200'):
            above_ma50 = data['price'] > data['ma50']
            above_ma200 = data['price'] > data['ma200']
            ma_signals.append({
                'name': name,
                'above_ma50': above_ma50,
                'above_ma200': above_ma200,
                'golden': above_ma50 and above_ma200,
                'price': data['price'],
                'ma50': data['ma50'],
                'ma200': data['ma200'],
            })

    # Generate investment suggestions
    suggestions = []
    if sentiment == 'Bullish':
        suggestions.append({
            'type': 'core',
            'title': 'Market in Uptrend',
            'desc': 'Add to core positions (SPY, QQQ) on any pullbacks. Trend is your friend.',
            'icon': '📈',
        })
        if top_sectors:
            top_name = top_sectors[0][0]
            top_chg = top_sectors[0][1].get('change_pct', 0)
            suggestions.append({
                'type': 'sector',
                'title': f'Leading Sector: {top_name}',
                'desc': f'{top_name} up {top_chg:.1f}% today — consider tactical overweight in sector ETF.',
                'icon': '🎯',
            })
    elif sentiment == 'Bearish':
        suggestions.append({
            'type': 'defensive',
            'title': 'Market Under Pressure',
            'desc': 'Reduce equity exposure, raise cash. Wait for better entry points.',
            'icon': '🛡️',
        })
        suggestions.append({
            'type': 'defensive',
            'title': 'Defensive Positions',
            'desc': 'Consider defensive ETFs: TLT (long bonds), GLD (gold), XLV (healthcare).',
            'icon': '🛡️',
        })

    if vix_data and vix_data['current'] < 15:
        suggestions.append({
            'type': 'options',
            'title': 'Low Volatility Environment',
            'desc': 'VIX below 15 — good for premium-selling options strategies.',
            'icon': '📊',
        })
    elif vix_data and vix_data['current'] >= 20:
        suggestions.append({
            'type': 'defensive',
            'title': 'High Volatility Alert',
            'desc': 'VIX elevated — use position sizing discipline, consider protective puts.',
            'icon': '⚠️',
        })

    # Small cap signal
    russell = indices.get('Russell 2000', {})
    sp500 = indices.get('S&P 500', {})
    if russell.get('change_pct', 0) < 0 and sp500.get('change_pct', 0) > 0:
        suggestions.append({
            'type': 'signal',
            'title': 'Flight to Quality',
            'desc': 'Large caps outperforming small caps — risk-off signal. Favor quality/value stocks.',
            'icon': '🔄',
        })

    # Gold signal
    if etfs.get('GLD (Gold)', {}).get('change_pct', 0) > 1:
        suggestions.append({
            'type': 'signal',
            'title': 'Gold Rally',
            'desc': f"GLD up {etfs['GLD (Gold)']['change_pct']:.1f}% — safe-haven demand. Consider as portfolio hedge.",
            'icon': '🥇',
        })

    # MA-based trend signals
    for sig in ma_signals:
        if sig['golden']:
            suggestions.append({
                'type': 'trend',
                'title': f'{sig["name"]}: Bullish Trend',
                'desc': f'Price (${sig["price"]:.2f}) above MA50 (${sig["ma50"]:.2f}) and MA200 (${sig["ma200"]:.2f}) — uptrend intact.',
                'icon': '✅',
            })

    return {
        'sentiment': sentiment,
        'sentiment_color': sentiment_color,
        'risk': risk,
        'risk_color': risk_color,
        'risk_comment': risk_comment,
        'top_sectors': top_sectors,
        'ma_signals': ma_signals,
        'suggestions': suggestions,
        'bull_count': bull_count,
    }


# ─── HTML Generation ────────────────────────────────────────────────────────

CSS = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, {DARK_BG} 0%, #1e1b4b 50%, {DARK_BG} 100%);
    color: {TEXT_PRIMARY};
    padding: 32px 24px;
    max-width: 1200px;
    margin: 0 auto;
}}
h1 {{ font-size: 2rem; margin-bottom: 8px; }}
h2 {{ font-size: 1.3rem; margin: 28px 0 14px; color: {TEXT_SECONDARY}; }}
.header {{
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 16px; margin-bottom: 28px;
}}
.badge {{
    display: inline-block; padding: 6px 16px; border-radius: 20px;
    font-weight: 700; font-size: 0.9rem;
}}
table {{
    width: 100%; border-collapse: collapse; margin: 12px 0;
    background: {DARK_CARD}; border-radius: 12px; overflow: hidden;
}}
th {{
    background: {DARK_GRID}; padding: 12px 16px; text-align: left;
    font-weight: 600; font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 0.05em; color: {TEXT_SECONDARY};
}}
td {{ padding: 10px 16px; border-bottom: 1px solid {DARK_GRID}; font-size: 0.95rem; }}
tr:last-child td {{ border-bottom: none; }}
tr:hover {{ background: {DARK_GRID}; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
@media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
.card {{
    background: {DARK_CARD}; border-radius: 12px; padding: 20px;
    border-left: 4px solid var(--accent);
}}
.vix-display {{
    text-align: center; padding: 24px; background: {DARK_CARD};
    border-radius: 12px; margin: 24px 0;
}}
.suggestion-card {{
    background: {DARK_CARD}; border-left: 4px solid var(--accent);
    border-radius: 8px; padding: 16px; margin-bottom: 12px;
}}
.suggestion-title {{ font-size: 1.05rem; font-weight: 600; margin-bottom: 4px; }}
.suggestion-desc {{ color: {TEXT_SECONDARY}; font-size: 0.9rem; }}
.footer {{
    margin-top: 32px; text-align: center; color: #64748b; font-size: 0.8rem;
}}
.positive {{ color: {POSITIVE}; font-weight: 600; }}
.negative {{ color: {NEGATIVE}; font-weight: 600; }}
.neutral {{ color: #9ca3af; }}
.chart-section {{
    background: {DARK_CARD}; border-radius: 12px; padding: 20px; margin: 20px 0;
}}
.chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
"""


def color_for_pct(val):
    if val > 0.05:
        return 'positive'
    elif val < -0.05:
        return 'negative'
    return 'neutral'


def build_index_rows(indices):
    rows = ''
    for name, d in indices.items():
        cls = color_for_pct(d['change_pct'])
        rows += f"""
    <tr>
        <td style="font-weight:600">{name}</td>
        <td>{d['price']:,.2f}</td>
        <td class="{cls}">{d['change']:+,.2f}</td>
        <td class="{cls}">{d['change_pct']:+.2f}%</td>
        <td>{d['high']:,.2f}</td>
        <td>{d['low']:,.2f}</td>
    </tr>"""
    return rows


def build_etf_rows(etfs):
    rows = ''
    for name, d in etfs.items():
        cls = color_for_pct(d['change_pct'])
        ma50 = '✅' if d.get('ma50') and d['price'] > d['ma50'] else '❌'
        ma200 = '✅' if d.get('ma200') and d['price'] > d['ma200'] else '❌'
        rows += f"""
    <tr>
        <td style="font-weight:600">{name}</td>
        <td>{d['price']:,.2f}</td>
        <td class="{cls}">{d['change_pct']:+.2f}%</td>
        <td>{ma50}</td>
        <td>{ma200}</td>
    </tr>"""
    return rows


def build_sector_rows(top_sectors):
    rows = ''
    for i, (name, d) in enumerate(top_sectors):
        cls = color_for_pct(d.get('change_pct', 0))
        rows += f"""
    <tr>
        <td>{i + 1}</td>
        <td style="font-weight:600">{name}</td>
        <td class="{cls}">{d.get('change_pct', 0):+.2f}%</td>
        <td>{d.get('price', 'N/A')}</td>
    </tr>"""
    return rows


def build_suggestion_cards(suggestions):
    type_colors = {
        'core': '#3b82f6',
        'sector': POSITIVE,
        'defensive': NEGATIVE,
        'signal': NEUTRAL,
        'options': '#8b5cf6',
        'trend': '#06b6d4',
    }
    cards = ''
    for s in suggestions:
        color = type_colors.get(s['type'], '#6b7280')
        cards += f"""
    <div class="suggestion-card" style="--accent:{color}">
        <div class="suggestion-title">{s['icon']} {s['title']}</div>
        <div class="suggestion-desc">{s['desc']}</div>
    </div>"""
    return cards


def generate_html(indices, etfs, vix_data, analysis, now, charts=None):
    """Generate the complete HTML report with embedded charts."""
    vix_html = ''
    if vix_data:
        vix_color = POSITIVE if vix_data['current'] < 15 else (
            NEUTRAL if vix_data['current'] < 20 else NEGATIVE
        )
        vix_html = f"""
    <div class="vix-display">
        <div style="font-size:2.5rem;font-weight:700;color:{vix_color}">
            VIX: {vix_data['current']:.2f}
        </div>
        <div style="color:{TEXT_SECONDARY};margin-top:8px">
            Volatility Index
            <span style="color:{vix_color}">({vix_data['change']:+.2f})</span>
        </div>
    </div>"""

    # Build chart sections
    charts_html = ''
    if charts:
        if 'indices' in charts:
            charts_html += chart_html_section(charts['indices'], '📈 Index Trends (Normalized)')
        if 'vix' in charts:
            charts_html += chart_html_section(charts['vix'], '😱 VIX Volatility Trend')
        if 'etf_performance' in charts:
            charts_html += f"""
    <div class="chart-section">
        <h2 style="margin:0 0 16px;color:{TEXT_PRIMARY};font-size:1.2rem">📊 ETF Daily Performance</h2>
        <div style="text-align:center">
            <img src="data:image/png;base64,{charts['etf_performance']}" 
                 style="max-width:100%;border-radius:8px;background:{DARK_BG}"/>
        </div>
    </div>"""
        if 'sectors' in charts:
            charts_html += f"""
    <div class="chart-section">
        <h2 style="margin:0 0 16px;color:{TEXT_PRIMARY};font-size:1.2rem">🔄 Sector Rotation</h2>
        <div style="text-align:center">
            <img src="data:image/png;base64,{charts['sectors']}" 
                 style="max-width:100%;border-radius:8px;background:{DARK_BG}"/>
        </div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en" style="color-scheme:dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Monitor - {now.strftime('%B %d, %Y')}</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 Market Monitor</h1>
            <div style="color:{TEXT_SECONDARY}">{now.strftime('%A, %B %d, %Y at %I:%M %p')} ET</div>
        </div>
        <div style="display:flex;gap:12px;align-items:center">
            <span class="badge" style="background:{analysis['sentiment_color']}22;color:{analysis['sentiment_color']};border:1px solid {analysis['sentiment_color']}44">
                {analysis['sentiment']}
            </span>
            <span class="badge" style="background:{analysis['risk_color']}22;color:{analysis['risk_color']};border:1px solid {analysis['risk_color']}44">
                {analysis['risk']} Risk
            </span>
        </div>
    </div>

    {charts_html}

    <h2>🏛️ Major Indices</h2>
    <table>
        <thead>
            <tr>
                <th>Index</th><th>Price</th><th>Change</th><th>Change %</th><th>Day High</th><th>Day Low</th>
            </tr>
        </thead>
        <tbody>{build_index_rows(indices)}</tbody>
    </table>

    <h2>📦 Key ETFs</h2>
    <table>
        <thead>
            <tr>
                <th>ETF</th><th>Price</th><th>Change %</th><th>Above MA50</th><th>Above MA200</th>
            </tr>
        </thead>
        <tbody>{build_etf_rows(etfs)}</tbody>
    </table>

    {vix_html}

    <div class="grid">
        <div>
            <h2>🏆 Sector Rotation</h2>
            <table>
                <thead>
                    <tr><th>#</th><th>Sector</th><th>Change %</th><th>Price</th></tr>
                </thead>
                <tbody>{build_sector_rows(analysis['top_sectors'])}</tbody>
            </table>
        </div>
        <div>
            <h2>💡 Investment Suggestions</h2>
            {build_suggestion_cards(analysis['suggestions'])}
        </div>
    </div>

    <div style="margin-top:24px">
        <h2>🔑 Key Signals</h2>
        <div style="background:{DARK_CARD};border-radius:12px;padding:20px">
            <p style="color:{TEXT_SECONDARY};margin-bottom:8px">
                <strong>Market Sentiment:</strong> {analysis['sentiment']} — {analysis['bull_count']}/4 indices positive
            </p>
            <p style="color:{TEXT_SECONDARY};margin-bottom:8px">
                <strong>Risk Level:</strong> {analysis['risk']} — {analysis['risk_comment']}
            </p>
            <p style="color:{TEXT_SECONDARY}">
                <strong>Trend:</strong> {sum(1 for s in analysis['ma_signals'] if s['golden'])}/{len(analysis['ma_signals'])}
                ETFs above both MA50/MA200 (bullish)
            </p>
        </div>
    </div>

    <div class="footer">
        Generated at {now.isoformat()} • Data from Yahoo Finance
    </div>
</body>
</html>"""


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

    print(f'Fetching market data...')
    indices, etfs, vix_data = fetch_all_data()

    print(f'Analyzing market...')
    analysis = analyze_market(indices, etfs, vix_data)

    # Load historical data and generate charts
    print(f'Loading historical data for charts...')
    records = load_historical_data()
    charts = None
    if records:
        print(f'  Found {len(records)} historical records')
        print(f'  Generating trend charts...')
        charts = generate_all_charts(records)
        print(f'  Generated {len(charts)} charts')

    # Generate and save HTML
    html = generate_html(indices, etfs, vix_data, analysis, now, charts)
    html_file = os.path.join(OUTPUT_DIR, f'{timestamp}.html')
    with open(html_file, 'w') as f:
        f.write(html)

    # Save JSON data
    json_file = os.path.join(JSON_DIR, f'{timestamp}.json')
    with open(json_file, 'w') as f:
        json.dump({
            'timestamp': now.isoformat(),
            'indices': indices,
            'etfs': etfs,
            'vix': vix_data,
            'sentiment': analysis['sentiment'],
            'risk': analysis['risk'],
            'suggestions': analysis['suggestions'],
        }, f, indent=2)

    # Create .txt copy for Discord delivery (Discord blocks .html attachments)
    import shutil
    txt_file = os.path.join(OUTPUT_DIR, f'{timestamp}_market_report.txt')
    shutil.copy2(html_file, txt_file)

    print(f'Report saved to {html_file}')
    print(f'Text copy saved to {txt_file}')
    print(f'Data saved to {json_file}')
    print(f'Sentiment: {analysis["sentiment"]}, Risk: {analysis["risk"]}')
    print(f'Generated {len(analysis["suggestions"])} investment suggestions')


if __name__ == '__main__':
    main()
