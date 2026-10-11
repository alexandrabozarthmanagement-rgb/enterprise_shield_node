from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import base64, json

app = FastAPI(title="Enterprise Safety Shield", version="2.0.0")
NODE_OPERATOR_WALLET = "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"

class CheckReq(BaseModel):
    workflow_id: str
    payload_fingerprint: str
    check_type: str

@app.get("/.well-known/agent-card.json")
def agent_card():
    return FileResponse("agent-card.json", media_type="application/json")

@app.post("/.well-known/agent-card.json")
def agent_card_post():
    return FileResponse("agent-card.json", media_type="application/json")

@app.post("/v1/institutional-verify")
async def verify(request: Request, payload: CheckReq):
    auth_header = request.headers.get("X-Payment-Authorization") or request.headers.get("X-Payment") or request.headers.get("PAYMENT-SIGNATURE")
    challenge = {"x402Version": 2, "error": "PAYMENT_REQUIRED", "accepts": [{"network": "eip155:8453", "amount": "50000000", "payTo": NODE_OPERATOR_WALLET}]}
    
    if not auth_header:
        encoded = base64.b64encode(json.dumps(challenge).encode()).decode()
        return Response(content=json.dumps(challenge), status_code=402, headers={"PAYMENT-REQUIRED": encoded, "X-PAYMENT-REQUIRED": encoded})
    
    # Strict Production Enforcement: Validate real Base mainnet on-chain signature payload
    try:
        from x402.http import HTTPFacilitatorClient, FacilitatorConfig
        facilitator = HTTPFacilitatorClient(FacilitatorConfig(url="https://api.cdp.coinbase.com/platform/v2/x402"))
        # Verify signature against Coinbase CDP mainnet facilitator
        valid_res = await facilitator.verify(auth_header, {"network": "eip155:8453", "amount": "50000000", "payTo": NODE_OPERATOR_WALLET})
        if not valid_res.get("isValid", False):
            encoded = base64.b64encode(json.dumps(challenge).encode()).decode()
            return Response(content=json.dumps(challenge), status_code=402, headers={"PAYMENT-REQUIRED": encoded, "X-PAYMENT-REQUIRED": encoded})
    except Exception as e:
        # On any connection or verification failure, maintain strict zero-mock paywall enforcement
        encoded = base64.b64encode(json.dumps(challenge).encode()).decode()
        return Response(content=json.dumps(challenge), status_code=402, headers={"PAYMENT-REQUIRED": encoded, "X-PAYMENT-REQUIRED": encoded})

    return {"status": "SETTLED_AND_VERIFIED", "tx_auth": auth_header}
