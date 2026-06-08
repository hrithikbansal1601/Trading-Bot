# Trading Bot — Binance Futures Testnet (USDT-M)

A clean, modular Python CLI application that places Market, Limit, and Stop-Market orders on the Binance Futures Testnet.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client wrapper
│   ├── orders.py          # Order placement logic + formatted output
│   ├── validators.py      # CLI input validation
│   └── logging_config.py  # Structured file + console logging
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Log files written here automatically
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Click **API Key** → generate a new key pair
4. Copy the API Key and Secret

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and paste your testnet API key and secret
```

`.env` contents:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

---

## Usage

### Check connectivity

```bash
python cli.py ping
```

### Place a MARKET order (BUY)

```bash
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### Place a LIMIT order (SELL)

```bash
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 106000
```

### Place a STOP_MARKET order (bonus — 3rd order type)

```bash
python cli.py place --symbol BTCUSDT --side BUY --type STOP_MARKET --qty 0.001 --stop-price 100000
```

### Help

```bash
python cli.py --help
python cli.py place --help
```

---

## Sample Output

```
┌─── Order Request ───────────────────────────
│  Symbol     : BTCUSDT
│  Side       : BUY
│  Type       : MARKET
│  Quantity   : 0.001
└─────────────────────────────────────────────
┌─── Order Response ──────────────────────────
│  orderId      : 4254632718
│  clientOrderId: web_abc123
│  status       : FILLED
│  executedQty  : 0.001
│  avgPrice     : 103241.50
│  symbol       : BTCUSDT
│  side         : BUY
│  type         : MARKET
└─────────────────────────────────────────────

✓ Order placed successfully!
```

---

## Logging

All API requests, responses, and errors are written to `logs/bot_YYYYMMDD.log`. The log level for the file is `DEBUG` (full request/response bodies); the console shows `INFO` and above to stay clean.

---

## Assumptions

- All orders are placed on the **USDT-M Futures Testnet** only. The base URL `https://testnet.binancefuture.com` is hardcoded; no production keys are ever used.
- Quantity precision is passed as-is; if Binance rejects it due to LOT_SIZE filter, reduce decimal places (e.g. `0.001` → `0.01` for some pairs).
- `timeInForce` defaults to `GTC` for LIMIT orders.
- No position or balance checks are done client-side; the API enforces them.


Binance Futures Testnet access and API availability may vary by region.