#!/usr/bin/env python3
"""
Test the updated SuperOps client with MSP API endpoints
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

async def test_updated_client():
    """Test the updated SuperOps client methods"""
    
    print("🔧 Testing Updated SuperOps Client")
    print("=" * 50)
    
    try:
        # Import after adding to path
        from clients.superops_client import SuperOpsClient
        
        # Initialize client
        client = SuperOpsClient()
        
        # Step 1: Get technicians
        print("👥 Step 1: Getting technicians...")
        technicians = await client.get_technicians()
        
        if technicians and len(technicians) > 0:
            technician = technicians[0]
            technician_id = technician.get('userId')
            technician_name = technician.get('name')
            print(f"✅ Found technician: {technician_name} (ID: {technician_id})")
        else:
            print("❌ No technicians found")
            return
        
        # Step 2: Create ticket
        print("\n🎟️ Step 2: Creating ticket...")
        ticket_data = {
            "subject": "Test Ticket - Updated Client",
            "description": "Testing the updated SuperOps client with MSP API",
            "requestType": "Incident"
        }
        
        ticket_result = await client.create_ticket(ticket_data)
        
        if ticket_result and ticket_result.get('id'):
            ticket_id = ticket_result['id']
            print(f"✅ Created ticket: {ticket_result.get('subject')} (ID: {ticket_id})")
        else:
            print("❌ Failed to create ticket")
            print(f"Result: {ticket_result}")
            return
        
        # Step 3: Update ticket to assign technician
        print(f"\n🔧 Step 3: Assigning technician to ticket...")
        update_data = {
            "technician": {
                "userId": technician_id
            }
        }
        
        update_result = await client.update_ticket(ticket_id, update_data)
        
        if update_result and update_result.get('id'):
            assigned_tech = update_result.get('technician', {})
            print(f"✅ Updated ticket successfully")
            print(f"   Ticket ID: {update_result.get('ticketId')}")
            print(f"   Subject: {update_result.get('subject')}")
            print(f"   Status: {update_result.get('status')}")
            if assigned_tech:
                print(f"   Assigned to: {assigned_tech.get('name')} ({assigned_tech.get('userId')})")
            
            print("\n🎉 All tests passed!")
            print("   ✓ Get technicians")
            print("   ✓ Create ticket")
            print("   ✓ Update ticket with technician assignment")
        else:
            print("❌ Failed to update ticket")
            print(f"Result: {update_result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_updated_client())