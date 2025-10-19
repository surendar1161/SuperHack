#!/usr/bin/env python3
"""
Test script for requester roles tools
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_requester_roles():
    """Test the requester roles tools"""
    
    print("🔧 Testing Requester Roles Tools")
    print("=" * 50)
    
    try:
        # Test get_requester_roles
        print("\n1. Testing get_requester_roles...")
        from src.tools.user.get_requester_roles import get_requester_roles
        
        result = await get_requester_roles()
        
        if result.get("success"):
            requester_roles = result.get("requester_roles", [])
            print(f"✅ Successfully retrieved {len(requester_roles)} requester roles")
            
            # Display first few roles
            for i, role in enumerate(requester_roles[:3]):
                role_type = role.get("roleType", {})
                features = role.get("roleFeatureList", [])
                print(f"   {i+1}. {role.get('name')} (ID: {role.get('roleId')})")
                print(f"      Type: {role_type.get('name', 'N/A')}")
                print(f"      Features: {len(features)} features")
                print(f"      Description: {role.get('description', 'N/A')[:50]}...")
            
            if len(requester_roles) > 3:
                print(f"   ... and {len(requester_roles) - 3} more")
                
            # Test get_requester_roles_summary
            print(f"\n2. Testing get_requester_roles_summary...")
            from src.tools.user.get_requester_roles import get_requester_roles_summary
            
            result2 = await get_requester_roles_summary()
            
            if result2.get("success"):
                summary = result2.get("summary")
                print(f"✅ Generated requester roles summary:")
                print(f"   Total Roles: {summary.get('total_requester_roles')}")
                print(f"   Role Types: {list(summary.get('role_types', {}).keys())}")
                features_analysis = summary.get("features_analysis", {})
                print(f"   Total Features: {features_analysis.get('total_unique_features')}")
                users_analysis = summary.get("users_analysis", {})
                print(f"   Total Users: {users_analysis.get('total_users_across_roles')}")
            else:
                print(f"❌ Failed to generate summary: {result2.get('error')}")
            
        else:
            print(f"❌ Failed to get requester roles: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Requester Roles Tools Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_requester_roles())