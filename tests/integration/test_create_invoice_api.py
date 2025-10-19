#!/usr/bin/env python3
"""
Test the create invoice API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_invoice_api():
    """Test the create invoice API directly"""
    
    print("💰 Testing SuperOps Create Invoice API")
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
        "query": """mutation createInvoice($input: CreateInvoiceInput!) {
            createInvoice(input: $input) {
                invoiceId
                displayId
                client
                site
                invoiceDate
                dueDate
                statusEnum
                sentToClient
                discountAmount
                additionalDiscount
                additionalDiscountRate
                totalAmount
                notes
                items { 
                    serviceItem 
                    discountRate 
                    taxAmount 
                } 
                paymentDate
                totalAmount
                paymentMethod
                paymentReference
                invoicePaymentTerm
            }
        }""",
        "variables": {
            "input": {
                "client": {
                    "accountId": "7206852887935602688"
                },
                "site": {
                    "id": "7206852887969157120"
                },
                "statusEnum": "DRAFT",
                "invoiceDate": "2025-01-01",
                "dueDate": "2025-02-01",
                "addItems": [
                    {
                        "billedDate": "2025-01-01",
                        "serviceItem": {
                            "itemId": "4478246199507894272"
                        },
                        "details": "Test Service - API Integration",
                        "quantity": "2",
                        "unitPrice": "100",
                        "discountRate": "5",
                        "discountAmount": "20",
                        "taxable": True
                    }
                ],
                "additionalDiscount": "50",
                "additionalDiscountRate": "5",
                "memo": "Test invoice created via API",
                "title": "Test Invoice - API Integration",
                "footer": "Thank you for your business"
            }
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Mutation: createInvoice")
    print(f"   Client Account ID: 7206852887935602688")
    print(f"   Site ID: 7206852887969157120")
    print(f"   Invoice Date: 2025-01-01")
    print(f"   Due Date: 2025-02-01")
    print(f"   Status: DRAFT")
    print(f"   Items: 1 service item")
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
                        
                        # Extract invoice data
                        if result and "data" in result and result["data"] and "createInvoice" in result["data"]:
                            invoice = result["data"]["createInvoice"]
                            
                            print(f"📈 Invoice Creation Results:")
                            print(f"   Invoice ID: {invoice.get('invoiceId', 'N/A')}")
                            print(f"   Display ID: {invoice.get('displayId', 'N/A')}")
                            print(f"   Status: {invoice.get('statusEnum', 'N/A')}")
                            print(f"   Invoice Date: {invoice.get('invoiceDate', 'N/A')}")
                            print(f"   Due Date: {invoice.get('dueDate', 'N/A')}")
                            print(f"   Total Amount: {invoice.get('totalAmount', 'N/A')}")
                            print(f"   Additional Discount: {invoice.get('additionalDiscount', 'N/A')}")
                            print(f"   Sent to Client: {invoice.get('sentToClient', 'N/A')}")
                            
                            # Show client and site info
                            client_info = invoice.get('client', {})
                            site_info = invoice.get('site', {})
                            if client_info:
                                print(f"   Client: {client_info}")
                            if site_info:
                                print(f"   Site: {site_info}")
                            
                            # Show items
                            items = invoice.get('items', [])
                            if items:
                                print(f"   Items ({len(items)}):")
                                for i, item in enumerate(items, 1):
                                    print(f"     {i}. Service Item: {item.get('serviceItem', 'N/A')}")
                                    print(f"        Discount Rate: {item.get('discountRate', 'N/A')}")
                                    print(f"        Tax Amount: {item.get('taxAmount', 'N/A')}")
                            
                            print(f"\n🎉 Invoice created successfully!")
                            
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
    print("🎯 SuperOps Create Invoice API Test")
    print("Testing the createInvoice mutation")
    print()
    
    # Run the async test
    asyncio.run(test_create_invoice_api())