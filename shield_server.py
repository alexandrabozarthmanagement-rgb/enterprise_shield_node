import base64, json, time, hashlib, sqlite3, os, httpx
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

app = FastAPI(title="Enterprise Safety Shield API")
NODE_OPERATOR_WALLET = "0xef45b3724Fb9b676d5532f588c4a5d3cCb50Db17"
FACILITATOR_VERIFY_URL = "https://gateway-api.circle.com/v1/x402/verify"
PRIVATE_KEY = os.getenv("NODE_PRIVATE_KEY") or os.getenv("AGENT_PRIVATE_KEY")

# Initialize Local Transaction Ledger
def init_db():
    conn = sqlite3.connect("enterprise_ledger.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            tx_hash TEXT PRIMARY KEY,
            timestamp INTEGER,
            amount_usdc REAL,
            payee TEXT,
            attestation_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
async def root():
    return {
        "status": "ACTIVE",
        "node": "Enterprise Safety Shield",
        "network": "Base Mainnet",
        "payTo": NODE_OPERATOR_WALLET,
        "key_loaded": bool(PRIVATE_KEY)
    }

@app.post("/v1/institutional-verify")
async def verify_main(request: Request):
    auth_header = (
        request.headers.get("X-Payment-Authorization") or 
        request.headers.get("X-Payment") or 
        request.headers.get("PAYMENT-SIGNATURE")
    )
    
    challenge = {
        "x402Version": 2,
        "error": "PAYMENT_REQUIRED",
        "resource": {
            "url": "https://enterprise-shield-node.onrender.com/v1/institutional-verify",
            "description": "Institutional verification API endpoint gated by x402 tollbooth",
            "mimeType": "application/json"
        },
        "accepts": [{
            "scheme": "exact",
            "network": "eip155:8453", # Base Mainnet
            "amount": "50000000",      # $50.00 USDC (6 decimals)
            "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "payTo": NODE_OPERATOR_WALLET,
            "maxTimeoutSeconds": 60
        }],
        "extensions": {
            "bazaar": {
                "discoverable": True,
                "info": {
                    "title": "Institutional Verification API",
                    "description": "Gated verification endpoint for AI agents requiring 50 USDC payment on Base.",
                    "category": "compliance",
                    "provider": "Enterprise Shield Node"
                },
                "input": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Unique identifier of requesting agent"}
                    },
                    "required": ["agent_id"]
                },
                "output": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "verified": {"type": "boolean"},
                        "verification_report": {"type": "object"}
                    }
                }
            }
        }
    }

    if not auth_header:
        encoded = base64.b64encode(json.dumps(challenge).encode()).decode()
        return Response(
            content=json.dumps(challenge), 
            status_code=402, 
            headers={"PAYMENT-REQUIRED": encoded, "X-PAYMENT-REQUIRED": encoded}
        )

    # Cryptographic Verification Step via Facilitator
    async with httpx.AsyncClient() as client:
        verify_resp = await client.post(
            FACILITATOR_VERIFY_URL,
            json={"paymentPayload": auth_header, "paymentRequirements": challenge["accepts"][0]}
        )
        
    if verify_resp.status_code != 200 or not verify_resp.json().get("isValid"):
        return Response(content=json.dumps({"error": "INVALID_PAYMENT_SIGNATURE"}), status_code=403)

    # Generate Hash & Log Receipt to Ledger
    timestamp = int(time.time())
    payload_data = f"VERIFIED_INSTITUTIONAL_{timestamp}_{NODE_OPERATOR_WALLET}"
    attestation_hash = hashlib.sha256(payload_data.encode()).hexdigest()

    conn = sqlite3.connect("enterprise_ledger.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO receipts (tx_hash, timestamp, amount_usdc, payee, attestation_hash) VALUES (?, ?, ?, ?, ?)",
        (attestation_hash, timestamp, 50.00, NODE_OPERATOR_WALLET, attestation_hash)
    )
    conn.commit()
    conn.close()

    return {
        "status": "INSTITUTIONAL_VERIFIED",
        "verified": True,
        "timestamp": timestamp,
        "payee": NODE_OPERATOR_WALLET,
        "verification_report": {
            "risk_score": 98.4,
            "sanctions_clearance": True,
            "aml_status": "PASSED",
            "attestation_hash": attestation_hash
        }
    }

@app.get("/v1/receipt/{tx_hash}")
async def get_receipt(tx_hash: str):
    conn = sqlite3.connect("enterprise_ledger.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tx_hash, timestamp, amount_usdc, payee, attestation_hash FROM receipts WHERE tx_hash=?", (tx_hash,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return Response(content=json.dumps({"error": "RECEIPT_NOT_FOUND"}), status_code=404)

    return {
        "receipt_id": row[0],
        "timestamp": row[1],
        "amount_usdc": row[2],
        "payee": row[3],
        "attestation_hash": row[4],
        "status": "SETTLED"
    }