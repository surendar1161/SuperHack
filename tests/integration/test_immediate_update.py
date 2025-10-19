#!/usr/bin/env python3
"""
Test creating and immediately updating a timer
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_immediate_timer_update():
    """Create timer and immediately try to update it"""
    
    print("⚡ Immediate Timer Update Test")
    print("=" * 50)
    
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
    
    # Step 1: Create timer
    print("🚀 Step 1: Creating new timer...")
    
    create_mutation = {
        "query": """
            mutation ($timerEntryInput: CreateWorklogTimerEntryInput!) {
                createWorklogTimerEntry(input: $timerEntryInput) {
                    timerId
                    billable
                    type
                    notes
                    running
                    timespent
                }
            }
        """,
        "variables": {
            "timerEntryInput": {
                "billable": True,
                "notes": "Fresh timer for immediate update test",
                "type": "AUTOMATIC",
                "workItem": {
                    "workId": "6028540472074190848",
                    "module": "TICKET"
                }
            }
        }
    }
    
    timer_id = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=create_mutation, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "createWorklogTimerEntry" in result["data"]:
                        timer_entry = result["data"]["createWorklogTimerEntry"]
                        timer_id = timer_entry.get("timerId")
                        
                        print(f"✅ Timer created: {timer_id}")
                        print(f"   Running: {timer_entry.get('running')}")
                        print()
                    else:
                        print(f"❌ Failed to create timer: {result}")
                        return
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    return
                    
    except Exception as e:
        print(f"💥 Exception creating timer: {e}")
        return
    
    if not timer_id:
        print("❌ No timer ID received")
        return
    
    # Step 2: Immediately try to update notes
    print("📝 Step 2: Immediately updating notes...")
    
    update_mutation = {
        "query": """
            mutation ($updateTimerInput: UpdateWorklogTimerEntryInput!) {
                updateWorklogTimerEntry(input: $updateTimerInput) {
                    timerId
                    billable
                    type
                    notes
                    running
                    timespent
                }
            }
        """,
        "variables": {
            "updateTimerInput": {
                "timerId": timer_id,
                "notes": "UPDATED: Notes changed immediately after creation"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=update_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Update Status: {response.status}")
                print(f"Update Response: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "errors" in result:
                        print("❌ Update failed with errors:")
                        for error in result["errors"]:
                            print(f"   - {error.get('message', error)}")
                    
                    if "data" in result and result["data"] and "updateWorklogTimerEntry" in result["data"]:
                        timer_data = result["data"]["updateWorklogTimerEntry"]
                        if timer_data:
                            print("✅ Update successful!")
                            print(f"   Updated Notes: {timer_data.get('notes')}")
                        else:
                            print("❌ updateWorklogTimerEntry returned null")
                    else:
                        print("❌ No valid data in response")
                        
    except Exception as e:
        print(f"💥 Exception updating timer: {e}")
    
    print()
    print("🔍 Analysis:")
    print("-" * 20)
    print("If the update fails immediately after creation, it suggests:")
    print("1. The updateWorklogTimerEntry mutation might not be the correct one")
    print("2. There might be additional required fields")
    print("3. The timer might need to be in a specific state to be updated")
    print("4. There might be permission issues with the update operation")

if __name__ == "__main__":
    asyncio.run(test_immediate_timer_update())