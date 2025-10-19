"""
Simple test script for the Get Alerts List tool without Strands dependency
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_alerts_api_directly():
    """Test the alerts API directly using aiohttp"""
    import aiohttp
    
    # API configuration from the curl command
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL query and variables (using only basic fields that exist)
    payload = {
        "query": """query getAlertList($input: ListInfoInput!) {
          getAlertList(input: $input) {
            alerts {
              asset
            }
            listInfo {
              page
            }
          }
        }""",
        "variables": {
            "input": {
                "page": 1,
                "pageSize": 10
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("Testing SuperOps Alerts API...")
            print("=" * 50)
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API call successful!")
                    print(f"Response data: {json.dumps(data, indent=2)}")
                    
                    # Parse the response
                    if 'data' in data and 'getAlertList' in data['data']:
                        alert_list = data['data']['getAlertList']
                        alerts = alert_list.get('alerts', [])
                        list_info = alert_list.get('listInfo', {})
                        
                        print(f"\n📊 Results Summary:")
                        print(f"   Total alerts found: {len(alerts)}")
                        print(f"   Current page: {list_info.get('page', 'N/A')}")
                        print(f"   Page size: {list_info.get('pageSize', 'N/A')}")
                        print(f"   Total count: {list_info.get('totalCount', 'N/A')}")
                        print(f"   Total pages: {list_info.get('totalPages', 'N/A')}")
                        
                        if alerts:
                            print(f"\n🚨 First Alert Details:")
                            first_alert = alerts[0]
                            for key, value in first_alert.items():
                                print(f"   {key}: {value}")
                        else:
                            print("\n📝 No alerts found")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API call failed with status {response.status}")
                    print(f"Error response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_alerts_api_directly())