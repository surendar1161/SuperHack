#!/usr/bin/env python3
"""
Test the invoice creation Strands tool
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

async def test_invoice_tool():
    """Test the invoice creation Strands tool"""
    
    print("🛠️ Testing Invoice Creation Strands Tool")
    print("=" * 50)
    
    try:
        # Import the tools
        from tools.billing.create_invoice import create_invoice, create_simple_invoice
        
        # Test 1: Create a complex invoice with multiple items
        print("💰 Test 1: Creating complex invoice with multiple items...")
        
        items = [
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Laptop Setup and Configuration",
                "quantity": "1",
                "unit_price": "150",
                "discount_rate": "10",
                "taxable": True
            },
            {
                "billed_date": "2025-01-01", 
                "service_item_id": "4478246199507894272",
                "details": "Software Installation and Updates",
                "quantity": "2",
                "unit_price": "75",
                "discount_amount": "15",
                "taxable": True
            }
        ]
        
        complex_invoice_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="2025-01-01",
            due_date="2025-02-01",
            items=items,
            status="DRAFT",
            title="IT Services Invoice - Complex",
            memo="Multiple services provided",
            footer="Thank you for choosing our IT services",
            additional_discount="25",
            additional_discount_rate="5"
        )
        
        if complex_invoice_result.get('success'):
            print(f"✅ SUCCESS! Created complex invoice")
            print(f"   Invoice ID: {complex_invoice_result.get('invoice_id')}")
            print(f"   Display ID: {complex_invoice_result.get('display_id')}")
            print(f"   Total Amount: {complex_invoice_result.get('total_amount')}")
            print(f"   Items Count: {complex_invoice_result.get('items_count')}")
            print(f"   Status: {complex_invoice_result.get('status')}")
        else:
            print(f"❌ FAILED: {complex_invoice_result.get('error')}")
            return
        
        # Test 2: Create a simple invoice using convenience function
        print(f"\n💡 Test 2: Creating simple invoice using convenience function...")
        
        simple_invoice_result = await create_simple_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            service_item_id="4478246199507894272",
            service_description="Network Troubleshooting and Repair",
            quantity=1.0,
            unit_price=200.0,
            discount_rate=15.0
        )
        
        if simple_invoice_result.get('success'):
            print(f"✅ SUCCESS! Created simple invoice")
            print(f"   Invoice ID: {simple_invoice_result.get('invoice_id')}")
            print(f"   Display ID: {simple_invoice_result.get('display_id')}")
            print(f"   Total Amount: {simple_invoice_result.get('total_amount')}")
            print(f"   Items Count: {simple_invoice_result.get('items_count')}")
        else:
            print(f"❌ FAILED: {simple_invoice_result.get('error')}")
        
        # Test 3: Test validation with invalid data
        print(f"\n❓ Test 3: Testing validation with invalid date format...")
        
        invalid_date_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="01-01-2025",  # Invalid format
            due_date="2025-02-01",
            items=[{
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Test Service",
                "quantity": "1",
                "unit_price": "100"
            }]
        )
        
        if not invalid_date_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {invalid_date_result.get('message')}")
            print(f"   Error: {invalid_date_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for invalid date format")
        
        # Test 4: Test validation with empty items
        print(f"\n❓ Test 4: Testing validation with empty items...")
        
        empty_items_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="2025-01-01",
            due_date="2025-02-01",
            items=[]  # Empty items
        )
        
        if not empty_items_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {empty_items_result.get('message')}")
            print(f"   Error: {empty_items_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for empty items")
        
        print(f"\n🎉 All invoice tool tests completed!")
        print("   ✓ create_invoice with multiple items")
        print("   ✓ create_simple_invoice convenience function")
        print("   ✓ Date format validation")
        print("   ✓ Empty items validation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_invoice_tool())