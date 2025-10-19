#!/usr/bin/env python3
"""
Detailed test of timer update API to see exact responses
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_timer_update():
    """Test updating the timer we just created"""
    
    print("🔍 Detailed Timer Update Test")
    print("=" * 50)
    
    # Use the timer ID from the previous test
    timer_id = "553751328387428352"
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    api_url = "https://api.superops.ai/it"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print(f"🎯 Testing with Timer ID: {timer_id}")
    print()
    
    # Test 1: Update notes only
    print("📝 Test 1: Update notes only")
    print("-" * 30)
    
    update_notes_mutation = {
        "query": """
            mutation ($updateTimerInput: UpdateWorklogTimerEntryInput!) {
                updateWorklogTimerEntry(input: $updateTimerInput) {
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
            "updateTimerInput": {
                "timerId": timer_id,
                "notes": "Updated notes: Working on detailed testing"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=update_notes_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Status: {response.status}")
                print(f"Raw Response: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("Parsed JSON:")
                        print(json.dumps(result, indent=2))
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                else:
                    print(f"HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"Exception: {e}")
    
    print()
    print("=" * 50)
    
    # Test 2: Stop timer (set running to false)
    print("🛑 Test 2: Stop timer (running = false)")
    print("-" * 40)
    
    stop_timer_mutation = {
        "query": """
            mutation ($updateTimerInput: UpdateWorklogTimerEntryInput!) {
                updateWorklogTimerEntry(input: $updateTimerInput) {
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
            "updateTimerInput": {
                "timerId": timer_id,
                "running": False
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=stop_timer_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Status: {response.status}")
                print(f"Raw Response: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("Parsed JSON:")
                        print(json.dumps(result, indent=2))
                        
                        # Check if the update was successful
                        if "data" in result:
                            if result["data"] is None:
                                print("⚠️  Data is null - this might indicate the timer doesn't exist or can't be updated")
                            elif "updateWorklogTimerEntry" in result["data"]:
                                timer_data = result["data"]["updateWorklogTimerEntry"]
                                if timer_data is None:
                                    print("⚠️  updateWorklogTimerEntry returned null")
                                else:
                                    print(f"✅ Timer updated successfully!")
                                    print(f"   Running: {timer_data.get('running')}")
                                    print(f"   Notes: {timer_data.get('notes')}")
                        
                        if "errors" in result:
                            print("❌ GraphQL Errors found:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                                
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                else:
                    print(f"HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_timer_update())