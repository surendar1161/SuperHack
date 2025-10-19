#!/usr/bin/env python3
"""
Test SuperOps API connection with simple queries
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def test_superops_connection():
    """Test basic SuperOps API connection"""
    
    print("🚀 SuperOps API Connection Test")
    print("=" * 50)
    
    api_url = "https://api.superops.ai/it"
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print(f"🔧 API URL: {api_url}")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    
    # Test queries to try
    test_queries = [
        {
            "name": "Schema Introspection",
            "query": {"query": "{ __schema { types { name } } }"}
        },
        {
            "name": "Simple Type Query",
            "query": {"query": "{ __type(name: \"Task\") { name fields { name type { name } } } }"}
        },
        {
            "name": "Basic Query",
            "query": {"query": "query { __typename }"}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test in test_queries:
            print(f"\n🧪 Testing: {test['name']}")
            print(f"📤 Query: {test['query']}")
            
            try:
                async with session.post(
                    api_url,
                    json=test['query'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    response_text = await response.text()
                    print(f"📡 Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            
                            if "errors" in result:
                                print("❌ GraphQL Errors:")
                                for error in result["errors"]:
                                    print(f"   • {error.get('message')}")
                            else:
                                print("✅ Success!")
                                if test['name'] == "Simple Type Query" and "data" in result:
                                    # Print Task type fields if available
                                    task_type = result.get("data", {}).get("__type")
                                    if task_type and task_type.get("fields"):
                                        print("📋 Available Task fields:")
                                        for field in task_type["fields"][:10]:  # Show first 10 fields
                                            field_name = field.get("name")
                                            field_type = field.get("type", {}).get("name", "Unknown")
                                            print(f"   • {field_name}: {field_type}")
                                
                        except json.JSONDecodeError:
                            print(f"❌ Invalid JSON: {response_text}")
                    else:
                        print(f"❌ HTTP Error: {response_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
    
    # Now let's try to get some actual data
    print(f"\n🔍 Testing Data Queries")
    print("-" * 30)
    
    data_queries = [
        {
            "name": "Get Technicians",
            "query": {
                "query": """
                    query {
                        technicians {
                            userId
                            firstName
                            lastName
                        }
                    }
                """
            }
        },
        {
            "name": "Get Tech Groups", 
            "query": {
                "query": """
                    query {
                        techGroups {
                            groupId
                            groupName
                        }
                    }
                """
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test in data_queries:
            print(f"\n📊 Testing: {test['name']}")
            
            try:
                async with session.post(
                    api_url,
                    json=test['query'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    response_text = await response.text()
                    print(f"📡 Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_text)
                            
                            if "errors" in result:
                                print("❌ GraphQL Errors:")
                                for error in result["errors"]:
                                    print(f"   • {error.get('message')}")
                            elif "data" in result:
                                print("✅ Data retrieved!")
                                data = result["data"]
                                
                                if test['name'] == "Get Technicians" and "technicians" in data:
                                    techs = data["technicians"][:3]  # Show first 3
                                    print(f"👥 Found {len(data['technicians'])} technicians (showing first 3):")
                                    for tech in techs:
                                        print(f"   • {tech.get('userId')}: {tech.get('firstName')} {tech.get('lastName')}")
                                
                                elif test['name'] == "Get Tech Groups" and "techGroups" in data:
                                    groups = data["techGroups"][:3]  # Show first 3
                                    print(f"🏢 Found {len(data['techGroups'])} tech groups (showing first 3):")
                                    for group in groups:
                                        print(f"   • {group.get('groupId')}: {group.get('groupName')}")
                                
                        except json.JSONDecodeError:
                            print(f"❌ Invalid JSON: {response_text}")
                    else:
                        print(f"❌ HTTP Error: {response_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")

async def main():
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await test_superops_connection()
    print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())