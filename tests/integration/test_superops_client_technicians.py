#!/usr/bin/env python3
"""
Test the SuperOps client get_technicians method
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from clients.superops_client import SuperOpsClient

# Load environment variables
load_dotenv()

async def test_superops_client_technicians():
    """Test the SuperOps client get_technicians method"""
    
    print("🔧 Testing SuperOps Client - get_technicians method")
    print("=" * 60)
    
    # Initialize client
    client = SuperOpsClient()
    
    try:
        print("🚀 Calling get_technicians()...")
        technicians = await client.get_technicians()
        
        print(f"✅ SUCCESS! Found {len(technicians)} technicians")
        print()
        
        if technicians:
            print("👥 Technicians:")
            print("-" * 40)
            for i, tech in enumerate(technicians, 1):
                print(f"   {i}. {tech.get('name', 'Unknown')}")
                print(f"      User ID: {tech.get('userId', 'N/A')}")
                print(f"      Email: {tech.get('email', 'N/A')}")
                print(f"      Department: {tech.get('department', 'N/A')}")
                print()
        else:
            print("⚠️  No technicians found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_superops_client_technicians())