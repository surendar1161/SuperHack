#!/usr/bin/env python3
"""
Direct test of SuperOps API for creating timer entries
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_superops_timer_api():
    """Test SuperOps timer creation API directly"""
    
    print("🧪 Testing SuperOps Timer Creation API...")
    print("=" * 60)
    
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
    api_url = "https://api.superops.ai/it"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL mutation
    mutation = {
        "query": """
            mutation ($timerEntryInput: CreateWorklogTimerEntryInput!) {
                createWorklogTimerEntry(input: $timerEntryInput) {
                    timerId
                    billable
                    type
                    notes
                    running
                    timespent
                    segments { 
                        segmentId 
                        startTime 
                        endTime 
                        timespent 
                        afterHours 
                    }
                }
            }
        """,
        "variables": {
            "timerEntryInput": {
                "billable": True,
                "notes": "i am agent",  # As requested
                "type": "AUTOMATIC",
                "workItem": {
                    "workId": "6028540472074190848",
                    "module": "TICKET"
                }
            }
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Ticket ID: 6028540472074190848")
    print(f"   Notes: 'i am agent'")
    print(f"   Billable: True")
    print(f"   Type: AUTOMATIC")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps API...")
            
            async with session.post(
                api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                print("📊 Response:")
                print("=" * 40)
                print(f"Status Code: {response.status}")
                print(f"Response Headers: {dict(response.headers)}")
                print()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("✅ SUCCESS!")
                        print("Response JSON:")
                        print(json.dumps(result, indent=2))
                        
                        # Extract timer info if available
                        if "data" in result and "createWorklogTimerEntry" in result["data"]:
                            timer_entry = result["data"]["createWorklogTimerEntry"]
                            print()
                            print("🎯 Timer Entry Created:")
                            print(f"   Timer ID: {timer_entry.get('timerId')}")
                            print(f"   Notes: {timer_entry.get('notes')}")
                            print(f"   Billable: {timer_entry.get('billable')}")
                            print(f"   Running: {timer_entry.get('running')}")
                            print(f"   Time Spent: {timer_entry.get('timespent')}")
                        
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
    print("🎯 SuperOps Timer API Direct Test")
    print("Creating timer with 'i am agent' as notes")
    print()
    
    # Run the async test
    asyncio.run(test_superops_timer_api())