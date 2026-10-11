from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import base64
import json

PAYMENT_REQ_DATA = {
    "x402Version": 2,
    "error": "PAYMENT_REQUIRED",
    "accepts": [{
        "network": "eip155:8453",
        "amount": "50000000",
        "payTo": "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"
    }]
}

PAYMENT_REQ_JSON_STR = json.dumps(PAYMENT_REQ_DATA)
ENCODED_PAYMENT_HEADER = base64.b6aencode(PAYMENT_REQ_JSON_STR.encode("utf-8")).decode("utf-8")

class X402Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if "/v1/institutional-verify" in request.url.path:
            payment_sig = request.headers.get("payment-signature") or request.headers.get("x-payment")
            if not payment_sig:
                headers = {
                    "payment-required": ENCODED_PAYMENT_HEADER,
                    "x-payment-required": ENCODED_PAYMENT_HEADER
                }
                return JSONResponse(PAYMENT_REQ_DATA, status_code=402, headers=headers)
        return await call_next(request)

async def institutional_verify(request):
    return JSONResponse({"status": "success", "verified": True})

routes = [
    Route("/v1/institutional-verify", institutional_verify, methods=["GET", "POST", "OPTIONS"])
]

middleware = [
    Middleware(X402Middleware)
]

app = Starlette(routes=routes, middleware=middleware)