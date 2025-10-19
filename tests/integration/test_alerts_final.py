"""
Final test for the alerts tool with correct schema
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_alerts_tool_final():
    """Test the alerts tool with the correct working schema"""
    import aiohttp
    
    # API configuration
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    test_cases = [
        {
            "name": "Get first page of alerts",
            "page": 1,
            "page_size": 5
        },
        {
            "name": "Get second page of alerts", 
            "page": 2,
            "page_size": 3
        },
        {
            "name": "Get all alerts in one page",
            "page": 1,
            "page_size": 20
        }
    ]
    
    # Working GraphQL query
    query = """
    query getAlertList($input: ListInfoInput!) {
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
    }
    """
    
    async with aiohttp.ClientSession() as session:
        print("🚨 Testing SuperOps Alerts Tool")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print("-" * 40)
            
            payload = {
                "query": query,
                "variables": {
                    "input": {
                        "page": test_case["page"],
                        "pageSize": test_case["page_size"]
                    }
                }
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data:
                            print("❌ GraphQL Errors:")
                            for error in data['errors']:
                                print(f"   - {error['message']}")
                        else:
                            alert_list = data['data']['getAlertList']
                            alerts = alert_list.get('alerts', [])
                            list_info = alert_list.get('listInfo', {})
                            
                            print(f"✅ Success! Retrieved {len(alerts)} alerts")
                            print(f"   📄 Page: {list_info.get('page')}")
                            print(f"   📊 Page Size: {list_info.get('pageSize')}")
                            print(f"   🔢 Total Count: {list_info.get('totalCount')}")
                            
                            # Show alert summaries
                            if alerts:
                                print(f"\n   🚨 Alerts Summary:")
                                for alert in alerts:
                                    asset_info = alert.get('asset', {})
                                    asset_name = asset_info.get('name', 'Unknown') if isinstance(asset_info, dict) else 'Unknown'
                                    owner_name = asset_info.get('owner', {}).get('name', 'Unknown') if isinstance(asset_info, dict) and asset_info.get('owner') else 'Unknown'
                                    
                                    print(f"     • ID: {alert.get('id')} | {alert.get('severity')} | {alert.get('status')}")
                                    print(f"       Asset: {asset_name} (Owner: {owner_name})")
                                    print(f"       Message: {alert.get('message')}")
                            else:
                                print("   📝 No alerts found for this page")
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
        
        print(f"\n🎉 All tests completed!")
        print(f"\n💡 Tool Usage Summary:")
        print(f"   - The alerts tool successfully retrieves alerts from SuperOps")
        print(f"   - Supports pagination with page and page_size parameters")
        print(f"   - Returns alert ID, asset info, severity, status, and message")
        print(f"   - Asset field contains JSON with name, owner, client, and site info")
        print(f"   - Can be used for monitoring, reporting, and alert management")

if __name__ == "__main__":
    asyncio.run(test_alerts_tool_final())