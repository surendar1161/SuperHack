#!/usr/bin/env python3
"""
Complete ticket workflow test:
1. Get technicians
2. Create a ticket
3. Update ticket to assign technician
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_workflow():
    """Test complete ticket workflow with technician assignment"""
    
    print("🎯 Complete Ticket Workflow Test")
    print("=" * 50)
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    
    if not api_key or not customer_subdomain:
        print("❌ Missing API credentials")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print()
    
    # API endpoints and headers
    it_api_url = "https://api.superops.ai/it"  # For technicians
    msp_api_url = "https://api.superops.ai/msp"  # For ticket creation
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=CC010125CA4900268BCB4D47B3A1DF39; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Get Technicians
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
                        listInfo { 
                            page 
                            pageSize
                            totalCount
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
        
        try:
            async with session.post(it_api_url, json=technicians_query, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Failed to get technicians: {response.status}")
                    return
                
                result = json.loads(await response.text())
                
                if "data" in result and "getTechnicianList" in result["data"]:
                    user_list = result["data"]["getTechnicianList"].get("userList", [])
                    
                    if user_list:
                        technician = user_list[0]  # Use first technician
                        print(f"✅ Found technician: {technician['name']} (ID: {technician['userId']})")
                        
                        # Parse name for firstName/lastName
                        name_parts = technician['name'].split(' ', 1)
                        first_name = name_parts[0] if name_parts else "Unknown"
                        last_name = name_parts[1] if len(name_parts) > 1 else ""
                        
                    else:
                        print("❌ No technicians found")
                        return
                else:
                    print("❌ Invalid technicians response")
                    return
        
        except Exception as e:
            print(f"❌ Error getting technicians: {e}")
            return
        
        # Step 2: Create Ticket (using MSP API endpoint like the working curl)
        print("\n🎟️ Step 2: Creating ticket...")
        create_ticket_query = {
            "query": """
                mutation createTicket($input: CreateTicketInput!) {
                    createTicket(input: $input) {
                        ticketId
                        status
                        subject
                        technician
                        site
                        requestType
                        source
                        client
                    }
                }
            """,
            "variables": {
                "input": {
                    "source": "FORM",
                    "subject": "Test Ticket - Workflow Test",
                    "requestType": "Incident",
                    "site": {
                        "id": "7206852887969157120"
                    },
                    "description": "This is a test ticket created for workflow testing",
                    "client": {
                        "accountId": "7206852887935602688"
                    }
                }
            }
        }
        
        try:
            async with session.post(msp_api_url, json=create_ticket_query, headers=headers) as response:
                response_text = await response.text()
                print(f"📊 Create Ticket Response Status: {response.status}")
                
                if response.status != 200:
                    print(f"❌ Failed to create ticket: {response.status}")
                    print(f"Response: {response_text}")
                    return
                
                result = json.loads(response_text)
                print("📋 Create Ticket Response:")
                print(json.dumps(result, indent=2))
                
                if "data" in result and result["data"] and "createTicket" in result["data"]:
                    ticket = result["data"]["createTicket"]
                    ticket_id = ticket["ticketId"]
                    subject = ticket["subject"]
                    print(f"✅ Created ticket: {subject} (ID: {ticket_id})")
                    
                elif "errors" in result:
                    print("❌ GraphQL Errors in ticket creation:")
                    for error in result["errors"]:
                        print(f"   - {error.get('message', error)}")
                    return
                else:
                    print("❌ Invalid ticket creation response")
                    return
        
        except Exception as e:
            print(f"❌ Error creating ticket: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 3: Update Ticket to Assign Technician (using MSP API like the working curl)
        print(f"\n🔧 Step 3: Assigning technician {technician['name']} to ticket {subject}...")
        
        # Use the working MSP API format
        update_ticket_query = {
            "query": """mutation updateTicket($input: UpdateTicketInput!) {
                updateTicket(input: $input) {
                    ticketId
                    status
                    subject
                    technician
                    site
                    requestType
                    source
                    client
                }
            }""",
            "variables": {
                "input": {
                    "ticketId": ticket_id,
                    "technician": {
                        "userId": technician['userId']
                    }
                }
            }
        }
        
        try:
            async with session.post(msp_api_url, json=update_ticket_query, headers=headers) as response:
                response_text = await response.text()
                
                print(f"📊 Update Response Status: {response.status}")
                print("📋 Update Ticket Response:")
                print(response_text)
                
                if response.status == 200:
                    result = json.loads(response_text) if response_text else None
                    
                    if result and "data" in result and result["data"] and "updateTicket" in result["data"]:
                        updated_ticket = result["data"]["updateTicket"]
                        assigned_tech = updated_ticket.get("technician")
                        
                        print("✅ SUCCESS! Ticket updated successfully")
                        print(f"   Ticket ID: {updated_ticket.get('ticketId', 'N/A')}")
                        print(f"   Subject: {updated_ticket.get('subject', 'N/A')}")
                        print(f"   Status: {updated_ticket.get('status', 'N/A')}")
                        print(f"   Request Type: {updated_ticket.get('requestType', 'N/A')}")
                        
                        if assigned_tech:
                            print(f"   Assigned Technician: {assigned_tech}")
                        else:
                            print("   ⚠️ No technician assignment found in response")
                        
                        print("\n🎉 Complete workflow successful!")
                        print("   ✓ Got technicians")
                        print("   ✓ Created ticket")
                        print("   ✓ Assigned technician to ticket")
                        
                    elif "errors" in result:
                        print("❌ GraphQL Errors in ticket update:")
                        for error in result["errors"]:
                            print(f"   - {error.get('message', error)}")
                    else:
                        print("❌ Unexpected update response format")
                        print(json.dumps(result, indent=2))
                        
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
        
        except Exception as e:
            print(f"❌ Error updating ticket: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())