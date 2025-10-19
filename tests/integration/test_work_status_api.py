#!/usr/bin/env python3
"""
Test the work status API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_work_status_api():
    """Test the work status API directly"""
    
    print("📊 Testing SuperOps Work Status API")
    print("=" * 50)
    
    # API configuration from environment
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    
    if not api_key:
        print("❌ SUPEROPS_API_KEY not found in environment")
        return
    
    if not customer_subdomain:
        print("❌ SUPEROPS_CUSTOMER_SUBDOMAIN not found in environment")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print()
    
    # API endpoint and headers
    api_url = "https://api.superops.ai/msp"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=1A8E1DA0E531BF4AE8E6990443BEE32A; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL query from the curl command
    query = {
        "query": """query getWorkStatusList {
            getWorkStatusList {
                statusId
                name
                state
            }
        }""",
        "variables": {}
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Query: getWorkStatusList")
    print(f"   Fields: statusId, name, state")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps API...")
            
            async with session.post(
                api_url,
                json=query,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                print("📊 Response:")
                print("=" * 40)
                print(f"Status Code: {response.status}")
                print()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("✅ SUCCESS!")
                        print("Raw Response JSON:")
                        print(json.dumps(result, indent=2))
                        print()
                        
                        # Extract work status data
                        if result and "data" in result and result["data"] and "getWorkStatusList" in result["data"]:
                            status_list = result["data"]["getWorkStatusList"]
                            
                            print(f"📈 Results Summary:")
                            print(f"   Total Work Statuses: {len(status_list)}")
                            print()
                            
                            if status_list:
                                print("📊 Work Statuses Found:")
                                print("-" * 50)
                                
                                # Group by state for better organization
                                states = {}
                                for status in status_list:
                                    state = status.get("state", "Unknown")
                                    if state not in states:
                                        states[state] = []
                                    states[state].append(status)
                                
                                for state, statuses in states.items():
                                    print(f"\n🏷️  State: {state}")
                                    print("   " + "-" * 30)
                                    for status in statuses:
                                        status_id = status.get("statusId", "N/A")
                                        name = status.get("name", "Unknown")
                                        print(f"   • {name} (ID: {status_id})")
                                
                                print(f"\n📋 State Summary:")
                                for state, statuses in states.items():
                                    print(f"   {state}: {len(statuses)} statuses")
                                    
                            else:
                                print("⚠️  No work statuses found")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                        else:
                            print("❌ Unexpected response format")
                            print(json.dumps(result, indent=2))
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON response: {e}")
                        print(f"Raw response: {response_text}")
                        
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 SuperOps Work Status API Test")
    print("Testing the getWorkStatusList query")
    print()
    
    # Run the async test
    asyncio.run(test_work_status_api())