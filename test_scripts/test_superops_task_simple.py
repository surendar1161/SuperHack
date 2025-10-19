#!/usr/bin/env python3
"""
Simple test script to create a task in SuperOps using direct API call
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_superops_task():
    """Create a task directly using SuperOps API"""
    
    print("🚀 SuperOps Task Creation Test - Direct API Call")
    print("=" * 60)
    
    # SuperOps API configuration
    api_url = "https://api.superops.ai/it"
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathon")
    
    if not api_key:
        print("❌ SUPEROPS_API_KEY not found in environment variables")
        return None
    
    print(f"🔧 API URL: {api_url}")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Headers for SuperOps API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Task creation mutation (using working format with required fields)
    mutation = {
        "query": """
            mutation createTask($input: CreateTaskInput!) {
                createTask(input: $input) {
                    taskId
                    title
                    description
                    status
                    estimatedTime
                }
            }
        """,
        "variables": {
            "input": {
                "title": "API Test Task - Direct Call",
                "description": "<p>This is a test task created via direct SuperOps API call to verify task creation functionality.</p>",
                "estimatedTime": 90,
                "status": "In Progress",
                "scheduledStartDate": "2025-10-17T00:00",
                "techGroup": {
                    "groupId": "6410137295585656832"
                },
                "technician": {
                    "userId": "5066433879474626560"
                },
                "workItem": {
                    "workId": "6028540472074190848",
                    "module": "TICKET"
                }
            }
        }
    }
    
    print("\n📝 Creating task with GraphQL mutation...")
    print(f"📋 Task Title: {mutation['variables']['input']['title']}")
    print(f"⏱️  Estimated Time: {mutation['variables']['input']['estimatedTime']} minutes")
    print(f"📊 Status: {mutation['variables']['input']['status']}")
    
    try:
        async with aiohttp.ClientSession() as session:
            print("\n🔄 Sending API request...")
            
            async with session.post(
                api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"📡 Response Status: {response.status}")
                print(f"📡 Response Headers: {dict(response.headers)}")
                
                response_text = await response.text()
                print(f"📡 Raw Response: {response_text}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        
                        print("\n" + "=" * 60)
                        print("✅ TASK CREATION SUCCESS!")
                        print("=" * 60)
                        
                        if "data" in result and result["data"] and "createTask" in result["data"]:
                            task_data = result["data"]["createTask"]
                            
                            print(f"🆔 Task ID: {task_data.get('taskId', 'N/A')}")
                            print(f"📝 Title: {task_data.get('title', 'N/A')}")
                            print(f"📄 Description: {task_data.get('description', 'N/A')}")
                            print(f"📊 Status: {task_data.get('status', 'N/A')}")
                            print(f"⏱️  Estimated Time: {task_data.get('estimatedTime', 'N/A')} minutes")
                            
                            print("=" * 60)
                            print("📊 Full Response Data:")
                            print(json.dumps(result, indent=2))
                            print("=" * 60)
                            
                            return task_data
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   • {error.get('message', 'Unknown error')}")
                                if 'locations' in error:
                                    print(f"     Location: {error['locations']}")
                                if 'path' in error:
                                    print(f"     Path: {error['path']}")
                            return None
                        
                        else:
                            print("❌ Unexpected response format:")
                            print(json.dumps(result, indent=2))
                            return None
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON response: {e}")
                        print(f"Raw response: {response_text}")
                        return None
                
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    return None
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

async def main():
    """Main function"""
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = await create_superops_task()
    
    if result:
        print(f"\n🎉 SUCCESS! Task created with ID: {result.get('taskId', 'Unknown')}")
    else:
        print(f"\n💥 FAILED - Task creation unsuccessful")

if __name__ == "__main__":
    asyncio.run(main())