#!/usr/bin/env python3
"""
Test script for payment terms tools
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_payment_terms():
    """Test the payment terms tools"""
    
    print("🔧 Testing Payment Terms Tools")
    print("=" * 50)
    
    try:
        # Test get_payment_terms
        print("\n1. Testing get_payment_terms...")
        from src.tools.billing.get_payment_terms import get_payment_terms
        
        result = await get_payment_terms()
        
        if result.get("success"):
            payment_terms = result.get("payment_terms", [])
            print(f"✅ Successfully retrieved {len(payment_terms)} payment terms")
            
            # Display first few payment terms
            for i, term in enumerate(payment_terms[:3]):
                print(f"   {i+1}. {term.get('paymentTermName')} (ID: {term.get('paymentTermId')}, Value: {term.get('paymentTermValue')})")
            
            if len(payment_terms) > 3:
                print(f"   ... and {len(payment_terms) - 3} more")
                
            # Test get_payment_term_by_id if we have terms
            if payment_terms:
                print(f"\n2. Testing get_payment_term_by_id...")
                from src.tools.billing.get_payment_terms import get_payment_term_by_id
                
                first_term_id = payment_terms[0].get("paymentTermId")
                result2 = await get_payment_term_by_id(first_term_id)
                
                if result2.get("success"):
                    term = result2.get("payment_term")
                    print(f"✅ Retrieved payment term: {term.get('paymentTermName')}")
                else:
                    print(f"❌ Failed to get payment term by ID: {result2.get('error')}")
                
                # Test get_payment_term_by_name
                print(f"\n3. Testing get_payment_term_by_name...")
                from src.tools.billing.get_payment_terms import get_payment_term_by_name
                
                first_term_name = payment_terms[0].get("paymentTermName")
                if first_term_name:
                    # Search for part of the name
                    search_name = first_term_name.split()[0] if " " in first_term_name else first_term_name[:3]
                    result3 = await get_payment_term_by_name(search_name)
                    
                    if result3.get("success"):
                        if "payment_term" in result3:
                            term = result3.get("payment_term")
                            print(f"✅ Found payment term: {term.get('paymentTermName')}")
                        else:
                            terms = result3.get("payment_terms", [])
                            print(f"✅ Found {len(terms)} matching payment terms")
                    else:
                        print(f"❌ Failed to search payment terms: {result3.get('error')}")
                
                # Test get_payment_terms_summary
                print(f"\n4. Testing get_payment_terms_summary...")
                from src.tools.billing.get_payment_terms import get_payment_terms_summary
                
                result4 = await get_payment_terms_summary()
                
                if result4.get("success"):
                    summary = result4.get("summary")
                    print(f"✅ Generated payment terms summary:")
                    print(f"   Total Terms: {summary.get('total_payment_terms')}")
                    stats = summary.get("statistics", {})
                    print(f"   Average Value: {stats.get('average_value')}")
                    print(f"   Min Value: {stats.get('minimum_value')}")
                    print(f"   Max Value: {stats.get('maximum_value')}")
                else:
                    print(f"❌ Failed to generate summary: {result4.get('error')}")
            
        else:
            print(f"❌ Failed to get payment terms: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Payment Terms Tools Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_payment_terms())