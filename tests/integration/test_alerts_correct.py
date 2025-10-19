"""
Test script with correct alerts schema
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_alerts_correct_schema():
    """Test with the correct schema format"""
    import aiohttp
    
    # API configuration
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Correct query format - asset is a JSON field, not an object
    payload = {
        "query": """query getAlertList($input: ListInfoInput!) {
          getAlertList(input: $input) {
            alerts {
              id
              asset
              severity
              status
              message
            }
            listInfo {
              page
              pageSize
              totalCount
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
            print("Testing SuperOps Alerts API with correct schema...")
            print("=" * 60)
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data:
                        print("❌ Errors found:")
                        for error in data['errors']:
                            print(f"   - {error['message']}")
                    else:
                        print("✅ API call successful!")
                        
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
                            
                            if alerts:
                                print(f"\n🚨 Alert Details:")
                                for i, alert in enumerate(alerts[:3], 1):  # Show first 3 alerts
                                    print(f"\n   Alert {i}:")
                                    print(f"     ID: {alert.get('id', 'N/A')}")
                                    print(f"     Severity: {alert.get('severity', 'N/A')}")
                                    print(f"     Status: {alert.get('status', 'N/A')}")
                                    print(f"     Message: {alert.get('message', 'N/A')}")
                                    
                                    # Parse asset JSON if it exists
                                    asset = alert.get('asset')
                                    if asset:
                                        if isinstance(asset, dict):
                                            asset_name = asset.get('name', 'Unknown')
                                            asset_id = asset.get('assetId', 'Unknown')
                                            owner_name = asset.get('owner', {}).get('name', 'Unknown') if asset.get('owner') else 'Unknown'
                                        else:
                                            asset_name = str(asset)
                                            asset_id = 'Unknown'
                                            owner_name = 'Unknown'
                                        
                                        print(f"     Asset: {asset_name} (ID: {asset_id})")
                                        print(f"     Owner: {owner_name}")
                            else:
                                print("\n📝 No alerts found")
                        
                        print(f"\n📋 Full Response:")
                        print(json.dumps(data, indent=2))
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API call failed with status {response.status}")
                    print(f"Error response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_alerts_correct_schema())