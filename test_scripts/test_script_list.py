#!/usr/bin/env python3
"""
Test Script List Tool - Test the get_script_list_by_type functionality
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_script_list_tool():
    """Test the script list tool functionality"""
    print("🧪 Testing Script List Tool")
    print("=" * 50)
    
    try:
        # Test get_script_list_by_type
        print("\n1. Testing get_script_list_by_type...")
        from src.tools.knowledge.get_script_list import get_script_list_by_type
        
        result = await get_script_list_by_type(script_type="WINDOWS", page=1, page_size=5)
        
        if result.get("success"):
            scripts = result.get("scripts", [])
            print(f"✅ Success! Retrieved {len(scripts)} Windows scripts")
            
            if scripts:
                print("\n📋 Sample Scripts:")
                for i, script in enumerate(scripts[:3], 1):
                    print(f"   {i}. {script.get('name', 'N/A')}")
                    print(f"      ID: {script.get('scriptId', 'N/A')}")
                    print(f"      Description: {script.get('description', 'N/A')[:50]}...")
                    print(f"      Added By: {script.get('addedBy', 'N/A')}")
                    print()
                
                if len(scripts) > 3:
                    print(f"   ... and {len(scripts) - 3} more")
                
            # Test get_script_summary
            print(f"\n2. Testing get_script_summary...")
            from src.tools.knowledge.get_script_list import get_script_summary
            
            result2 = await get_script_summary()
            
            if result2.get("success"):
                print(f"✅ Success! Script summary generated")
                print(f"📊 Total Scripts Available: {result2.get('total_scripts', 0)}")
                
                script_types = result2.get('script_types', {})
                for script_type, data in script_types.items():
                    print(f"   • {script_type}: {data.get('count', 0)} scripts")
            else:
                print(f"❌ Failed to get script summary: {result2.get('error')}")
                
            # Test search functionality
            print(f"\n3. Testing search_scripts_by_name...")
            from src.tools.knowledge.get_script_list import search_scripts_by_name
            
            result3 = await search_scripts_by_name("system", "WINDOWS")
            
            if result3.get("success"):
                matches = result3.get("scripts", [])
                print(f"✅ Success! Found {len(matches)} scripts matching 'system'")
                
                if matches:
                    print("\n🔍 Matching Scripts:")
                    for script in matches[:3]:
                        print(f"   • {script.get('name', 'N/A')}")
            else:
                print(f"❌ Failed to search scripts: {result3.get('error')}")
                
        else:
            print(f"❌ Failed to get script list: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Script List Tool Test...")
    asyncio.run(test_script_list_tool())