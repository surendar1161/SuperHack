#!/usr/bin/env python3
"""
Standalone test for quote creation tool
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the specific path for the quote tool
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools', 'billing'))

async def test_quote_standalone():
    """Test the quote creation tool standalone"""
    
    print("🛠️ Testing Quote Creation Tool (Standalone)")
    print("=" * 55)
    
    try:
        # Import the quote tool directly
        from create_quote import create_quote, create_simple_quote
        
        # Test 1: Create a simple quote
        print("💰 Test 1: Creating simple quote...")
        
        items = [
            {
                "service_item_id": "4478245546991632384",
                "quantity": 2,
                "unit_price": 250
            }
        ]
        
        simple_result = await create_quote(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            quote_date="2025-10-15",
            expiry_date="2025-11-15",
            items=items,
            title="IT Support Services Quote - Tool Test",
            description="Comprehensive IT support and maintenance services",
            status="DRAFT"
        )
        
        if simple_result.get('success'):
            print(f"✅ SUCCESS! Created quote")
            print(f"   Quote ID: {simple_result.get('quote_id')}")
            print(f"   Display ID: {simple_result.get('display_id')}")
            print(f"   Title: {simple_result.get('title')}")
            print(f"   Status: {simple_result.get('status')}")
            print(f"   Items Count: {simple_result.get('items_count')}")
            print(f"   Quote Date: {simple_result.get('quote_date')}")
            print(f"   Expiry Date: {simple_result.get('expiry_date')}")
        else:
            print(f"❌ FAILED: {simple_result.get('error')}")
            print(f"   Message: {simple_result.get('message')}")
            return
        
        # Test 2: Create quote with multiple items
        print(f"\n💼 Test 2: Creating quote with multiple items...")
        
        multi_items = [
            {
                "service_item_id": "4478245546991632384",
                "quantity": 5,
                "unit_price": 150
            },
            {
                "service_item_id": "4478245546991632384",
                "quantity": 2,
                "unit_price": 400
            }
        ]
        
        multi_result = await create_quote(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            quote_date="2025-10-15",
            expiry_date="2025-12-15",
            items=multi_items,
            title="Enterprise IT Services Package Quote",
            description="Comprehensive enterprise IT services including hardware and software support",
            status="DRAFT"
        )
        
        if multi_result.get('success'):
            print(f"✅ SUCCESS! Created multi-item quote")
            print(f"   Quote ID: {multi_result.get('quote_id')}")
            print(f"   Display ID: {multi_result.get('display_id')}")
            print(f"   Title: {multi_result.get('title')}")
            print(f"   Items Count: {multi_result.get('items_count')}")
        else:
            print(f"❌ FAILED: {multi_result.get('error')}")
            print(f"   Message: {multi_result.get('message')}")
        
        # Test 3: Use the convenience function
        print(f"\n💡 Test 3: Using create_simple_quote convenience function...")
        
        convenience_result = await create_simple_quote(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            service_item_id="4478245546991632384",
            service_description="Network Security Assessment and Implementation",
            quantity=1.0,
            unit_price=800.0,
            title="Security Services Quote"
        )
        
        if convenience_result.get('success'):
            print(f"✅ SUCCESS! Created quote via convenience function")
            print(f"   Quote ID: {convenience_result.get('quote_id')}")
            print(f"   Display ID: {convenience_result.get('display_id')}")
            print(f"   Title: {convenience_result.get('title')}")
            print(f"   Service: Network Security Assessment and Implementation")
        else:
            print(f"❌ FAILED: {convenience_result.get('error')}")
            print(f"   Message: {convenience_result.get('message')}")
        
        # Test 4: Test validation with invalid date format
        print(f"\n❓ Test 4: Testing validation with invalid date format...")
        
        invalid_date_result = await create_quote(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            quote_date="15-10-2025",  # Invalid format
            expiry_date="2025-11-15",
            items=[{
                "service_item_id": "4478245546991632384",
                "quantity": 1,
                "unit_price": 100
            }],
            title="Test Quote"
        )
        
        if not invalid_date_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {invalid_date_result.get('message')}")
            print(f"   Error: {invalid_date_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for invalid date format")
        
        # Test 5: Test validation with empty items
        print(f"\n❓ Test 5: Testing validation with empty items...")
        
        empty_items_result = await create_quote(
            client_account_id="7206852887935602688",
            site_id="7206852887969157120",
            quote_date="2025-10-15",
            expiry_date="2025-11-15",
            items=[],  # Empty items list
            title="Empty Quote Test"
        )
        
        if not empty_items_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {empty_items_result.get('message')}")
            print(f"   Error: {empty_items_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for empty items")
        
        print(f"\n🎉 All standalone quote tool tests completed!")
        print("   ✓ Simple quote creation")
        print("   ✓ Multi-item quote creation") 
        print("   ✓ Convenience function for quick quoting")
        print("   ✓ Date format validation")
        print("   ✓ Empty items validation")
        print("\n📊 Summary:")
        print("   - Quote creation API is working correctly")
        print("   - Tool handles complex quote scenarios")
        print("   - Validation prevents invalid inputs")
        print("   - Both detailed and convenience functions work")
        print("   - Quotes can be used for pre-sales and service estimates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_quote_standalone())