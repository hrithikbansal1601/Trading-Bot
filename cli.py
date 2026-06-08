#!/usr/bin/env python3
"""
trading_bot CLI — place orders on Binance Futures Testnet (USDT-M)

Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 95000
  python cli.py place --symbol BTCUSDT --side BUY --type STOP_MARKET --qty 0.001 --stop-price 85000
  python cli.py ping
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.orders import place_order
from bot.validators import ValidationError
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger("cli")


def _get_client() -> BinanceClient:
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        print(
            "ERROR: BINANCE_API_KEY and BINANCE_API_SECRET must be set.\n"
            "Copy .env.example to .env and fill in your testnet credentials."
        )
        sys.exit(1)
    return BinanceClient(api_key, api_secret)


def cmd_ping(args: argparse.Namespace) -> None:
    client = _get_client()
    ok = client.ping()
    sys.exit(0 if ok else 1)


def cmd_place(args: argparse.Namespace) -> None:
    client = _get_client()
    try:
        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side.upper(),
            order_type=args.type.upper(),
            quantity=str(args.qty),
            price=str(args.price) if args.price is not None else None,
            stop_price=str(args.stop_price) if args.stop_price is not None else None,
        )
    except (ValidationError, BinanceAPIError) as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet trading bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ping
    sub.add_parser("ping", help="Check connectivity to Binance Futures Testnet")

    # place
    p = sub.add_parser("place", help="Place a futures order")
    p.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    p.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side",
    )
    p.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET", "market", "limit", "stop_market"],
        help="Order type",
    )
    p.add_argument("--qty", required=True, type=float, help="Order quantity")
    p.add_argument("--price", type=float, default=None, help="Limit price (required for LIMIT)")
    p.add_argument(
        "--stop-price",
        dest="stop_price",
        type=float,
        default=None,
        help="Stop price (required for STOP_MARKET)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {"ping": cmd_ping, "place": cmd_place}
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
