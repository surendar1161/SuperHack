#!/usr/bin/env python3
"""
Enhanced test for quote creation with detailed terminal display
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_quote_header():
    """Print a beautiful header for the quote"""
    print("\n" + "=" * 80)
    print("🏢 SUPEROPS QUOTE MANAGEMENT SYSTEM")
    print("=" * 80)

def print_quote_details(quote_data):
    """Print detailed quote information in a beautiful format"""
    print("\n📋 QUOTE DETAILS")
    print("-" * 50)
    print(f"Quote ID: {quote_data.get('quoteId', 'N/A')}")
    print(f"Display ID: #{quote_data.get('displayId', 'N/A')}")
    print(f"Title: {quote_data.get('title', 'N/A')}")
    print(f"Description: {quote_data.get('description', 'N/A')}")
    print(f"Status: {quote_data.get('statusEnum', 'N/A')}")
    print(f"Quote Date: {quote_data.get('quoteDate', 'N/A')}")
    print(f"Expiry Date: {quote_data.get('expiryDate', 'N/A')}")
    print(f"Total Amount: ${quote_data.get('totalAmount', '0.00')}")
    
    # Client information
    client_info = quote_data.get('client')
    if client_info:
        print(f"\n👤 CLIENT INFORMATION")
        print("-" * 30)
        print(f"Client: {client_info}")
    
    # Site information
    site_info = quote_data.get('site')
    if site_info:
        print(f"\n🏢 SITE INFORMATION")
        print("-" * 30)
        print(f"Site: {site_info}")
    
    # Items details
    items = quote_data.get('items', [])
    if items:
        print(f"\n📦 QUOTE ITEMS ({len(items)} items)")
        print("-" * 50)
        
        total_quote_value = 0
        
        for i, item in enumerate(items, 1):
            service_item = item.get('serviceItem', {})
            quantity = item.get('quantity', 'N/A')
            unit_price = item.get('unitPrice', 'N/A')
            discount_rate = item.get('discountRate', 'N/A')
            discount_amount = item.get('discountAmount', 'N/A')
            tax_amount = item.get('taxAmount', 'N/A')
            
            print(f"\n   Item #{i}")
            
            # Handle service item - it might be an object or just data
            if isinstance(service_item, dict):
                print(f"   ├─ Service: {service_item.get('name', 'Unknown Service')}")
                print(f"   ├─ Item ID: {service_item.get('itemId', 'N/A')}")
                print(f"   ├─ Description: {service_item.get('description', 'N/A')}")
                print(f"   ├─ Quantity Type: {service_item.get('quantityType', 'N/A')}")
            else:
                print(f"   ├─ Service Item: {service_item}")
            
            print(f"   ├─ Quantity: {quantity}")
            print(f"   ├─ Unit Price: ${unit_price}")
            
            # Calculate line total
            line_total = 'N/A'
            try:
                if unit_price != 'N/A' and quantity != 'N/A':
                    line_total = float(unit_price) * float(quantity)
                    print(f"   ├─ Line Total: ${line_total:.2f}")
                    total_quote_value += line_total
            except (ValueError, TypeError):
                print(f"   ├─ Line Total: Unable to calculate")
            
            if discount_rate not in ['N/A', None, '']:
                print(f"   ├─ Discount Rate: {discount_rate}%")
            if discount_amount not in ['N/A', None, '']:
                print(f"   ├─ Discount Amount: ${discount_amount}")
            if tax_amount not in ['N/A', None, '']:
                print(f"   └─ Tax Amount: ${tax_amount}")
            else:
                print(f"   └─ Tax Amount: Not specified")
        
        print(f"\n💰 QUOTE SUMMARY")
        print("-" * 30)
        print(f"Items Subtotal: ${total_quote_value:.2f}")
        print(f"Final Total: ${quote_data.get('totalAmount', '0.00')}")
    
    # Additional quote information
    print(f"\n📋 QUOTE STATUS")
    print("-" * 30)
    print(f"Current Status: {quote_data.get('statusEnum', 'N/A')}")
    print(f"Valid Until: {quote_data.get('expiryDate', 'N/A')}")
    
    if quote_data.get('description'):
        print(f"\n📝 DESCRIPTION")
        print("-" * 30)
        print(f"{quote_data.get('description')}")

async def test_detailed_quote_display():
    """Test quote creation with detailed display"""
    
    print_quote_header()
    
    # API configuration from environment
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    
    if not api_key or not customer_subdomain:
        print("❌ Missing API credentials")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    
    # API endpoint and headers
    api_url = "https://api.superops.ai/msp"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=C8136EE789722E75C5C0806BB154EDC6; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Enhanced GraphQL mutation with available fields
    mutation = {
        "query": """mutation createQuote($createQuote: CreateQuoteInput!) {
            createQuote(input: $createQuote) {
                quoteId
                displayId
                title
                description
                quoteDate
                expiryDate
                statusEnum
                totalAmount
                client
                site
                items {
                    serviceItem
                    quantity
                    unitPrice
                    discountRate
                    discountAmount
                    taxAmount
                }
            }
        }""",
        "variables": {
            "createQuote": {
                "client": {
                    "accountId": "7206852887935602688"
                },
                "description": "Comprehensive IT Services Package - Network Security, Hardware Setup, and Ongoing Support",
                "site": {
                    "id": "7206852887969157120"
                },
                "addItems": [
                    {
                        "serviceItem": {
                            "itemId": "4478245546991632384"
                        },
                        "quantity": 5,
                        "unitPrice": 150
                    },
                    {
                        "serviceItem": {
                            "itemId": "4478245546991632384"
                        },
                        "quantity": 2,
                        "unitPrice": 500
                    }
                ],
                "statusEnum": "DRAFT",
                "quoteDate": "2025-10-15",
                "expiryDate": "2025-12-15",
                "title": "Enterprise IT Services Package - Detailed Quote"
            }
        }
    }
    
    print(f"\n🚀 Creating detailed quote...")
    print(f"   Client Account: 7206852887935602688")
    print(f"   Site: 7206852887969157120")
    print(f"   Items: 2 service items")
    print(f"   Quote Date: 2025-10-15")
    print(f"   Expiry Date: 2025-12-15")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and result["data"] and "createQuote" in result["data"]:
                        quote_data = result["data"]["createQuote"]
                        
                        print(f"\n✅ Quote created successfully!")
                        
                        # Print detailed quote information
                        print_quote_details(quote_data)
                        
                        print(f"\n🔍 RAW API RESPONSE")
                        print("-" * 50)
                        print(json.dumps(quote_data, indent=2))
                        
                        print(f"\n" + "=" * 80)
                        print("🎉 QUOTE CREATION COMPLETED SUCCESSFULLY")
                        print("=" * 80)
                        
                    elif "errors" in result:
                        print(f"\n❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   - {error.get('message', error)}")
                    else:
                        print(f"\n❌ Unexpected response format")
                        print(json.dumps(result, indent=2))
                        
                else:
                    print(f"\n❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"\n💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_detailed_quote_display())