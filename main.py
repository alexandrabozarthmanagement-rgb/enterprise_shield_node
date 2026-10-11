from fastapi import FastAPI, Request

app = FastAPI()

@app.api_route("/v1/institutional-verify", methods=["GET", "POST"])
async def institutional_verify(request: Request):
    return {
        "status": "active", 
        "message": "x402 payment gate operational",
        "network": "base",
        "payTo": "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"
    }