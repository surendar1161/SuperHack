#!/usr/bin/env python3
"""
Test the worklog entries API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_worklog_entries_api():
    """Test the worklog entries API directly"""
    
    print("📝 Testing SuperOps Worklog Entries API")
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
    
    # API endpoint and headers (MSP API for worklog entries)
    api_url = "https://api.superops.ai/msp"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Test data based on the curl command provided
    current_time = datetime.now()
    bill_date_time = current_time.isoformat()
    
    # GraphQL mutation (from the curl command provided)
    mutation = {
        "query": """
            mutation createWorklogEntries($input: [CreateWorklogEntryInput!]!) {
                createWorklogEntries(input: $input) {
                    itemId
                    status
                    serviceItem
                    billable
                    afterHours
                    qty
                    unitPrice
                    billDateTime
                    technician
                    notes
                    workItem
                }
            }
        """,
        "variables": {
            "input": [
                {
                    "billable": True,
                    "afterHours": True,
                    "qty": "4",
                    "unitPrice": "50",
                    "billDateTime": bill_date_time,
                    "notes": "Test worklog entry from API - troubleshooting network issues",
                    "workItem": {
                        "workId": 6028540472074190848,  # Using the ticket ID from previous tests
                        "module": "TICKET"  # Changed from PROJECT to TICKET
                    }
                }
            ]
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Mutation: createWorklogEntries")
    print(f"   Work Item: Ticket ID 6028540472074190848")
    print(f"   Hours: 4 hours @ $50/hour")
    print(f"   Billable: Yes")
    print(f"   After Hours: Yes")
    print(f"   Bill Date: {bill_date_time}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps MSP API...")
            
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
                print()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("Response JSON:")
                        print(json.dumps(result, indent=2))
                        print()
                        
                        # Extract worklog data
                        if "data" in result and "createWorklogEntries" in result["data"]:
                            worklog_entries = result["data"]["createWorklogEntries"]
                            
                            if worklog_entries:
                                print("✅ SUCCESS!")
                                print(f"📈 Created {len(worklog_entries)} worklog entries:")
                                print("-" * 40)
                                
                                for i, entry in enumerate(worklog_entries, 1):
                                    item_id = entry.get("itemId", "Unknown")
                                    status = entry.get("status", "Unknown")
                                    billable = entry.get("billable", False)
                                    qty = entry.get("qty", "0")
                                    unit_price = entry.get("unitPrice", "0")
                                    notes = entry.get("notes", "No notes")
                                    
                                    print(f"   Entry {i}:")
                                    print(f"     Item ID: {item_id}")
                                    print(f"     Status: {status}")
                                    print(f"     Billable: {billable}")
                                    print(f"     Quantity: {qty} hours")
                                    print(f"     Unit Price: ${unit_price}")
                                    print(f"     Total: ${float(qty) * float(unit_price)}")
                                    print(f"     Notes: {notes}")
                                    print()
                            else:
                                print("⚠️  No worklog entries returned")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                        else:
                            print("❌ Unexpected response format")
                        
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

async def test_multiple_worklog_entries():
    """Test creating multiple worklog entries at once"""
    
    print("\n" + "=" * 60)
    print("📝 Testing Multiple Worklog Entries")
    print("=" * 60)
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    api_url = "https://api.superops.ai/msp"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Create multiple entries for different types of work
    current_time = datetime.now()
    
    entries = [
        {
            "billable": True,
            "afterHours": False,
            "qty": "2",
            "unitPrice": "75",
            "billDateTime": current_time.isoformat(),
            "notes": "Initial troubleshooting and diagnosis",
            "workItem": {
                "workId": 6028540472074190848,
                "module": "TICKET"
            }
        },
        {
            "billable": True,
            "afterHours": False,
            "qty": "1.5",
            "unitPrice": "75",
            "billDateTime": (current_time + timedelta(hours=2)).isoformat(),
            "notes": "Implementation of solution and testing",
            "workItem": {
                "workId": 6028540472074190848,
                "module": "TICKET"
            }
        },
        {
            "billable": False,
            "afterHours": False,
            "qty": "0.5",
            "unitPrice": "0",
            "billDateTime": (current_time + timedelta(hours=4)).isoformat(),
            "notes": "Documentation and knowledge base update",
            "workItem": {
                "workId": 6028540472074190848,
                "module": "TICKET"
            }
        }
    ]
    
    mutation = {
        "query": """
            mutation createWorklogEntries($input: [CreateWorklogEntryInput!]!) {
                createWorklogEntries(input: $input) {
                    itemId
                    status
                    billable
                    qty
                    unitPrice
                    notes
                }
            }
        """,
        "variables": {
            "input": entries
        }
    }
    
    print(f"📋 Creating {len(entries)} worklog entries:")
    for i, entry in enumerate(entries, 1):
        billable_status = "Billable" if entry["billable"] else "Non-billable"
        total = float(entry["qty"]) * float(entry["unitPrice"])
        print(f"   {i}. {entry['qty']}h @ ${entry['unitPrice']}/h = ${total} ({billable_status})")
        print(f"      Notes: {entry['notes']}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=mutation, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "createWorklogEntries" in result["data"]:
                        worklog_entries = result["data"]["createWorklogEntries"]
                        
                        if worklog_entries:
                            print("✅ Multiple entries created successfully!")
                            total_billable = sum(
                                float(entry.get("qty", 0)) * float(entry.get("unitPrice", 0))
                                for entry in worklog_entries
                                if entry.get("billable", False)
                            )
                            print(f"💰 Total billable amount: ${total_billable}")
                        else:
                            print("⚠️  No entries returned")
                    else:
                        print("❌ Failed to create multiple entries")
                        print(json.dumps(result, indent=2))
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    print("🎯 SuperOps Worklog Entries API Test")
    print("Testing the createWorklogEntries mutation")
    print()
    
    # Run the async tests
    asyncio.run(test_worklog_entries_api())
    asyncio.run(test_multiple_worklog_entries())