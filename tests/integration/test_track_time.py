#!/usr/bin/env python3
"""
Test script for track_time tool with SuperOps API
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.tracking.track_time import track_time
from utils.logger import get_logger

logger = get_logger("test_track_time")

async def test_track_time():
    """Test the track_time tool with SuperOps API"""
    
    print("🧪 Testing track_time tool with SuperOps API...")
    print("=" * 60)
    
    try:
        # Test parameters
        test_params = {
            "ticket_id": "6028540472074190848",  # From the curl example
            "duration": 0.5,  # 30 minutes
            "description": "i am agent",  # As requested
            "activity_type": "Testing",
            "billable": True
        }
        
        print(f"📋 Test Parameters:")
        print(f"   Ticket ID: {test_params['ticket_id']}")
        print(f"   Duration: {test_params['duration']} hours (30 minutes)")
        print(f"   Description: {test_params['description']}")
        print(f"   Activity Type: {test_params['activity_type']}")
        print(f"   Billable: {test_params['billable']}")
        print()
        
        print("🚀 Calling track_time function...")
        
        # Call the track_time function
        result = await track_time(**test_params)
        
        print("📊 Result:")
        print("=" * 40)
        
        if result.get("success"):
            print("✅ SUCCESS!")
            print(f"   Timer ID: {result.get('timer_id')}")
            print(f"   Duration: {result.get('duration_formatted')}")
            print(f"   Billable: {result.get('billable')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get("data"):
                print(f"   API Response Data:")
                for key, value in result["data"].items():
                    print(f"     {key}: {value}")
        else:
            print("❌ FAILED!")
            print(f"   Error: {result.get('error')}")
            print(f"   Message: {result.get('message')}")
            
        print()
        print("🔍 Full Response:")
        print("-" * 40)
        import json
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 SuperOps Track Time API Test")
    print("Testing with 'i am agent' as notes")
    print()
    
    # Run the async test
    asyncio.run(test_track_time())