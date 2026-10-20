import httpx

url = "https://x402-list.com/api/v1/submit"
payload = {
    "url": "https://enterprise-shield-node.onrender.com/v1/institutional-verify",
    "name": "Enterprise Shield Node",
    "description": "Gated institutional verification endpoint requiring 50 USDC on Base.",
    "email": "alexandrabozarthmanagement@gmail.com",
    "website_url": "https://enterprise-shield-node.onrender.com",
    "category": "verification",
    "endpoints": ["/v1/institutional-verify"]
}

res = httpx.post(url, json=payload)
print("Status Code:", res.status_code)
print("Response:", res.text)