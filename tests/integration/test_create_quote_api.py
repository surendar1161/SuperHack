#!/usr/bin/env python3
"""
Test the create quote API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_quote_api():
    """Test the create quote API directly"""
    
    print("💰 Testing SuperOps Create Quote API")
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
    
    # API endpoint and headers
    api_url = "https://api.superops.ai/msp"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=C8136EE789722E75C5C0806BB154EDC6; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL mutation from the curl command
    mutation = {
        "query": """mutation createQuote($createQuote: CreateQuoteInput!) {
            createQuote(input: $createQuote) {
                quoteId
                displayId
                items {serviceItem quantity}
                title
                client
            }
        }""",
        "variables": {
            "createQuote": {
                "client": {
                    "accountId": "7206852887935602688"
                },
                "description": "Test quote for IT services - API Integration",
                "site": {
                    "id": "7206852887969157120"
                },
                "addItems": [
                    {
                        "serviceItem": {
                            "itemId": "4478245546991632384"
                        },
                        "quantity": 3,
                        "unitPrice": 332
                    }
                ],
                "statusEnum": "DRAFT",
                "quoteDate": "2025-10-15",
                "expiryDate": "2025-11-15",
                "title": "IT Services Quote - API Test"
            }
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Mutation: createQuote")
    print(f"   Client Account ID: 7206852887935602688")
    print(f"   Site ID: 7206852887969157120")
    print(f"   Quote Date: 2025-10-15")
    print(f"   Expiry Date: 2025-11-15")
    print(f"   Status: DRAFT")
    print(f"   Items: 1 service item (Quantity: 3, Unit Price: 332)")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps API...")
            
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
                        print("✅ SUCCESS!")
                        print("Raw Response JSON:")
                        print(json.dumps(result, indent=2))
                        print()
                        
                        # Extract quote data
                        if result and "data" in result and result["data"] and "createQuote" in result["data"]:
                            quote = result["data"]["createQuote"]
                            
                            print(f"📈 Quote Creation Results:")
                            print(f"   Quote ID: {quote.get('quoteId', 'N/A')}")
                            print(f"   Display ID: {quote.get('displayId', 'N/A')}")
                            print(f"   Title: {quote.get('title', 'N/A')}")
                            
                            # Show client info
                            client_info = quote.get('client', {})
                            if client_info:
                                print(f"   Client: {client_info}")
                            
                            # Show items
                            items = quote.get('items', [])
                            if items:
                                print(f"   Items ({len(items)}):")
                                for i, item in enumerate(items, 1):
                                    service_item = item.get('serviceItem', {})
                                    quantity = item.get('quantity', 'N/A')
                                    print(f"     {i}. Service: {service_item}")
                                    print(f"        Quantity: {quantity}")
                            
                            print(f"\n🎉 Quote created successfully!")
                            
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                        else:
                            print("❌ Unexpected response format")
                            print(json.dumps(result, indent=2))
                        
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

if __name__ == "__main__":
    print("🎯 SuperOps Create Quote API Test")
    print("Testing the createQuote mutation")
    print()
    
    # Run the async test
    asyncio.run(test_create_quote_api())