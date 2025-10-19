"""
Test script for the Get Alerts List tool
"""

import asyncio
import os
from dotenv import load_dotenv
from src.clients.superops_client import SuperOpsClient
from src.tools.alerts.get_alerts import GetAlertsListTool, GetAlertsListInput

# Load environment variables
load_dotenv()

async def test_get_alerts_list():
    """Test the get alerts list functionality"""
    
    # Initialize SuperOps client
    client = SuperOpsClient(
        api_key=os.getenv("SUPEROPS_API_KEY"),
        base_url=os.getenv("SUPEROPS_API_URL", "https://api.superops.ai/msp"),
        customer_subdomain=os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    )
    
    # Initialize the tool
    alerts_tool = GetAlertsListTool(client)
    
    try:
        print("Testing Get Alerts List Tool...")
        print("=" * 50)
        
        # Test with default parameters
        print("\n1. Testing with default parameters (page=1, page_size=10):")
        input_data = GetAlertsListInput()
        result = await alerts_tool.execute(input_data)
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Total alerts retrieved: {result['total_alerts']}")
            print(f"Pagination info: {result['pagination']}")
            
            if result['alerts']:
                print("\nFirst alert details:")
                first_alert = result['alerts'][0]
                for key, value in first_alert.items():
                    print(f"  {key}: {value}")
            else:
                print("No alerts found")
        else:
            print(f"Error: {result['error']}")
        
        # Test with custom parameters
        print("\n2. Testing with custom parameters (page=1, page_size=5):")
        input_data = GetAlertsListInput(page=1, page_size=5)
        result = await alerts_tool.execute(input_data)
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Total alerts retrieved: {result['total_alerts']}")
            print(f"Pagination info: {result['pagination']}")
        else:
            print(f"Error: {result['error']}")
        
        # Test pagination (page 2)
        print("\n3. Testing pagination (page=2, page_size=5):")
        input_data = GetAlertsListInput(page=2, page_size=5)
        result = await alerts_tool.execute(input_data)
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Total alerts retrieved: {result['total_alerts']}")
            print(f"Pagination info: {result['pagination']}")
        else:
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
    
    finally:
        # Clean up
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_get_alerts_list())