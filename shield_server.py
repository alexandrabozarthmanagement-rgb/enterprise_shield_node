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
@app.post("/v1/institutional-verify") 
async def verify(request: Request, payload: CheckReq): 
    if not request.headers.get("X-Payment-Authorization"): 
        challenge = {"x402Version": 2, "error": "PAYMENT_REQUIRED", "accepts": [{"network": "eip155:8453", "amount": "50000000", "payTo": NODE_OPERATOR_WALLET}]} 
        return Response(content=json.dumps(challenge), status_code=402, headers={"PAYMENT-REQUIRED": base64.b64encode(json.dumps(challenge).encode()).decode()}) 
    return {"status": "SETTLED_AND_VERIFIED"} 
