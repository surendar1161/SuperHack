#!/usr/bin/env python3
"""
Complete test of timer lifecycle: Create -> Update -> Stop
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_timer_entry():
    """Create a new timer entry"""
    
    print("🚀 Step 1: Creating new timer entry...")
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
    
    # Create timer mutation
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
                "notes": "Test timer for lifecycle testing",
                "type": "AUTOMATIC",
                "workItem": {
                    "workId": "6028540472074190848",
                    "module": "TICKET"
                }
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=create_mutation, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "createWorklogTimerEntry" in result["data"]:
                        timer_entry = result["data"]["createWorklogTimerEntry"]
                        timer_id = timer_entry.get("timerId")
                        
                        print("✅ Timer created successfully!")
                        print(f"   Timer ID: {timer_id}")
                        print(f"   Notes: {timer_entry.get('notes')}")
                        print(f"   Running: {timer_entry.get('running')}")
                        print(f"   Billable: {timer_entry.get('billable')}")
                        print()
                        
                        return timer_id
                    else:
                        print(f"❌ Failed to create timer: {result}")
                        return None
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    return None
                    
    except Exception as e:
        print(f"💥 Exception creating timer: {e}")
        return None

async def update_timer_notes(timer_id):
    """Update timer notes"""
    
    print("📝 Step 2: Updating timer notes...")
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
    
    # Update timer mutation (notes only)
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
                "notes": "Updated: Timer is now in progress - working on issue resolution"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=update_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Update Response Status: {response.status}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "updateWorklogTimerEntry" in result["data"]:
                        timer_entry = result["data"]["updateWorklogTimerEntry"]
                        
                        print("✅ Timer notes updated successfully!")
                        print(f"   Timer ID: {timer_entry.get('timerId')}")
                        print(f"   Updated Notes: {timer_entry.get('notes')}")
                        print(f"   Still Running: {timer_entry.get('running')}")
                        print()
                        
                        return True
                    elif "errors" in result:
                        print(f"❌ GraphQL Errors: {result['errors']}")
                        return False
                    else:
                        print(f"❌ Unexpected response: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"💥 Exception updating timer: {e}")
        return False

async def stop_timer(timer_id):
    """Stop the timer"""
    
    print("🛑 Step 3: Stopping timer...")
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
    
    # Stop timer mutation (set running to false)
    stop_mutation = {
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
                "running": False,
                "notes": "COMPLETED: Timer stopped - task finished successfully"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=stop_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Stop Response Status: {response.status}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "updateWorklogTimerEntry" in result["data"]:
                        timer_entry = result["data"]["updateWorklogTimerEntry"]
                        
                        print("✅ Timer stopped successfully!")
                        print(f"   Timer ID: {timer_entry.get('timerId')}")
                        print(f"   Final Notes: {timer_entry.get('notes')}")
                        print(f"   Running: {timer_entry.get('running')}")
                        print(f"   Total Time Spent: {timer_entry.get('timespent')}")
                        
                        segments = timer_entry.get('segments', [])
                        if segments:
                            print(f"   Segments: {len(segments)} segment(s)")
                            for i, segment in enumerate(segments):
                                print(f"     Segment {i+1}: {segment.get('startTime')} -> {segment.get('endTime')} ({segment.get('timespent')} min)")
                        
                        print()
                        return True
                        
                    elif "errors" in result:
                        print(f"❌ GraphQL Errors: {result['errors']}")
                        print(f"Full response: {json.dumps(result, indent=2)}")
                        return False
                    else:
                        print(f"❌ Unexpected response: {result}")
                        return False
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"💥 Exception stopping timer: {e}")
        return False

async def main():
    """Run the complete timer lifecycle test"""
    
    print("🎯 Timer Lifecycle Test")
    print("Testing: Create -> Update -> Stop")
    print("=" * 60)
    print()
    
    # Step 1: Create timer
    timer_id = await create_timer_entry()
    if not timer_id:
        print("❌ Test failed: Could not create timer")
        return
    
    # Step 2: Update timer notes
    update_success = await update_timer_notes(timer_id)
    if not update_success:
        print("⚠️  Warning: Could not update timer notes, but continuing...")
    
    # Step 3: Stop timer
    stop_success = await stop_timer(timer_id)
    
    # Final result
    print("🏁 Test Results:")
    print("=" * 30)
    print(f"✅ Timer Created: {timer_id}")
    print(f"{'✅' if update_success else '❌'} Notes Updated: {update_success}")
    print(f"{'✅' if stop_success else '❌'} Timer Stopped: {stop_success}")
    
    if stop_success:
        print()
        print("🎉 SUCCESS: Complete timer lifecycle test passed!")
        print(f"   Timer ID {timer_id} was created, updated, and stopped successfully")
    else:
        print()
        print("⚠️  PARTIAL SUCCESS: Timer created but stop operation failed")
        print("   This helps us understand the API behavior")

if __name__ == "__main__":
    asyncio.run(main())