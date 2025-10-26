#!/usr/bin/env python3
"""
Test Create Client Tool - Test the create_client functionality
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_create_client_tool():
    """Test the create client tool functionality"""
    print("🏢 Testing Create Client Tool")
    print("=" * 50)
    
    try:
        # Test basic client creation
        print("\n1. Testing create_client...")
        from src.tools.user.create_client import create_client
        
        result = await create_client(
            name="Test Client Organization",
            stage="Active",
            status="Paid",
            account_manager_id="8275806997713629184"
        )
        
        if result.get("success"):
            print(f"✅ Success! Created client ID: {result.get('account_id')}")
            print(f"🏢 Client Details:")
            print(f"   • Name: {result.get('name')}")
            print(f"   • Stage: {result.get('stage')}")
            print(f"   • Status: {result.get('status')}")
            print(f"   • Account ID: {result.get('account_id')}")
            print(f"   • HQ Site: {result.get('hq_site')}")
            
            # Test active client creation
            print(f"\n2. Testing create_active_client...")
            from src.tools.user.create_client import create_active_client
            
            result2 = await create_active_client("Active Demo Client")
            
            if result2.get("success"):
                print(f"✅ Success! Created active client ID: {result2.get('account_id')}")
                print(f"🎯 Active Client: {result2.get('name')} - {result2.get('stage')}")
            else:
                print(f"❌ Failed to create active client: {result2.get('error')}")
                
            # Test prospect client creation
            print(f"\n3. Testing create_prospect_client...")
            from src.tools.user.create_client import create_prospect_client
            
            result3 = await create_prospect_client("Prospect Demo Client")
            
            if result3.get("success"):
                print(f"✅ Success! Created prospect client ID: {result3.get('account_id')}")
                print(f"🎯 Prospect Client: {result3.get('name')} - {result3.get('stage')}")
            else:
                print(f"❌ Failed to create prospect client: {result3.get('error')}")
                
            # Test enterprise client creation
            print(f"\n4. Testing create_enterprise_client...")
            from src.tools.user.create_client import create_enterprise_client
            
            result4 = await create_enterprise_client(
                name="Enterprise Demo Corp",
                site_name="Enterprise HQ",
                timezone="America/New_York"
            )
            
            if result4.get("success"):
                print(f"✅ Success! Created enterprise client ID: {result4.get('account_id')}")
                print(f"🏢 Enterprise Client: {result4.get('name')} - 24/7 Operations")
            else:
                print(f"❌ Failed to create enterprise client: {result4.get('error')}")
                
        else:
            print(f"❌ Failed to create client: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Create Client Tool Test...")
    asyncio.run(test_create_client_tool())