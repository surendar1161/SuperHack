#!/usr/bin/env python3
"""
Test the create KB article API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_article_api():
    """Test the create KB article API directly"""
    
    print("📚 Testing SuperOps Create KB Article API")
    print("=" * 50)
    
    # API configuration from environment
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
    
    if not api_key:
        print("❌ SUPEROPS_API_KEY not found in environment")
        return
    
    if not customer_subdomain:
        print("❌ SUPEROPS_CUSTOMER_SUBDOMAIN not found in environment")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print()
    
    # API endpoint and headers
    api_url = "https://api.superops.ai/msp"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=057178D0A7F0670BC8DB1B9E44498289; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL mutation from the curl command
    mutation = {
        "query": """mutation ($input: CreateKbArticleInput!) {
            createKbArticle(input: $input) {
                itemId
                name
                description
                status
                parent {itemId}
                createdBy
                createdOn
                lastModifiedBy
                lastModifiedOn
                viewCount
                articleType
                visibility { site}
                loginRequired
            }
        }""",
        "variables": {
            "input": {
                "name": "IT Troubleshooting Guide - API Test",
                "status": "DRAFT",
                "parent": {
                    "itemId": "8768135920619339720"
                },
                "visibility": {
                    "added": [
                        {
                            "clientSharedType": "AllClients",
                            "siteSharedType": "AllSites",
                            "portalType": "TECHNICIAN",
                            "userSharedType": "User",
                            "groupSharedType": "AllGroups",
                            "addedUserIds": ["8275806997713629184"]
                        }
                    ]
                },
                "content": "<h2>IT Troubleshooting Guide</h2><p dir=\"auto\">This comprehensive guide covers common IT issues and their solutions.</p><h3>Network Connectivity Issues</h3><ol><li>Check physical connections</li><li>Verify network settings</li><li>Test with different devices</li><li>Contact network administrator if needed</li></ol><h3>Software Installation Problems</h3><ol><li>Verify system requirements</li><li>Run as administrator</li><li>Check for conflicting software</li><li>Consult software documentation</li></ol>",
                "loginRequired": True
            }
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Mutation: createKbArticle")
    print(f"   Article Name: IT Troubleshooting Guide - API Test")
    print(f"   Parent ID: 8768135920619339720")
    print(f"   Status: DRAFT")
    print(f"   Login Required: True")
    print(f"   User ID: 8275806997713629184")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps API...")
            
            async with session.post(
                api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                print("📊 Response:")
                print("=" * 40)
                print(f"Status Code: {response.status}")
                print()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print("✅ SUCCESS!")
                        print("Raw Response JSON:")
                        print(json.dumps(result, indent=2))
                        print()
                        
                        # Extract article data
                        if result and "data" in result and result["data"] and "createKbArticle" in result["data"]:
                            article = result["data"]["createKbArticle"]
                            
                            print(f"📈 KB Article Creation Results:")
                            print(f"   Article ID: {article.get('itemId', 'N/A')}")
                            print(f"   Name: {article.get('name', 'N/A')}")
                            print(f"   Description: {article.get('description', 'N/A')}")
                            print(f"   Status: {article.get('status', 'N/A')}")
                            print(f"   Login Required: {article.get('loginRequired', 'N/A')}")
                            print(f"   View Count: {article.get('viewCount', 'N/A')}")
                            print(f"   Article Type: {article.get('articleType', 'N/A')}")
                            
                            # Show parent info
                            parent_info = article.get('parent', {})
                            if parent_info:
                                print(f"   Parent ID: {parent_info.get('itemId', 'N/A')}")
                            
                            # Show visibility info
                            visibility_info = article.get('visibility', {})
                            if visibility_info:
                                print(f"   Visibility: {visibility_info}")
                            
                            # Show creation info
                            print(f"   Created By: {article.get('createdBy', 'N/A')}")
                            print(f"   Created On: {article.get('createdOn', 'N/A')}")
                            print(f"   Last Modified By: {article.get('lastModifiedBy', 'N/A')}")
                            print(f"   Last Modified On: {article.get('lastModifiedOn', 'N/A')}")
                            
                            print(f"\n🎉 KB Article created successfully!")
                            
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   - {error.get('message', error)}")
                        else:
                            print("❌ Unexpected response format")
                            print(json.dumps(result, indent=2))
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON response: {e}")
                        print(f"Raw response: {response_text}")
                        
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎯 SuperOps Create KB Article API Test")
    print("Testing the createKbArticle mutation")
    print()
    
    # Run the async test
    asyncio.run(test_create_article_api())