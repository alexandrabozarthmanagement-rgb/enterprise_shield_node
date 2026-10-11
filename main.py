from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

async def institutional_verify(request):
    payment_sig = request.headers.get("payment-signature") or request.headers.get("x-payment")
    
    if not payment_sig:
        headers = {
            "payment-required": "eyJ4NDAyVmVyc2lvbiI6MiwiaWQiOiJpbnN0aXR1dGlvbmFsLXZlcmlmeSJ5",
            "x-payment-required": "eyJ4NDAyVmVyc2lvbiI6MiwiaWQiOiJpbnN0aXR1dGlvbmFsLXZlcmlmeSJ5"
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
        return JSONResponse(body, status_code=402, headers=headers)
        
    return JSONResponse({"status": "success", "verified": True})

routes = [
    Route("/v1/institutional-verify", institutional_verify, methods=["GET", "POST", "OPTIONS"])
]

app = Starlette(routes=routes)