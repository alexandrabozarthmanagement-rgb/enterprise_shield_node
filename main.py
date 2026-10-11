from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow cross-origin requests from marketplace validators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PAYMENT_REQUIRED_HEADER = "eyJ4NDAyVmVyc2lvbiI6MiwiaWQiOiJpbnN0aXR1dGlvbmFsLXZlcmlmeSJ9"

@app.api_route("/v1/institutional-verify", methods=["GET", "POST", "OPTIONS"])
async def institutional_verify(request: Request):
    # Check if a valid x402 payment signature header is present
    payment_sig = request.headers.get("payment-signature") or request.headers.get("x-payment")
    
    if not payment_sig:
        # Issue 402 Payment Required challenge for unauthenticated GET/POST requests
        headers = {
            "payment-required": PAYMENT_REQUIRED_HEADER,
            "x-payment-required": PAYMENT_REQUIRED_HEADER,
            "Access-Control-Expose-Headers": "payment-required, x-payment-required"
        }
        body = {
            "x402Version": 2,
            "error": "PAYMENT_REQUIRED",
            "accepts": [{
                "network": "eip155:8453",
                "amount": "50000000",
                "payTo": "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"
            }]
        }
        return Response(
            content=str(body).replace("'", '"'),
            status_code=402,
            media_type="application/json",
            headers=headers
        )

    # Process paid request
    return {
        "status": "success",
        "verified": True,
        "message": "Institutional verification cleared."
    }