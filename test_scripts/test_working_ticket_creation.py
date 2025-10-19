#!/usr/bin/env python3
"""
Test ticket creation using the working SuperOps client implementation
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def test_working_ticket_creation():
    """Test ticket creation using the exact working format from SuperOps client"""
    
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    # Use the exact working format from the SuperOps client
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Use the exact working mutation from the client
    mutation = {
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
                "subject": "API Test Ticket - Working Format",
                "requestType": "Incident",
                "site": {
                    "id": "7206852887969157120"
                },
                "description": "This ticket was created using the working SuperOps client format to test ticket creation functionality.",
                "client": {
                    "accountId": "7206852887935602688"
                }
            }
        }
    }
    
    # Use MSP API endpoint (working format)
    msp_api_url = "https://api.superops.ai/msp"
    
    print("🎫 SuperOps Ticket Creation Test - Working Format")
    print("=" * 60)
    print(f"🔧 API URL: {msp_api_url}")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print(f"📝 Subject: {mutation['variables']['input']['subject']}")
    print(f"📂 Request Type: {mutation['variables']['input']['requestType']}")
    print(f"🏢 Site ID: {mutation['variables']['input']['site']['id']}")
    print(f"👤 Client ID: {mutation['variables']['input']['client']['accountId']}")
    
    async with aiohttp.ClientSession() as session:
        
        print(f"\n🚀 Creating ticket using working format...")
        
        try:
            async with session.post(
                msp_api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                print(f"\n📡 Response Status: {response.status}")
                print(f"📡 Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print(f"📡 Parsed Response: {json.dumps(result, indent=2)}")
                        
                        if "data" in result and result["data"] and "createTicket" in result["data"]:
                            create_result = result["data"]["createTicket"]
                            
                            if create_result:
                                print("\n" + "=" * 60)
                                print("✅ TICKET CREATED SUCCESSFULLY!")
                                print("=" * 60)
                                print(f"🆔 Ticket ID: {create_result.get('ticketId')}")
                                print(f"📝 Subject: {create_result.get('subject')}")
                                print(f"📊 Status: {create_result.get('status')}")
                                print(f"📂 Request Type: {create_result.get('requestType')}")
                                print(f"🔗 Source: {create_result.get('source')}")
                                print(f"👤 Technician: {create_result.get('technician')}")
                                print(f"🏢 Site: {create_result.get('site')}")
                                print(f"🏢 Client: {create_result.get('client')}")
                                print(f"📅 Created At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                print("=" * 60)
                                
                                # Log the successful creation
                                print("\n📋 LOGGING TICKET CREATION SUCCESS:")
                                print("-" * 40)
                                print(f"SUCCESS: Ticket created via SuperOps API")
                                print(f"Ticket ID: {create_result.get('ticketId')}")
                                print(f"Subject: {create_result.get('subject')}")
                                print(f"Status: {create_result.get('status')}")
                                print(f"Request Type: {create_result.get('requestType')}")
                                print(f"API Endpoint: {msp_api_url}")
                                print(f"Timestamp: {datetime.now().isoformat()}")
                                print("-" * 40)
                                
                                return create_result
                            else:
                                print("❌ createTicket returned null")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   • {error.get('message')}")
                                if 'extensions' in error:
                                    print(f"     Type: {error['extensions'].get('classification')}")
                        
                        else:
                            print("❌ Unexpected response format")
                            print(json.dumps(result, indent=2))
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"Raw response: {response_text}")
                
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    return None

async def main():
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = await test_working_ticket_creation()
    
    if result:
        print(f"\n🎉 SUCCESS! Ticket creation is working!")
        print(f"✅ Ticket ID: {result.get('ticketId')}")
    else:
        print(f"\n❌ Ticket creation failed")

if __name__ == "__main__":
    asyncio.run(main())