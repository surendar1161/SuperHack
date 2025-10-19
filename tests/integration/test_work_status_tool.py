#!/usr/bin/env python3
"""
Test the work status Strands tool
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

async def test_work_status_tool():
    """Test the work status Strands tool"""
    
    print("🛠️ Testing Work Status Strands Tool")
    print("=" * 50)
    
    try:
        # Import the tools
        from tools.metadata.get_work_status import (
            get_work_status_list, 
            get_work_status_by_name, 
            get_work_status_by_state
        )
        
        # Test 1: Get all work statuses
        print("📊 Test 1: Getting all work statuses...")
        all_statuses_result = await get_work_status_list()
        
        if all_statuses_result.get('success'):
            statuses = all_statuses_result.get('statuses', [])
            count = all_statuses_result.get('count', 0)
            print(f"✅ SUCCESS! Found {count} work statuses")
            
            print("\n📋 Available Work Statuses:")
            print("-" * 40)
            for status in statuses:
                print(f"   • {status.get('display_name')} (ID: {status.get('id')})")
            
        else:
            print(f"❌ FAILED: {all_statuses_result.get('error')}")
            return
        
        # Test 2: Get specific status by name
        print(f"\n🔍 Test 2: Getting status by name 'In Progress'...")
        status_by_name_result = await get_work_status_by_name("In Progress")
        
        if status_by_name_result.get('success'):
            status = status_by_name_result.get('status')
            print(f"✅ SUCCESS! Found status: {status.get('display_name')}")
            print(f"   ID: {status.get('id')}")
            print(f"   State: {status.get('state')}")
        else:
            print(f"❌ FAILED: {status_by_name_result.get('error')}")
        
        # Test 3: Get statuses by state
        print(f"\n🏷️ Test 3: Getting statuses with state 'COMPLETED'...")
        status_by_state_result = await get_work_status_by_state("COMPLETED")
        
        if status_by_state_result.get('success'):
            statuses = status_by_state_result.get('statuses', [])
            count = status_by_state_result.get('count', 0)
            print(f"✅ SUCCESS! Found {count} statuses with state 'COMPLETED'")
            
            for status in statuses:
                print(f"   • {status.get('name')} (ID: {status.get('id')})")
        else:
            print(f"❌ FAILED: {status_by_state_result.get('error')}")
        
        # Test 4: Test with non-existent status
        print(f"\n❓ Test 4: Testing with non-existent status 'NonExistent'...")
        nonexistent_result = await get_work_status_by_name("NonExistent")
        
        if not nonexistent_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {nonexistent_result.get('message')}")
            available = nonexistent_result.get('available_statuses', [])
            print(f"   Available statuses: {', '.join(available[:3])}...")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for non-existent status")
        
        print(f"\n🎉 All work status tool tests completed!")
        print("   ✓ get_work_status_list")
        print("   ✓ get_work_status_by_name")
        print("   ✓ get_work_status_by_state")
        print("   ✓ Error handling for non-existent status")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_work_status_tool())