#!/usr/bin/env python3
"""
Test the SuperOps client create_invoice method
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

async def test_invoice_client():
    """Test the SuperOps client create_invoice method"""
    
    print("🔧 Testing SuperOps Client - create_invoice method")
    print("=" * 60)
    
    try:
        # Import after adding to path
        from clients.superops_client import SuperOpsClient
        from agents.config import AgentConfig
        
        # Initialize client
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Test 1: Create invoice with single item
        print("💰 Test 1: Creating invoice with single item...")
        
        invoice_data = {
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
                    "details": "IT Support Services - Client Test",
                    "quantity": "1",
                    "unitPrice": "250",
                    "discountRate": "10",
                    "taxable": True
                }
            ],
            "additionalDiscount": "25",
            "additionalDiscountRate": "5",
            "memo": "Test invoice via SuperOps client",
            "title": "IT Services Invoice - Client Test",
            "footer": "Professional IT Services"
        }
        
        invoice_result = await client.create_invoice(invoice_data)
        
        if invoice_result and invoice_result.get('invoiceId'):
            print(f"✅ SUCCESS! Created invoice")
            print(f"   Invoice ID: {invoice_result.get('invoiceId')}")
            print(f"   Display ID: {invoice_result.get('displayId')}")
            print(f"   Status: {invoice_result.get('status')}")
            print(f"   Invoice Date: {invoice_result.get('invoiceDate')}")
            print(f"   Due Date: {invoice_result.get('dueDate')}")
            print(f"   Total Amount: {invoice_result.get('totalAmount')}")
            
            # Show items
            items = invoice_result.get('items', [])
            if items:
                print(f"   Items ({len(items)}):")
                for i, item in enumerate(items, 1):
                    service_item = item.get('serviceItem', {})
                    print(f"     {i}. {service_item.get('name', 'Unknown Service')}")
                    print(f"        Item ID: {service_item.get('itemId', 'N/A')}")
                    print(f"        Discount Rate: {item.get('discountRate', 'N/A')}%")
        else:
            print("❌ Failed to create invoice")
            print(f"Result: {invoice_result}")
            return
        
        # Test 2: Create invoice with multiple items
        print(f"\n💼 Test 2: Creating invoice with multiple items...")
        
        multi_item_data = {
            "client": {
                "accountId": "7206852887935602688"
            },
            "site": {
                "id": "7206852887969157120"
            },
            "statusEnum": "DRAFT",
            "invoiceDate": "2025-01-01",
            "dueDate": "2025-02-15",
            "addItems": [
                {
                    "billedDate": "2025-01-01",
                    "serviceItem": {
                        "itemId": "4478246199507894272"
                    },
                    "details": "Hardware Setup and Configuration",
                    "quantity": "2",
                    "unitPrice": "150",
                    "discountRate": "5",
                    "taxable": True
                },
                {
                    "billedDate": "2025-01-01",
                    "serviceItem": {
                        "itemId": "4478246199507894272"
                    },
                    "details": "Software Installation and Training",
                    "quantity": "1",
                    "unitPrice": "300",
                    "discountAmount": "30",
                    "taxable": True
                }
            ],
            "memo": "Multi-item invoice test",
            "title": "Comprehensive IT Services",
            "footer": "Thank you for your business"
        }
        
        multi_result = await client.create_invoice(multi_item_data)
        
        if multi_result and multi_result.get('invoiceId'):
            print(f"✅ SUCCESS! Created multi-item invoice")
            print(f"   Invoice ID: {multi_result.get('invoiceId')}")
            print(f"   Display ID: {multi_result.get('displayId')}")
            print(f"   Total Amount: {multi_result.get('totalAmount')}")
            
            items = multi_result.get('items', [])
            print(f"   Items: {len(items)} services")
            
            print("\n🎉 All SuperOps client tests passed!")
            print("   ✓ Single item invoice creation")
            print("   ✓ Multi-item invoice creation")
            print("   ✓ Invoice data parsing and formatting")
        else:
            print("❌ Failed to create multi-item invoice")
            print(f"Result: {multi_result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_invoice_client())