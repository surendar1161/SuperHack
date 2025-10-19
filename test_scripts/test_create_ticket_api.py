#!/usr/bin/env python3
"""
Test SuperOps ticket creation API directly
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def test_create_ticket():
    """Test creating a ticket in SuperOps"""
    
    api_url = "https://api.superops.ai/msp/api"  # Note: MSP API for tickets
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain
    }
    
    print("🎫 SuperOps Ticket Creation Test")
    print("=" * 50)
    print(f"🔧 API URL: {api_url}")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    
    # Test ticket data
    ticket_data = {
        "subject": "API Test Ticket - Direct Creation",
        "description": "This is a test ticket created via SuperOps API to verify ticket creation functionality.",
        "priority": "Medium",
        "status": "Open",
        "category": "Hardware",
        "subcategory": "Printer",
        "requester": {
            "email": "test@example.com",
            "name": "Test User"
        }
    }
    
    print(f"\n📝 Creating ticket:")
    print(f"   📋 Subject: {ticket_data['subject']}")
    print(f"   🎯 Priority: {ticket_data['priority']}")
    print(f"   📊 Status: {ticket_data['status']}")
    print(f"   📂 Category: {ticket_data['category']}")
    
    async with aiohttp.ClientSession() as session:
        
        # Try REST API endpoint for ticket creation
        rest_endpoints = [
            "/tickets",
            "/ticket",
            "/incidents",
            "/incident"
        ]
        
        for endpoint in rest_endpoints:
            print(f"\n🔄 Trying endpoint: {endpoint}")
            
            try:
                async with session.post(
                    f"{api_url}{endpoint}",
                    json=ticket_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    
                    response_text = await response.text()
                    print(f"📡 Status: {response.status}")
                    print(f"📡 Response: {response_text[:200]}...")
                    
                    if response.status in [200, 201]:
                        try:
                            result = json.loads(response_text)
                            
                            print("✅ SUCCESS! Ticket created:")
                            print("=" * 60)
                            print("🎉 TICKET CREATION SUCCESSFUL!")
                            print("=" * 60)
                            
                            # Try to extract ticket information
                            if isinstance(result, dict):
                                ticket_id = result.get('id') or result.get('ticketId') or result.get('number')
                                print(f"🆔 Ticket ID: {ticket_id}")
                                print(f"📝 Subject: {result.get('subject', ticket_data['subject'])}")
                                print(f"📊 Status: {result.get('status', ticket_data['status'])}")
                                print(f"🎯 Priority: {result.get('priority', ticket_data['priority'])}")
                                print(f"📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            
                            print("=" * 60)
                            print(f"📋 Full Response: {json.dumps(result, indent=2)}")
                            print("=" * 60)
                            
                            return result
                            
                        except json.JSONDecodeError:
                            print(f"✅ Ticket created (non-JSON response): {response_text}")
                            return {"status": "created", "response": response_text}
                    
                    elif response.status == 404:
                        print(f"❌ Endpoint not found: {endpoint}")
                    elif response.status == 401:
                        print(f"❌ Authentication failed")
                    elif response.status == 403:
                        print(f"❌ Access forbidden")
                    else:
                        print(f"❌ HTTP Error {response.status}: {response_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        # Try GraphQL approach for tickets
        print(f"\n🔄 Trying GraphQL approach...")
        
        graphql_mutations = [
            {
                "name": "createTicket",
                "query": """
                    mutation createTicket($input: CreateTicketInput!) {
                        createTicket(input: $input) {
                            id
                            subject
                            description
                            priority
                            status
                        }
                    }
                """,
                "variables": {
                    "input": ticket_data
                }
            },
            {
                "name": "createIncident", 
                "query": """
                    mutation createIncident($input: CreateIncidentInput!) {
                        createIncident(input: $input) {
                            id
                            subject
                            description
                            priority
                            status
                        }
                    }
                """,
                "variables": {
                    "input": ticket_data
                }
            }
        ]
        
        for mutation in graphql_mutations:
            print(f"\n🧪 Trying GraphQL mutation: {mutation['name']}")
            
            try:
                async with session.post(
                    api_url,
                    json=mutation,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    
                    response_text = await response.text()
                    print(f"📡 Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            
                            if "data" in result and result["data"]:
                                mutation_result = result["data"].get(mutation['name'])
                                if mutation_result:
                                    print("✅ SUCCESS! Ticket created via GraphQL:")
                                    print("=" * 60)
                                    print("🎉 TICKET CREATION SUCCESSFUL!")
                                    print("=" * 60)
                                    print(f"🆔 Ticket ID: {mutation_result.get('id')}")
                                    print(f"📝 Subject: {mutation_result.get('subject')}")
                                    print(f"📊 Status: {mutation_result.get('status')}")
                                    print(f"🎯 Priority: {mutation_result.get('priority')}")
                                    print("=" * 60)
                                    return mutation_result
                            
                            elif "errors" in result:
                                print("❌ GraphQL Errors:")
                                for error in result["errors"]:
                                    print(f"   • {error.get('message')}")
                            
                        except json.JSONDecodeError:
                            print(f"❌ Invalid JSON: {response_text}")
                    
                    else:
                        print(f"❌ HTTP Error: {response_text[:200]}...")
                        
            except Exception as e:
                print(f"❌ GraphQL request failed: {e}")
    
    print("\n💥 All ticket creation attempts failed")
    return None

async def main():
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = await test_create_ticket()
    
    if result:
        print(f"\n🎉 SUCCESS! Ticket creation is working!")
    else:
        print(f"\n❌ Ticket creation failed - may need different API approach")

if __name__ == "__main__":
    asyncio.run(main())