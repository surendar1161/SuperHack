#!/usr/bin/env python3
"""
Test Create Ticket Note Tool - Test the create_ticket_note functionality
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_create_ticket_note_tool():
    """Test the create ticket note tool functionality"""
    print("📝 Testing Create Ticket Note Tool")
    print("=" * 50)
    
    try:
        # Test basic note creation
        print("\n1. Testing create_ticket_note...")
        from src.tools.ticket.create_ticket_note import create_ticket_note
        
        result = await create_ticket_note(
            ticket_id="10679116294692864",
            content="The network access points need to be replaced due to hardware failure",
            privacy_type="PUBLIC"
        )
        
        if result.get("success"):
            print(f"✅ Success! Created note ID: {result.get('note_id')}")
            print(f"📝 Note Details:")
            print(f"   • Content: {result.get('content')[:50]}...")
            print(f"   • Privacy: {result.get('privacy_type')}")
            print(f"   • Added By: {result.get('added_by')}")
            print(f"   • Added On: {result.get('added_on')}")
            print(f"   • Ticket ID: {result.get('ticket_id')}")
            
            # Test investigation note
            print(f"\n2. Testing add_investigation_note...")
            from src.tools.ticket.create_ticket_note import add_investigation_note
            
            result2 = await add_investigation_note(
                ticket_id="10679116294692864",
                findings="Network equipment showing signs of hardware failure",
                next_steps="Schedule maintenance window for replacement"
            )
            
            if result2.get("success"):
                print(f"✅ Success! Created investigation note ID: {result2.get('note_id')}")
                print(f"🔍 Investigation Note: {result2.get('content')[:60]}...")
            else:
                print(f"❌ Failed to create investigation note: {result2.get('error')}")
                
            # Test resolution note
            print(f"\n3. Testing add_resolution_note...")
            from src.tools.ticket.create_ticket_note import add_resolution_note
            
            result3 = await add_resolution_note(
                ticket_id="10679116294692864",
                solution="Replaced faulty network access points with new hardware",
                time_taken="2 hours"
            )
            
            if result3.get("success"):
                print(f"✅ Success! Created resolution note ID: {result3.get('note_id')}")
                print(f"✅ Resolution Note: {result3.get('content')[:60]}...")
            else:
                print(f"❌ Failed to create resolution note: {result3.get('error')}")
                
            # Test private note
            print(f"\n4. Testing add_private_note...")
            from src.tools.ticket.create_ticket_note import add_private_note
            
            result4 = await add_private_note(
                ticket_id="10679116294692864",
                content="Internal note: Customer may need additional training on network usage"
            )
            
            if result4.get("success"):
                print(f"✅ Success! Created private note ID: {result4.get('note_id')}")
                print(f"🔒 Private Note: {result4.get('privacy_type')} - {result4.get('content')[:50]}...")
            else:
                print(f"❌ Failed to create private note: {result4.get('error')}")
                
        else:
            print(f"❌ Failed to create ticket note: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Create Ticket Note Tool Test...")
    asyncio.run(test_create_ticket_note_tool())