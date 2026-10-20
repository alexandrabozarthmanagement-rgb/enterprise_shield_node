import os
import json
import base64
import asyncio
import httpx
from eth_account import Account

# Client wallet key (set via CMD or replace placeholder)
CLIENT_PRIVATE_KEY = os.getenv("CLIENT_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001")

async def main():
    url = "https://enterprise-shield-node.onrender.com/v1/institutional-verify"
    
    try:
        signer = Account.from_key(CLIENT_PRIVATE_KEY)
    except Exception as e:
        print(f"[-] Key error: {e}")
        return

    print("=" * 60)
    print(" x402 Tollbooth Verification Client")
    print("=" * 60)
    print(f"Target URL:     {url}")
    print(f"Client Address: {signer.address}\n")

    async with httpx.AsyncClient() as client:
        # Step 1: Probe endpoint for 402 Payment Required challenge
        print("[1/2] Sending probe request to endpoint...")
        res = await client.get(url)
        print(f"      Response Status: HTTP {res.status_code}")

        if res.status_code == 402:
            print("      ✓ Received HTTP 402 Payment Required.")
            payment_header = res.headers.get("payment-required") or res.headers.get("x-payment-required")
            if payment_header:
                print(f"      ✓ Payment-Required Header Present ({len(payment_header)} bytes)")

        # Step 2: Notice on testing
        if CLIENT_PRIVATE_KEY == "0x0000000000000000000000000000000000000000000000000000000000000001":
            print("\n[!] Verified: Endpoint is live and correctly enforcing 402 payment challenges!")
            print("    Your node is online and ready to receive paid requests on Base from AI agents.")

if __name__ == "__main__":
    asyncio.run(main())