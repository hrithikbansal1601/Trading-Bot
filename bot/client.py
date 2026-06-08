from __future__ import annotations
import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("client")


class BinanceAPIError(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> Any:
        logger.debug("Response status: %s", response.status_code)
        logger.debug("Response body: %s", response.text)
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return response.text

        if response.status_code >= 400:
            raise BinanceAPIError(
                data.get("code", response.status_code),
                data.get("msg", "Unknown error"),
            )
        return data

    def _get(self, path: str, params: dict | None = None, signed: bool = False) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)
        url = BASE_URL + path
        logger.debug("GET %s | params: %s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.get(url, params=params, timeout=10)
            return self._handle_response(resp)
        except requests.RequestException as exc:
            logger.error("Network error during GET request: %s", exc)
            raise BinanceAPIError(-1, f"Network error: {exc}")

    def _post(self, path: str, params: dict | None = None, signed: bool = True) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)
        url = BASE_URL + path
        logger.debug("POST %s | params: %s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.post(url, data=params, timeout=10)
            return self._handle_response(resp)
        except requests.RequestException as exc:
            logger.error("Network error during POST request: %s", exc)
            raise BinanceAPIError(-1, f"Network error: {exc}")


    def ping(self) -> bool:
        try:
            self._get("/fapi/v1/ping")
            logger.info("Ping successful — testnet is reachable.")
            return True
        except Exception as exc:
            logger.error("Ping failed: %s", exc)
            return False

    def get_account_info(self) -> dict:
        return self._get("/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force
        elif order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price

        logger.info(
            "Placing order → symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
            symbol, side, order_type, quantity, price, stop_price,
        )
        result = self._post("/fapi/v1/order", params=params)
        logger.info("Order placed successfully → orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result
