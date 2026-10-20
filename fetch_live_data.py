import httpx 
import asyncio 
 
async def main(): 
    url = "https://enterprise-shield-node.onrender.com/v1/institutional-verify" 
    async with httpx.AsyncClient() as client: 
        print("[*] Fetching current public web data feed...") 
        # Fetching live public data payload 
        public_res = httpx.get("https://api.duckduckgo.com/?q=Base+blockchain+USDC+volume&format=json") 
        print("[+] Public data retrieved successfully.") 
        print("[*] Submitting verification request to node...") 
        res = await client.post(url, json={"agent_id": "autonomous-live-runner", "data_feed": public_res.status_code}) 
        print(f"Response Status: HTTP {res.status_code}") 
 
if __name__ == "__main__": 
    asyncio.run(main()) 
