"""
Test script to explore the alerts GraphQL schema
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_alerts_schema():
    """Test different field combinations to understand the schema"""
    import aiohttp
    
    # API configuration
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Test different field combinations
    test_queries = [
        {
            "name": "Basic fields",
            "query": """query getAlertList($input: ListInfoInput!) {
              getAlertList(input: $input) {
                alerts {
                  asset {
                    name
                    assetId
                  }
                }
                listInfo {
                  page
                  pageSize
                  totalCount
                }
              }
            }"""
        },
        {
            "name": "With alert ID and status",
            "query": """query getAlertList($input: ListInfoInput!) {
              getAlertList(input: $input) {
                alerts {
                  id
                  status
                  asset {
                    name
                    assetId
                  }
                }
                listInfo {
                  page
                  pageSize
                  totalCount
                }
              }
            }"""
        },
        {
            "name": "With severity and message",
            "query": """query getAlertList($input: ListInfoInput!) {
              getAlertList(input: $input) {
                alerts {
                  id
                  severity
                  message
                  asset {
                    name
                  }
                }
                listInfo {
                  page
                }
              }
            }"""
        }
    ]
    
    variables = {
        "input": {
            "page": 1,
            "pageSize": 5
        }
    }
    
    async with aiohttp.ClientSession() as session:
        for test in test_queries:
            print(f"\n{'='*50}")
            print(f"Testing: {test['name']}")
            print(f"{'='*50}")
            
            payload = {
                "query": test["query"],
                "variables": variables
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    print(f"Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data:
                            print("❌ Errors found:")
                            for error in data['errors']:
                                print(f"   - {error['message']}")
                        else:
                            print("✅ Success!")
                            if 'data' in data and data['data']:
                                alert_list = data['data']['getAlertList']
                                alerts = alert_list.get('alerts', [])
                                print(f"   Found {len(alerts)} alerts")
                                if alerts:
                                    print(f"   First alert keys: {list(alerts[0].keys())}")
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_alerts_schema())