# Crypto Liquidity Monitor

Telegram-first MVP for collecting public market data from xRocket and storing it in PostgreSQL.

> **Important:** this starter is read-only. It does not place orders, withdraw funds, or move assets.

## Features

- Telegram bot built with aiogram 3
- xRocket REST polling for ticker, trades and order book
- PostgreSQL storage
- Basic analytics:
  - current price / spread
  - 24h volume
  - order-book depth
  - recent trade count
- Docker Compose for one-command local startup
- Environment variables for secrets

## Project structure

```text
crypto-liquidity-monitor/
├── app/
│   ├── analytics/
│   │   └── market.py
│   ├── bot/
│   │   ├── handlers.py
│   │   └── keyboards.py
│   ├── collectors/
│   │   └── xrocket_collector.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── exchanges/
│   │   └── xrocket.py
│   ├── config.py
│   └── main.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 1. Create a Telegram bot

Open `@BotFather` in Telegram and create a bot. Copy its token.

## 2. Configure `.env`

```bash
cp .env.example .env
```

Set at least:

```env
TELEGRAM_BOT_TOKEN=your_token
XRocket_API_BASE_URL=https://exchange.api.xrocket.com
SYMBOL=TON/USDT
```

The exact xRocket endpoint/base URL can change. Check the current official xRocket API documentation and update `XRocket_API_BASE_URL` if needed.

## 3. Run

```bash
docker compose up --build
```

The bot should start polling Telegram.

## Telegram commands

- `/start` — menu
- `/market` — current market snapshot
- `/orderbook` — placeholder (not implemented yet, see Notes)
- `/trades` — placeholder (not implemented yet, see Notes)
- `/help` — help

## Web dashboard

`docker compose up --build` also starts a `web` service (FastAPI) that serves
a live HTML dashboard at **http://localhost:8000** (or `http://<server-ip>:8000`
on a remote server). It shows bid/ask/last price, spread, 24h volume and a
price chart, polling the same PostgreSQL data the bot collects — no separate
setup needed.

Endpoints:

- `GET /` — the dashboard page
- `GET /api/market` — latest snapshot as JSON
- `GET /api/history?limit=200` — recent snapshots for the chart

This is a plain web page today. To open it as a Telegram Mini App later, host
it behind HTTPS and point a bot menu button / inline button
(`WebApp` type) at that URL — no changes to the API are required.

## Easiest way to run it: Render (no server, no terminal)

This repo includes `render.yaml`, so [Render](https://render.com) can deploy
the dashboard, the bot, and a free PostgreSQL database automatically, with a
public HTTPS URL you just open in a browser:

1. Sign up at render.com (free) and connect your GitHub account.
2. **New +** → **Blueprint** → pick this repository. Render reads
   `render.yaml` and shows both services plus the database.
3. It will ask for `TELEGRAM_BOT_TOKEN` — paste the token from @BotFather.
4. Click **Apply**. Wait for both services to finish deploying.
5. Open the URL shown next to `liquidity-monitor-web` — that's your
   dashboard.

Free-tier services on Render pause after inactivity and cold-start with
a short delay on first request; upgrade the plan later if you need it
always instantly on.

## Notes

This MVP intentionally keeps the exchange adapter isolated in `app/exchanges/xrocket.py`. That makes it straightforward to add Binance, Bybit, CryptoBot, or another provider later without rewriting the bot/database layer.

Before connecting any real trading credentials, add a separate authenticated adapter and keep trading permissions out of this analytics service.
