#!/usr/bin/env python3
"""Systematic market monitoring HTML report generator."""

import yfinance as yf
import json
import os
from datetime import datetime


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
        sentiment_color = '#10b981'
    elif bull_count <= 1:
        sentiment = 'Bearish'
        sentiment_color = '#ef4444'
    else:
        sentiment = 'Mixed'
        sentiment_color = '#f59e0b'

    # Risk level
    if vix_data and vix_data['current'] < 15:
        risk = 'Low'
        risk_color = '#10b981'
        risk_comment = 'VIX below 15 — low fear, complacent market'
    elif vix_data and vix_data['current'] < 20:
        risk = 'Moderate'
        risk_color = '#f59e0b'
        risk_comment = 'VIX in normal range — moderate uncertainty'
    else:
        risk = 'Elevated'
        risk_color = '#ef4444'
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

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    color: #e2e8f0;
    padding: 32px 24px;
    max-width: 1200px;
    margin: 0 auto;
}
h1 { font-size: 2rem; margin-bottom: 8px; }
h2 { font-size: 1.3rem; margin: 28px 0 14px; color: #94a3b8; }
.header {
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 16px; margin-bottom: 28px;
}
.badge {
    display: inline-block; padding: 6px 16px; border-radius: 20px;
    font-weight: 700; font-size: 0.9rem;
}
table {
    width: 100%; border-collapse: collapse; margin: 12px 0;
    background: #1e293b; border-radius: 12px; overflow: hidden;
}
th {
    background: #334155; padding: 12px 16px; text-align: left;
    font-weight: 600; font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 0.05em; color: #94a3b8;
}
td { padding: 10px 16px; border-bottom: 1px solid #334155; font-size: 0.95rem; }
tr:last-child td { border-bottom: none; }
tr:hover { background: #334155; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
.card {
    background: #1e293b; border-radius: 12px; padding: 20px;
    border-left: 4px solid var(--accent);
}
.vix-display {
    text-align: center; padding: 24px; background: #1e293b;
    border-radius: 12px; margin: 24px 0;
}
.suggestion-card {
    background: #1e293b; border-left: 4px solid var(--accent);
    border-radius: 8px; padding: 16px; margin-bottom: 12px;
}
.suggestion-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 4px; }
.suggestion-desc { color: #94a3b8; font-size: 0.9rem; }
.footer {
    margin-top: 32px; text-align: center; color: #64748b; font-size: 0.8rem;
}
.positive { color: #10b981; font-weight: 600; }
.negative { color: #ef4444; font-weight: 600; }
.neutral { color: #9ca3af; }
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
        'sector': '#10b981',
        'defensive': '#ef4444',
        'signal': '#f59e0b',
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


def generate_html(indices, etfs, vix_data, analysis, now):
    """Generate the complete HTML report."""
    vix_html = ''
    if vix_data:
        vix_color = '#10b981' if vix_data['current'] < 15 else (
            '#f59e0b' if vix_data['current'] < 20 else '#ef4444'
        )
        vix_html = f"""
    <div class="vix-display">
        <div style="font-size:2.5rem;font-weight:700;color:{vix_color}">
            VIX: {vix_data['current']:.2f}
        </div>
        <div style="color:#94a3b8;margin-top:8px">
            Volatility Index
            <span style="color:{vix_color}">({vix_data['change']:+.2f})</span>
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
            <div style="color:#94a3b8">{now.strftime('%A, %B %d, %Y at %I:%M %p')} ET</div>
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
        <div style="background:#1e293b;border-radius:12px;padding:20px">
            <p style="color:#94a3b8;margin-bottom:8px">
                <strong>Market Sentiment:</strong> {analysis['sentiment']} — {analysis['bull_count']}/4 indices positive
            </p>
            <p style="color:#94a3b8;margin-bottom:8px">
                <strong>Risk Level:</strong> {analysis['risk']} — {analysis['risk_comment']}
            </p>
            <p style="color:#94a3b8">
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

    # Generate and save HTML
    html = generate_html(indices, etfs, vix_data, analysis, now)
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

    print(f'Report saved to {html_file}')
    print(f'Data saved to {json_file}')
    print(f'Sentiment: {analysis["sentiment"]}, Risk: {analysis["risk"]}')
    print(f'Generated {len(analysis["suggestions"])} investment suggestions')


if __name__ == '__main__':
    main()
