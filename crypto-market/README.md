# Crypto Market Plugin

A real-time cryptocurrency market monitoring plugin for Noctalia Shell, displaying live price data from multiple exchanges.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Multi-Exchange Support**: Huobi, Binance, OKX, and CoinGecko
- **Status Bar Widget**: Display single coin price with trend indicator
- **Market Panel**: Detailed view of multiple coins with 24h high/low
- **Display Modes**: Text mode (with coin symbol) or compact mode (price only)
- **Color Schemes**: Red-rises-green-falls or green-rises-red-falls
- **Auto Logo Management**: Downloads and caches coin logos from CoinGecko CDN
- **Language Switcher**: Switch the plugin interface between English and Simplified Chinese
- **Proxy Support**: Optional HTTP/SOCKS5 proxy configuration
- **Config Import/Export**: Export and restore your settings with a JSON file

## Installation

1. Copy the plugin to Noctalia plugins directory:
```bash
cp -r crypto-market ~/.config/noctalia/plugins/
```

2. Restart Noctalia Shell or reload the configuration.

## Usage

### Status Bar Widget
- **Left Click**: Open or close the detailed market panel
- **Right Click**: Open the context menu for settings, refresh, and display mode switching

### Market Panel
- View multiple coins with real-time prices, 24h change, high/low
- Click **Refresh** button to manually update data
- Click **Settings** to configure the plugin

### Settings
- **Data Source**: Choose between Huobi, Binance, OKX, or CoinGecko
- **Proxy URL**: Optional HTTP/SOCKS5 proxy (format: `http://host:port` or `socks5://host:port`)
- **Status Bar Coin**: Select which coin to display in the status bar
- **Display Mode**: Full mode (with symbol) or compact mode (price only)
- **Watch List**: Add/remove coins by clicking, reorder with arrow buttons
- **Color Scheme**: Red rises (Chinese style) or green rises (Western style)
- **Refresh Interval**: Set update frequency from 1 to 60 seconds
- **Language**: Switch the plugin interface between English and Simplified Chinese
- **Config Management**: Export/import settings to/from `~/Downloads/crypto-market-config.json`

## Configuration

Default settings in `manifest.json`:
```json
{
  "watchList": ["btc", "eth", "bnb", "sol", "xrp"],
  "barCoin": "btc",
  "displayMode": "text",
  "redRises": false,
  "refreshInterval": 5,
  "dataSource": "huobi",
  "proxyUrl": "",
  "language": "en"
}
```

## Supported Coins

Pre-configured coins with logos:
- **BTC** (Bitcoin)
- **ETH** (Ethereum)
- **BNB** (Binance Coin)
- **SOL** (Solana)
- **XRP** (Ripple)
- **ADA** (Cardano)
- **DOT** (Polkadot)
- **DOGE** (Dogecoin)
- **MATIC** (Polygon)
- **AVAX** (Avalanche)

You can add more coins by searching in the settings panel. The plugin will automatically download logos from CoinGecko.

## Data Sources

### Huobi (Default)
- API: `https://api.huobi.pro/market/history/kline`
- No rate limits for basic usage
- Recommended refresh interval: 5 seconds

### Binance
- API: `https://api.binance.com/api/v3/klines`
- Rate limit: 1200 requests per minute
- Recommended refresh interval: 3 seconds

### OKX
- API: `https://www.okx.com/api/v5/market/candles`
- Rate limit: 20 requests per 2 seconds
- Recommended refresh interval: 5 seconds

### CoinGecko
- API: `https://api.coingecko.com/api/v3/simple/price`
- Rate limit: 50 calls per minute (free tier)
- **Minimum refresh interval: 10 seconds** (enforced by plugin)

## Troubleshooting

### No data displayed
1. Check internet connection
2. Test API access: `curl -s 'https://api.huobi.pro/market/history/kline?period=1day&size=1&symbol=btcusdt'`
3. Try enabling proxy in settings if behind a firewall
4. Switch to a different data source

### Logos not showing
- Logos are downloaded on first launch
- Check cache directory: `ls ~/.cache/noctalia/crypto-market/logos/`
- If behind a firewall, configure proxy URL in settings

### Plugin not loading
1. Verify JSON syntax: `jq . manifest.json`
2. Check plugin is enabled: `cat ~/.config/noctalia/plugins.json | jq '.states["crypto-market"]'`
3. Check Noctalia logs for errors

### Rate limit errors
- Increase refresh interval in settings
- CoinGecko free tier: use minimum 10 seconds interval
- Binance: recommended 3+ seconds for multiple coins

## Development

### Project Structure
```
crypto-market/
├── Main.qml          # Core data manager, API polling, logo cache
├── BarWidget.qml     # Status bar widget component
├── Panel.qml         # Market panel with coin table
├── Settings.qml      # Configuration interface
├── i18n/             # Plugin translations
└── manifest.json     # Plugin metadata and defaults
```

### Tech Stack
- **QML/Qt Quick**: UI framework
- **Quickshell API**: Noctalia integration
- **Process**: Shell command execution for API calls and logo downloads

### API Testing
```bash
# Test Huobi API
curl -s 'https://api.huobi.pro/market/history/kline?period=1day&size=1&symbol=btcusdt'

# Test Binance API
curl -s 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1'

# Test OKX API
curl -s 'https://www.okx.com/api/v5/market/candles?instId=BTC-USDT&bar=1D&limit=1'

# Test CoinGecko API
curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true'
```

## License

MIT License - see LICENSE file for details.

## Author

chengongliang

## Version

1.0.0 - Requires Noctalia Shell >= 4.6.6
