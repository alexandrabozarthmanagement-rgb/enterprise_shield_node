import asyncio 
import os 
from x402 import x402Client 
from x402.mechanisms.evm.exact import ExactEvmScheme 
from eth_account import Account 
 
async def main(): 
    url = "https://enterprise-shield-node.onrender.com/v1/institutional-verify" 
    private_key = os.getenv("CLIENT_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001") 
    signer = Account.from_key(private_key) 
    client = x402Client() 
    client.register("eip155:*", ExactEvmScheme(signer=signer)) 
    print("[*] Initializing live x402 payment sequence against node...") 
 
if __name__ == "__main__": 
    asyncio.run(main()) 
