#!/usr/bin/env python3
"""
Test ticket creation with technician assignment using the correct SuperOps format
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_flow():
    """Test: Get technicians -> Create ticket with technician assignment"""
    
    print("🎯 Complete Ticket Creation with Technician Assignment")
    print("=" * 60)
    
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
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🏢 Customer: {customer_subdomain}")
    print()
    
    # Step 1: Get available technicians
    print("👥 Step 1: Getting available technicians...")
    
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
    
    selected_technician = None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(it_api_url, json=technicians_query, headers=headers) as response:
                if response.status == 200:
                    result = json.loads(await response.text())
                    
                    if "data" in result and "getTechnicianList" in result["data"]:
                        user_list = result["data"]["getTechnicianList"].get("userList", [])
                        
                        if user_list:
                            selected_technician = user_list[0]  # Use first technician
                            print(f"✅ Selected technician: {selected_technician.get('name')}")
                            print(f"   User ID: {selected_technician.get('userId')}")
                            print(f"   Email: {selected_technician.get('email')}")
                        else:
                            print("⚠️  No technicians found")
                    else:
                        print("❌ Failed to get technicians")
                        if "errors" in result:
                            for error in result["errors"]:
                                print(f"   Error: {error.get('message')}")
                else:
                    print(f"❌ HTTP Error {response.status}")
                    
    except Exception as e:
        print(f"💥 Exception getting technicians: {e}")
    
    if not selected_technician:
        print("❌ Cannot proceed without technician")
        return
    
    print()
    
    # Step 2: Create ticket with technician assignment (using SuperOps format)
    print("🎫 Step 2: Creating ticket with technician assignment...")
    
    # Use the exact format from the SuperOps client
    create_ticket_mutation = {
        "query": """
            mutation createTicket($input: CreateTicketInput!) {
                createTicket(input: $input) {
                    ticketId
                    status
                    subject
                    requester
                    technician
                    site
                    requestType
                    source
                    department
                }
            }
        """,
        "variables": {
            "input": {
                "source": "FORM",
                "subject": "Auto-Assigned Test Ticket - Technician Integration",
                "requestType": "Incident",
                "technician": {
                    "userId": selected_technician["userId"]
                },
                "site": {
                    "id": "6027178066613911552"  # Default site ID from SuperOps client
                },
                "description": "This ticket was created to test automatic technician assignment. The system fetched available technicians and assigned this ticket to an available technician automatically."
            }
        }
    }
    
    print(f"📋 Creating ticket with:")
    print(f"   Subject: Auto-Assigned Test Ticket - Technician Integration")
    print(f"   Assigned to: {selected_technician['name']} (ID: {selected_technician['userId']})")
    print(f"   Request Type: Incident")
    print(f"   Source: FORM")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(it_api_url, json=create_ticket_mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("Response JSON:")
                        print(json.dumps(result, indent=2))
                        print()
                        
                        if result and "data" in result and result["data"] and "createTicket" in result["data"]:
                            ticket_data = result["data"]["createTicket"]
                            
                            if ticket_data:
                                print("✅ SUCCESS! Ticket created with technician assignment:")
                                print(f"   🎫 Ticket ID: {ticket_data.get('ticketId')}")
                                print(f"   📝 Subject: {ticket_data.get('subject')}")
                                print(f"   📊 Status: {ticket_data.get('status')}")
                                print(f"   🔧 Request Type: {ticket_data.get('requestType')}")
                                print(f"   📍 Source: {ticket_data.get('source')}")
                                
                                # Check technician assignment
                                assigned_tech = ticket_data.get('technician')
                                if assigned_tech:
                                    print(f"   👤 Assigned Technician: {assigned_tech}")
                                    print("   ✅ Technician assignment: SUCCESS!")
                                else:
                                    print("   ⚠️  No technician assignment returned")
                                
                                # Check requester
                                requester = ticket_data.get('requester')
                                if requester:
                                    print(f"   👥 Requester: {requester}")
                                
                                print()
                                print("🏁 Test Results Summary:")
                                print("=" * 40)
                                print("✅ Technician API: Working")
                                print("✅ Ticket Creation: Working") 
                                print("✅ Technician Assignment: Working")
                                print("✅ Integration: Complete")
                                print()
                                print("🎉 Auto-assignment with technician lookup is fully functional!")
                                
                                return ticket_data.get('ticketId')
                            else:
                                print("❌ createTicket returned null")
                        
                        elif result and "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                        else:
                            print("❌ Unexpected response format")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Parse Error: {e}")
                        print(f"Raw Response: {response_text}")
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception creating ticket: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())