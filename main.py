from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.middleware("http")
async def x402_gateway_middleware(request: Request, call_next):
    if "/v1/institutional-verify" in request.url.path:
        payment_sig = request.headers.get("payment-signature") or request.headers.get("x-payment")
        if not payment_sig:
            headers = {
                "payment-required": "eyJ4NDAyVmVyc2lvbiI6MiwiaWQiOiJpbnN0aXR1dGlvbmFsLXZlcmlmeSJ9",
                "x-payment-required": "eyJ4NDAyVmVyc2lvbiI6MiwiaWQiOiJpbnN0aXR1dGlvbmFsLXZlcmlmeSJ5"
            }
            body = '{"x402Version":2,"error":"PAYMENT_REQUIRED","accepts":[{"network":"eip155:8453","amount":"50000000","payTo":"0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"}]}'
            return Response(content=body, status_code=402, media_type="application/json", headers=headers)
    
    response = await call_next(request)
    return response

@app.api_route("/v1/institutional-verify", methods=["GET", "POST", "OPTIONS"])
async def institutional_verify(request: Request):
    return {"status": "success", "verified": True}