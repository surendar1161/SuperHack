#!/usr/bin/env python3
"""
Test the Strands-compatible tools with the updated SuperOps client
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

async def test_strands_tools():
    """Test the Strands-compatible tools"""
    
    print("🛠️ Testing Strands Tools")
    print("=" * 40)
    
    try:
        # Import tools
        from tools.ticket.create_ticket import create_ticket
        from tools.ticket.update_ticket import update_ticket
        from tools.user.get_technicians import get_technicians
        
        # Step 1: Get technicians
        print("👥 Step 1: Testing get_technicians tool...")
        technicians_result = await get_technicians()
        
        if technicians_result.get('success') and technicians_result.get('technicians'):
            technicians = technicians_result['technicians']
            technician = technicians[0]
            technician_id = technician.get('userId')
            technician_name = technician.get('name')
            print(f"✅ Found {len(technicians)} technicians")
            print(f"   First technician: {technician_name} (ID: {technician_id})")
        else:
            print("❌ Failed to get technicians")
            print(f"Result: {technicians_result}")
            return
        
        # Step 2: Create ticket with auto-assignment
        print("\n🎟️ Step 2: Testing create_ticket tool...")
        create_result = await create_ticket(
            title="Test Ticket - Strands Tools",
            description="Testing the Strands-compatible tools with updated SuperOps client",
            priority="MEDIUM",
            auto_assign=True
        )
        
        if create_result.get('success'):
            ticket_id = create_result.get('ticket_id')
            assigned_to = create_result.get('assigned_to')
            print(f"✅ Created ticket: {create_result.get('title')}")
            print(f"   Ticket ID: {ticket_id}")
            print(f"   Auto-assigned to: {create_result.get('assigned_technician_name', assigned_to)}")
        else:
            print("❌ Failed to create ticket")
            print(f"Error: {create_result.get('error')}")
            return
        
        # Step 3: Update ticket
        print(f"\n🔧 Step 3: Testing update_ticket tool...")
        update_result = await update_ticket(
            ticket_id=ticket_id,
            status="IN_PROGRESS",
            notes="Updated via Strands tools test"
        )
        
        if update_result.get('success'):
            print(f"✅ Updated ticket successfully")
            print(f"   Updated fields: {update_result.get('updated_fields')}")
            
            print("\n🎉 All Strands tools tests passed!")
            print("   ✓ get_technicians tool")
            print("   ✓ create_ticket tool with auto-assignment")
            print("   ✓ update_ticket tool")
        else:
            print("❌ Failed to update ticket")
            print(f"Error: {update_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_strands_tools())