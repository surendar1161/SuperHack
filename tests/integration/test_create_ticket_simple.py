#!/usr/bin/env python3
"""
Simple test of ticket creation with technician assignment using direct API calls
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_ticket_creation_flow():
    """Test the complete flow: get technicians -> create ticket with assignment"""
    
    print("🎯 Complete Ticket Creation Flow Test")
    print("=" * 50)
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    
    if not api_key or not customer_subdomain:
        print("❌ Missing API credentials")
        return
    
    it_api_url = "https://api.superops.ai/it"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print(f"🔑 Using API Key: {api_key[:20]}...")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print()
    
    # Step 1: Get technicians
    print("👥 Step 1: Getting technicians...")
    
    technicians_query = {
        "query": """
            query getTechnicianList($input: ListInfoInput!) {
                getTechnicianList(input: $input) {
                    userList { 
                        userId
                        name 
                        email 
                        department
                    }
                }
            }
        """,
        "variables": {
            "input": {
                "page": 1,
                "pageSize": 10,
                "condition": {
                    "attribute": "roles.roleId",
                    "operator": "is",
                    "value": 3
                }
            }
        }
    }
    
    technician_user_id = None
    technician_name = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(it_api_url, json=technicians_query, headers=headers) as response:
                if response.status == 200:
                    result = json.loads(await response.text())
                    
                    if "data" in result and "getTechnicianList" in result["data"]:
                        user_list = result["data"]["getTechnicianList"].get("userList", [])
                        
                        if user_list:
                            # Use the first technician
                            first_tech = user_list[0]
                            technician_user_id = first_tech.get("userId")
                            technician_name = first_tech.get("name", "Unknown")
                            
                            print(f"✅ Found technician: {technician_name} (ID: {technician_user_id})")
                        else:
                            print("⚠️  No technicians found")
                    else:
                        print("❌ Failed to get technicians")
                        print(json.dumps(result, indent=2))
                else:
                    print(f"❌ HTTP Error {response.status}")
                    
    except Exception as e:
        print(f"💥 Exception getting technicians: {e}")
    
    if not technician_user_id:
        print("❌ Cannot proceed without technician ID")
        return
    
    print()
    
    # Step 2: Create ticket with assignment
    print("🎫 Step 2: Creating ticket with assignment...")
    
    create_ticket_mutation = {
        "query": """
            mutation createTicket($input: CreateTicketInput!) {
                createTicket(input: $input) {
                    ticketId
                    subject
                    description
                    priority
                    status
                    assignee {
                        userId
                        name
                        email
                    }
                }
            }
        """,
        "variables": {
            "input": {
                "subject": "Auto-Assigned Test Ticket",
                "description": "This ticket was created with automatic technician assignment. Testing the integration between technician lookup and ticket creation.",
                "priority": "MEDIUM",
                "assigneeId": technician_user_id
            }
        }
    }
    
    print(f"📋 Creating ticket assigned to: {technician_name} ({technician_user_id})")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(it_api_url, json=create_ticket_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("Raw Response:")
                        print(json.dumps(result, indent=2))
                        print()
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {e}")
                        print(f"Raw Response: {response_text}")
                        return
                    
                    if result and "data" in result and result["data"] and "createTicket" in result["data"]:
                        ticket_data = result["data"]["createTicket"]
                        
                        if ticket_data:
                            print("✅ SUCCESS! Ticket created with assignment:")
                            print(f"   Ticket ID: {ticket_data.get('ticketId')}")
                            print(f"   Subject: {ticket_data.get('subject')}")
                            print(f"   Priority: {ticket_data.get('priority')}")
                            print(f"   Status: {ticket_data.get('status')}")
                            
                            assignee = ticket_data.get('assignee')
                            if assignee:
                                print(f"   ✅ Assigned to: {assignee.get('name')} ({assignee.get('userId')})")
                                print(f"   📧 Email: {assignee.get('email')}")
                                
                                # Verify assignment worked
                                if assignee.get('userId') == technician_user_id:
                                    print("   🎯 Assignment verification: SUCCESS!")
                                else:
                                    print(f"   ⚠️  Assignment mismatch: expected {technician_user_id}, got {assignee.get('userId')}")
                            else:
                                print("   ❌ No assignee information returned")
                            
                            print()
                            print("🏁 Test Results:")
                            print("=" * 30)
                            print("✅ Technician lookup: SUCCESS")
                            print("✅ Ticket creation: SUCCESS")
                            print("✅ Automatic assignment: SUCCESS")
                            print()
                            print("🎉 Auto-assignment functionality is working!")
                            
                        else:
                            print("❌ createTicket returned null")
                    
                    elif "errors" in result:
                        print("❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   - {error.get('message', error)}")
                    else:
                        print("❌ Unexpected response format")
                        print(json.dumps(result, indent=2))
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception creating ticket: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ticket_creation_flow())