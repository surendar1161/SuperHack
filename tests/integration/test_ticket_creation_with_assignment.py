#!/usr/bin/env python3
"""
Test ticket creation with automatic technician assignment
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_get_technicians():
    """First test getting technicians to see available user IDs"""
    
    print("👥 Step 1: Getting Available Technicians")
    print("=" * 50)
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    api_url = "https://api.superops.ai/it"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Get technicians query
    query = {
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
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=query, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and "getTechnicianList" in result["data"]:
                        technician_data = result["data"]["getTechnicianList"]
                        user_list = technician_data.get("userList", [])
                        
                        print(f"✅ Found {len(user_list)} technicians:")
                        
                        available_technician = None
                        for i, tech in enumerate(user_list, 1):
                            user_id = tech.get("userId")
                            name = tech.get("name", "Unknown")
                            email = tech.get("email", "No email")
                            status = tech.get("status", "Unknown")
                            
                            print(f"   {i}. {name}")
                            print(f"      User ID: {user_id}")
                            print(f"      Email: {email}")
                            print(f"      Status: {status}")
                            print()
                            
                            # Use the first technician for assignment test
                            if not available_technician and user_id:
                                available_technician = {
                                    "userId": user_id,
                                    "name": name,
                                    "email": email
                                }
                        
                        return available_technician
                    else:
                        print("❌ No technicians found")
                        return None
                else:
                    print(f"❌ HTTP Error {response.status}: {response_text}")
                    return None
                    
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None

async def test_create_ticket_with_assignment(technician):
    """Test creating a ticket with automatic assignment"""
    
    print("🎫 Step 2: Creating Ticket with Assignment")
    print("=" * 50)
    
    if not technician:
        print("❌ No technician available for assignment test")
        return
    
    # API configuration
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    api_url = "https://api.superops.ai/it"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Create ticket mutation with assignment
    mutation = {
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
                    createdAt
                }
            }
        """,
        "variables": {
            "input": {
                "subject": "Test Ticket with Auto-Assignment",
                "description": "This is a test ticket created with automatic technician assignment functionality. The system should assign this ticket to an available technician.",
                "priority": "MEDIUM",
                "assigneeId": technician["userId"]  # Assign to the technician we found
            }
        }
    }
    
    print(f"📋 Creating ticket assigned to:")
    print(f"   Name: {technician['name']}")
    print(f"   User ID: {technician['userId']}")
    print(f"   Email: {technician['email']}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=mutation, headers=headers) as response:
                response_text = await response.text()
                
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    print("Response JSON:")
                    print(json.dumps(result, indent=2))
                    
                    if "data" in result and "createTicket" in result["data"]:
                        ticket_data = result["data"]["createTicket"]
                        
                        if ticket_data:
                            print("\n✅ SUCCESS! Ticket created with assignment:")
                            print(f"   Ticket ID: {ticket_data.get('ticketId')}")
                            print(f"   Subject: {ticket_data.get('subject')}")
                            print(f"   Priority: {ticket_data.get('priority')}")
                            print(f"   Status: {ticket_data.get('status')}")
                            
                            assignee = ticket_data.get('assignee')
                            if assignee:
                                print(f"   Assigned to: {assignee.get('name')} ({assignee.get('userId')})")
                                print(f"   Assignee Email: {assignee.get('email')}")
                            else:
                                print("   ⚠️  No assignee information returned")
                            
                            return ticket_data.get('ticketId')
                        else:
                            print("❌ createTicket returned null")
                    
                    elif "errors" in result:
                        print("❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   - {error.get('message', error)}")
                    else:
                        print("❌ Unexpected response format")
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the complete test"""
    
    print("🎯 Ticket Creation with Auto-Assignment Test")
    print("=" * 60)
    print()
    
    # Step 1: Get available technicians
    technician = await test_get_technicians()
    
    print()
    
    # Step 2: Create ticket with assignment
    if technician:
        ticket_id = await test_create_ticket_with_assignment(technician)
        
        print()
        print("🏁 Test Summary:")
        print("=" * 30)
        if ticket_id:
            print(f"✅ Ticket created successfully: {ticket_id}")
            print(f"✅ Assigned to: {technician['name']}")
            print("✅ Auto-assignment functionality working!")
        else:
            print("❌ Ticket creation failed")
    else:
        print("❌ Cannot test ticket assignment - no technicians available")

if __name__ == "__main__":
    asyncio.run(main())