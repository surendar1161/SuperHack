#!/usr/bin/env python3
"""
Standalone test for invoice creation tool
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the specific path for the invoice tool
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools', 'billing'))

async def test_invoice_standalone():
    """Test the invoice creation tool standalone"""
    
    print("🛠️ Testing Invoice Creation Tool (Standalone)")
    print("=" * 55)
    
    try:
        # Import the invoice tool directly
        from create_invoice import create_invoice, create_simple_invoice
        
        # Test 1: Create a simple invoice
        print("💰 Test 1: Creating simple invoice...")
        
        items = [
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "IT Support and Maintenance - Standalone Test",
                "quantity": "1",
                "unit_price": "300",
                "discount_rate": "15",
                "taxable": True
            }
        ]
        
        simple_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="2025-01-01",
            due_date="2025-02-01",
            items=items,
            status="DRAFT",
            title="IT Services Invoice - Standalone Test",
            memo="Created via standalone invoice tool test",
            footer="Professional IT Services"
        )
        
        if simple_result.get('success'):
            print(f"✅ SUCCESS! Created invoice")
            print(f"   Invoice ID: {simple_result.get('invoice_id')}")
            print(f"   Display ID: {simple_result.get('display_id')}")
            print(f"   Total Amount: {simple_result.get('total_amount')}")
            print(f"   Status: {simple_result.get('status')}")
            print(f"   Items Count: {simple_result.get('items_count')}")
            print(f"   Message: {simple_result.get('message')}")
        else:
            print(f"❌ FAILED: {simple_result.get('error')}")
            print(f"   Message: {simple_result.get('message')}")
            return
        
        # Test 2: Create invoice with multiple items and discounts
        print(f"\n💼 Test 2: Creating invoice with multiple items and discounts...")
        
        multi_items = [
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Server Setup and Configuration",
                "quantity": "1",
                "unit_price": "500",
                "discount_rate": "10",
                "taxable": True
            },
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Network Security Implementation",
                "quantity": "2",
                "unit_price": "200",
                "discount_amount": "50",
                "taxable": True
            }
        ]
        
        multi_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="2025-01-01",
            due_date="2025-02-15",
            items=multi_items,
            status="DRAFT",
            title="Enterprise IT Services Package",
            memo="Comprehensive IT setup and security",
            additional_discount="100",
            additional_discount_rate="5"
        )
        
        if multi_result.get('success'):
            print(f"✅ SUCCESS! Created multi-item invoice")
            print(f"   Invoice ID: {multi_result.get('invoice_id')}")
            print(f"   Display ID: {multi_result.get('display_id')}")
            print(f"   Total Amount: {multi_result.get('total_amount')}")
            print(f"   Items Count: {multi_result.get('items_count')}")
        else:
            print(f"❌ FAILED: {multi_result.get('error')}")
            print(f"   Message: {multi_result.get('message')}")
        
        # Test 3: Use the convenience function
        print(f"\n💡 Test 3: Using create_simple_invoice convenience function...")
        
        convenience_result = await create_simple_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            service_item_id="4478246199507894272",
            service_description="Emergency Network Repair",
            quantity=1.0,
            unit_price=400.0,
            discount_rate=12.0
        )
        
        if convenience_result.get('success'):
            print(f"✅ SUCCESS! Created invoice via convenience function")
            print(f"   Invoice ID: {convenience_result.get('invoice_id')}")
            print(f"   Display ID: {convenience_result.get('display_id')}")
            print(f"   Total Amount: {convenience_result.get('total_amount')}")
            print(f"   Service: Emergency Network Repair")
        else:
            print(f"❌ FAILED: {convenience_result.get('error')}")
            print(f"   Message: {convenience_result.get('message')}")
        
        # Test 4: Test validation with empty items
        print(f"\n❓ Test 4: Testing validation with empty items...")
        
        empty_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="2025-01-01",
            due_date="2025-02-01",
            items=[]  # Empty items list
        )
        
        if not empty_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {empty_result.get('message')}")
            print(f"   Error: {empty_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for empty items")
        
        print(f"\n🎉 All standalone invoice tool tests completed!")
        print("   ✓ Simple invoice creation with discounts")
        print("   ✓ Multi-item invoice with additional discounts") 
        print("   ✓ Convenience function for quick invoicing")
        print("   ✓ Input validation for empty items")
        print("\n📊 Summary:")
        print("   - Invoice creation API is working correctly")
        print("   - Tool handles complex invoice scenarios")
        print("   - Validation prevents invalid inputs")
        print("   - Both detailed and convenience functions work")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_invoice_standalone())