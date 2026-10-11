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

PAYMENT_REQ_JSON_STR = json.dumps(PAYMENT_REQ_DATA, separators=(",", ":"))
ENCODED_PAYMENT_HEADER = base64.b6aencode(PAYMENT_REQ_JSON_STR.encode("utf-8")).decode("utf-8")

async def app(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")
        if path == "/v1/institutional-verify":
            # Check headers for payment signature
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
            payment_sig = headers.get("payment-signature") or headers.get("x-payment")
            
            if not payment_sig:
                body_bytes = PAYMENT_REQ_JSON_STR.encode("utf-8")
                # Send raw ASGI response with exact uppercase/hyphenated header casing
                await send({
                    "type": "http.response.start",
                    "status": 402,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"PAYMENT-REQUIRED", ENCODED_PAYMENT_HEADER.encode("latin-1")),
                        (b"x-payment-required", ENCODED_PAYMENT_HEADER.encode("latin-1")),
                        (b"access-control-allow-origin", b"*"),
                        (b"access-control-expose-headers", b"PAYMENT-REQUIRED, x-payment-required"),
                        (b"content-length", str(len(body_bytes)).encode("latin-1")),
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": body_bytes,
                })
                return

        # Default success response for paid requests
        body_bytes = b'{"status":"success","verified":true}'
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json"),
                (b"access-control-allow-origin", b"*"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body_bytes,
        })