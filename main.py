from fastapi import FastAPI, Request, Response
import base64
import json

app = FastAPI()

PAYMENT_REQ_DATA = {
    "x402Version": 2,
    "error": "PAYMENT_REQUIRED",
    "resource": {
        "url": "https://enterprise-shield-node.onrender.com/v1/institutional-verify",
        "description": "Institutional verification API endpoint gated by x402 tollbooth",
        "mimeType": "application/json"
    },
    "accepts": [{
        "network": "eip155:8453",
        "scheme": "exact",
        "amount": "50000000",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "payTo": "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17",
        "maxTimeoutSeconds": 60
    }],
    "extensions": {
        "bazaar": {
            "info": {
                "title": "Institutional Verification API",
                "description": "Gated verification endpoint for AI agents requiring 50 USDC payment on Base.",
                "input": {
                    "type": "object",
                    "method": "POST",
                    "params": {}
                },
                "output": {
                    "type": "object",
                    "example": {
                        "status": "success",
                        "verified": True
                    }
                }
            },
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "verified": {"type": "boolean"}
                },
                "required": ["status", "verified"]
            }
        }
    }
}

PAYMENT_REQ_JSON_STR = json.dumps(PAYMENT_REQ_DATA, separators=(",", ":"))
ENCODED_PAYMENT_HEADER = base64.b64encode(PAYMENT_REQ_JSON_STR.encode("utf-8")).decode("utf-8")

@app.api_route("/v1/institutional-verify", methods=["GET", "POST", "OPTIONS"])
async def institutional_verify(request: Request):
    payment_sig = request.headers.get("payment-signature") or request.headers.get("x-payment")
    
    if not payment_sig:
        headers = {
            "Payment-Required": ENCODED_PAYMENT_HEADER,
            "x-payment-required": ENCODED_PAYMENT_HEADER,
            "Access-Control-Expose-Headers": "Payment-Required, x-payment-required",
            "Access-Control-Allow-Origin": "*"
        }
        return Response(
            content=PAYMENT_REQ_JSON_STR,
            status_code=402,
            media_type="application/json",
            headers=headers
        )

    return {"status": "success", "verified": True}