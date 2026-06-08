from __future__ import annotations
import re


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z]{2,20}$", symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Use uppercase letters only, e.g. BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got {qty}.")
    return qty


def validate_price(price: str | None, order_type: str) -> float | None:
    if order_type in {"LIMIT", "STOP_MARKET"} and price is None:
        raise ValidationError(f"Price is required for {order_type} orders.")
    if price is None:
        return None
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be positive, got {p}.")
    return p


def validate_stop_price(stop_price: str | None, order_type: str) -> float | None:
    if order_type == "STOP_MARKET" and stop_price is None:
        raise ValidationError("stop_price is required for STOP_MARKET orders.")
    if stop_price is None:
        return None
    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid stop_price '{stop_price}'.")
    if sp <= 0:
        raise ValidationError(f"stop_price must be positive, got {sp}.")
    return sp
