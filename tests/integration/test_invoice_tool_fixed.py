#!/usr/bin/env python3
"""
Test the fixed invoice creation tool
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
    """Test the fixed invoice creation tool"""
    
    print("🛠️ Testing Fixed Invoice Creation Tool")
    print("=" * 50)
    
    try:
        # Import the tools directly
        from tools.billing.create_invoice import create_invoice, create_simple_invoice
        
        # Test 1: Create a simple invoice
        print("💰 Test 1: Creating simple invoice...")
        
        items = [
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "IT Support and Maintenance",
                "quantity": "1",
                "unit_price": "200",
                "discount_rate": "10",
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
            title="IT Services Invoice - Tool Test",
            memo="Created via invoice tool test"
        )
        
        if simple_result.get('success'):
            print(f"✅ SUCCESS! Created invoice")
            print(f"   Invoice ID: {simple_result.get('invoice_id')}")
            print(f"   Display ID: {simple_result.get('display_id')}")
            print(f"   Total Amount: {simple_result.get('total_amount')}")
            print(f"   Status: {simple_result.get('status')}")
            print(f"   Items Count: {simple_result.get('items_count')}")
        else:
            print(f"❌ FAILED: {simple_result.get('error')}")
            print(f"   Message: {simple_result.get('message')}")
            return
        
        # Test 2: Create invoice with multiple items
        print(f"\n💼 Test 2: Creating invoice with multiple items...")
        
        multi_items = [
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Hardware Setup",
                "quantity": "2",
                "unit_price": "150",
                "discount_rate": "5",
                "taxable": True
            },
            {
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Software Configuration",
                "quantity": "1",
                "unit_price": "250",
                "discount_amount": "25",
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
            title="Comprehensive IT Services",
            additional_discount="50",
            additional_discount_rate="3"
        )
        
        if multi_result.get('success'):
            print(f"✅ SUCCESS! Created multi-item invoice")
            print(f"   Invoice ID: {multi_result.get('invoice_id')}")
            print(f"   Display ID: {multi_result.get('display_id')}")
            print(f"   Total Amount: {multi_result.get('total_amount')}")
            print(f"   Items Count: {multi_result.get('items_count')}")
        else:
            print(f"❌ FAILED: {multi_result.get('error')}")
        
        # Test 3: Use the convenience function
        print(f"\n💡 Test 3: Using create_simple_invoice convenience function...")
        
        convenience_result = await create_simple_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            service_item_id="4478246199507894272",
            service_description="Network Troubleshooting",
            quantity=1.0,
            unit_price=175.0,
            discount_rate=8.0
        )
        
        if convenience_result.get('success'):
            print(f"✅ SUCCESS! Created invoice via convenience function")
            print(f"   Invoice ID: {convenience_result.get('invoice_id')}")
            print(f"   Display ID: {convenience_result.get('display_id')}")
            print(f"   Total Amount: {convenience_result.get('total_amount')}")
        else:
            print(f"❌ FAILED: {convenience_result.get('error')}")
        
        # Test 4: Test validation
        print(f"\n❓ Test 4: Testing validation with invalid date...")
        
        invalid_result = await create_invoice(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            invoice_date="01-01-2025",  # Invalid format
            due_date="2025-02-01",
            items=[{
                "billed_date": "2025-01-01",
                "service_item_id": "4478246199507894272",
                "details": "Test",
                "quantity": "1",
                "unit_price": "100"
            }]
        )
        
        if not invalid_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {invalid_result.get('message')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed")
        
        print(f"\n🎉 All invoice tool tests completed!")
        print("   ✓ Simple invoice creation")
        print("   ✓ Multi-item invoice creation") 
        print("   ✓ Convenience function")
        print("   ✓ Input validation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_invoice_tool())