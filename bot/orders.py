from __future__ import annotations
from typing import Any

from .client import BinanceClient, BinanceAPIError
from .validators import (
    ValidationError,
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from .logging_config import setup_logger

logger = setup_logger("orders")


def _fmt_order_summary(params: dict) -> str:
    lines = [
        "┌─── Order Request ───────────────────────────",
        f"│  Symbol     : {params.get('symbol')}",
        f"│  Side       : {params.get('side')}",
        f"│  Type       : {params.get('order_type')}",
        f"│  Quantity   : {params.get('quantity')}",
    ]
    if params.get("price"):
        lines.append(f"│  Price      : {params['price']}")
    if params.get("stop_price"):
        lines.append(f"│  Stop Price : {params['stop_price']}")
    lines.append("└─────────────────────────────────────────────")
    return "\n".join(lines)


def _fmt_order_response(resp: dict) -> str:
    lines = [
        "┌─── Order Response ──────────────────────────",
        f"│  orderId      : {resp.get('orderId', 'N/A')}",
        f"│  clientOrderId: {resp.get('clientOrderId', 'N/A')}",
        f"│  status       : {resp.get('status', 'N/A')}",
        f"│  executedQty  : {resp.get('executedQty', 'N/A')}",
        f"│  avgPrice     : {resp.get('avgPrice', resp.get('price', 'N/A'))}",
        f"│  symbol       : {resp.get('symbol', 'N/A')}",
        f"│  side         : {resp.get('side', 'N/A')}",
        f"│  type         : {resp.get('type', 'N/A')}",
        "└─────────────────────────────────────────────",
    ]
    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict[str, Any]:
    # Validate inputs
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        qty = validate_quantity(quantity)
        prc = validate_price(price, order_type)
        stp = validate_stop_price(stop_price, order_type)
    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        raise

    params_summary = {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": qty,
        "price": prc,
        "stop_price": stp,
    }

    print(_fmt_order_summary(params_summary))
    logger.info("Validated order params: %s", params_summary)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=qty,
            price=prc,
            stop_price=stp,
        )
    except BinanceAPIError as exc:
        logger.error("API error while placing order: %s", exc)
        print(f"\n✗ Order FAILED — {exc}")
        raise
    except Exception as exc:
        logger.error("Unexpected error while placing order: %s", exc)
        print(f"\n✗ Order FAILED — {exc}")
        raise

    print(_fmt_order_response(response))
    print("\n✓ Order placed successfully!\n")
    return response
