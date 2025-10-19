#!/usr/bin/env python3
"""
Test Create Alert Tool - Test the create_alert functionality
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_create_alert_tool():
    """Test the create alert tool functionality"""
    print("🚨 Testing Create Alert Tool")
    print("=" * 50)
    
    try:
        # Test basic alert creation
        print("\n1. Testing create_alert...")
        from src.tools.analytics.create_alert import create_alert
        
        result = await create_alert(
            asset_id="4293925678745489408",
            message="High CPU Usage",
            description="CPU Usage is very higher than usual - threshold breach detected",
            severity="High"
        )
        
        if result.get("success"):
            print(f"✅ Success! Created alert ID: {result.get('alert_id')}")
            print(f"📋 Alert Details:")
            print(f"   • Message: {result.get('message')}")
            print(f"   • Severity: {result.get('severity')}")
            print(f"   • Status: {result.get('status')}")
            print(f"   • Created Time: {result.get('created_time')}")
            print(f"   • Asset ID: {result.get('asset_id')}")
            
            # Test CPU alert convenience function
            print(f"\n2. Testing create_cpu_alert...")
            from src.tools.analytics.create_alert import create_cpu_alert
            
            result2 = await create_cpu_alert("4293925678745489408", 95.5)
            
            if result2.get("success"):
                print(f"✅ Success! Created CPU alert ID: {result2.get('alert_id')}")
                print(f"📊 CPU Alert: {result2.get('message')} - {result2.get('severity')}")
            else:
                print(f"❌ Failed to create CPU alert: {result2.get('error')}")
                
            # Test memory alert convenience function
            print(f"\n3. Testing create_memory_alert...")
            from src.tools.analytics.create_alert import create_memory_alert
            
            result3 = await create_memory_alert("4293925678745489408", 88.2)
            
            if result3.get("success"):
                print(f"✅ Success! Created memory alert ID: {result3.get('alert_id')}")
                print(f"💾 Memory Alert: {result3.get('message')} - {result3.get('severity')}")
            else:
                print(f"❌ Failed to create memory alert: {result3.get('error')}")
                
            # Test network alert convenience function
            print(f"\n4. Testing create_network_alert...")
            from src.tools.analytics.create_alert import create_network_alert
            
            result4 = await create_network_alert("4293925678745489408", "connectivity")
            
            if result4.get("success"):
                print(f"✅ Success! Created network alert ID: {result4.get('alert_id')}")
                print(f"🌐 Network Alert: {result4.get('message')} - {result4.get('severity')}")
            else:
                print(f"❌ Failed to create network alert: {result4.get('error')}")
                
        else:
            print(f"❌ Failed to create alert: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Create Alert Tool Test...")
    asyncio.run(test_create_alert_tool())