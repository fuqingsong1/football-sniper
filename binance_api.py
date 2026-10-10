"""Binance 预测市场 (Prediction Trading) SAPI 签名客户端。
文档: developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading
所有端点都是 signed endpoint：HMAC-SHA256(secret, query) + X-MBX-APIKEY 头。
"""
import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

BASE = "https://api.binance.com"
PRED = "/sapi/v1/w3w/wallet/prediction"
log = logging.getLogger("binance_api")


class BinancePredAPI:
    def __init__(self, api_key: str, api_secret: str, proxy: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        # 只认 config.yaml 里的 proxy，忽略 HTTP_PROXY/HTTPS_PROXY 等环境变量。
        # 否则在装了沙箱/全局代理变量的环境里，请求会被劫持到别的代理上（502）。
        self.session.trust_env = False
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def _sign(self, params: dict) -> dict:
        params = {k: v for k, v in params.items() if v is not None}
        params.setdefault("timestamp", int(time.time() * 1000))
        params.setdefault("recvWindow", 5000)
        qs = urlencode(params)
        sig = hmac.new(self.api_secret.encode(), qs.encode(),
                       hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    def _req(self, method: str, path: str, params: dict = None):
        params = self._sign(params or {})
        url = BASE + path
        headers = {"X-MBX-APIKEY": self.api_key}
        if method == "GET":
            r = self.session.get(url, params=params, headers=headers, timeout=20)
        else:
            r = self.session.post(url, params=params, headers=headers, timeout=20)
        try:
            data = r.json()
        except ValueError:
            r.raise_for_status()
            raise
        if isinstance(data, dict) and "code" in data and data.get("code") not in (0, 200, "0", "200"):
            # 币安错误返回 {"code": -xxxx, "msg": ...}
            raise RuntimeError(f"Binance API 错误 {data.get('code')}: {data.get('msg')}")
        return data

    def get(self, path: str, **params):
        return self._req("GET", path, params)

    def post(self, path: str, **params):
        return self._req("POST", path, params)

    # ---------------- 具体端点 ----------------
    def category_list(self):
        return self.get(PRED + "/category/list")

    def market_list(self, l1: str = None, l2: str = None,
                    sort_by="END_DATE", order_by="ASC", offset=0, limit=100):
        return self.get(PRED + "/market/list", l1Category=l1, l2Category=l2,
                        sortBy=sort_by, orderBy=order_by, offset=offset, limit=limit)

    def market_detail(self, topic_id: int):
        return self.get(PRED + "/market/detail", marketTopicId=topic_id)

    def wallet_list(self):
        return self.get(PRED + "/wallet/list")

    def portfolio(self, wallet_address: str):
        return self.get(PRED + "/pnl/portfolio", walletAddress=wallet_address)

    def get_quote(self, wallet_address: str, token_id: str, side: str,
                  amount_in_wei: int, order_type: str, price_limit: str = None,
                  slippage_bps: int = 1200, funding_source: str = "MPC",
                  chain_id: str = "56"):
        return self.post(PRED + "/trade/get-quote",
                         walletAddress=wallet_address, tokenId=token_id, side=side,
                         amountIn=str(amount_in_wei), orderType=order_type,
                         priceLimit=price_limit, slippageBps=slippage_bps,
                         fundingSource=funding_source, chainId=chain_id)

    def place_order_bundle(self, wallet_address: str, wallet_id: str, quote_id: str,
                           order_type: str, price_limit: str = None,
                           slippage_bps: int = 1200, account_type: str = "SPOT",
                           funding_source: str = "CEX"):
        # timeInForce: MARKET→FOK, LIMIT→GTC（文档强制对应关系）
        tif = "FOK" if order_type == "MARKET" else "GTC"
        return self.post(PRED + "/trade/place-order-bundle",
                         walletAddress=wallet_address, walletId=wallet_id,
                         quoteId=quote_id, timeInForce=tif,
                         accountType=account_type, orderType=order_type,
                         priceLimit=price_limit, slippageBps=slippage_bps,
                         fundingSource=funding_source)

    def active_orders(self, wallet_address: str, **kw):
        return self.get(PRED + "/order/list", walletAddress=wallet_address, **kw)
