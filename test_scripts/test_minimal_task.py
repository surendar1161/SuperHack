#!/usr/bin/env python3
"""
Test creating a task with minimal required fields
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def create_minimal_task():
    """Create a task with minimal fields to see what's required"""
    
    api_url = "https://api.superops.ai/it"
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print("🚀 SuperOps Minimal Task Creation Test")
    print("=" * 50)
    
    # Try with just the basic required fields
    minimal_task_tests = [
        {
            "name": "Only Title",
            "input": {
                "title": "Minimal Test Task 1"
            }
        },
        {
            "name": "Title + Description",
            "input": {
                "title": "Minimal Test Task 2",
                "description": "<p>Simple test task</p>"
            }
        },
        {
            "name": "Title + Description + Status",
            "input": {
                "title": "Minimal Test Task 3",
                "description": "<p>Test task with status</p>",
                "status": "In Progress"
            }
        },
        {
            "name": "Title + Description + Status + Time",
            "input": {
                "title": "Minimal Test Task 4",
                "description": "<p>Test task with time</p>",
                "status": "In Progress",
                "estimatedTime": 30
            }
        },
        {
            "name": "All Basic Fields",
            "input": {
                "title": "Minimal Test Task 5",
                "description": "<p>Test task with all basic fields</p>",
                "status": "In Progress",
                "estimatedTime": 45,
                "scheduledStartDate": "2025-10-17T16:00"
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        
        for test in minimal_task_tests:
            print(f"\n🧪 Testing: {test['name']}")
            print(f"📋 Input: {json.dumps(test['input'], indent=2)}")
            
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
                    "input": test['input']
                }
            }
            
            try:
                async with session.post(
                    api_url,
                    json=mutation,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    
                    response_text = await response.text()
                    print(f"📡 Status: {response.status}")
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        
                        if "data" in result and result["data"] and "createTask" in result["data"]:
                            task_result = result["data"]["createTask"]
                            if task_result:
                                print("✅ SUCCESS! Task created:")
                                print(f"   🆔 Task ID: {task_result.get('taskId')}")
                                print(f"   📝 Title: {task_result.get('title')}")
                                print(f"   📊 Status: {task_result.get('status')}")
                                print(f"   ⏱️  Time: {task_result.get('estimatedTime')} min")
                                
                                # Log the successful creation
                                print("\n" + "=" * 60)
                                print("🎉 TASK CREATION SUCCESSFUL!")
                                print("=" * 60)
                                print(f"Task ID: {task_result.get('taskId')}")
                                print(f"Title: {task_result.get('title')}")
                                print(f"Description: {task_result.get('description')}")
                                print(f"Status: {task_result.get('status')}")
                                print(f"Estimated Time: {task_result.get('estimatedTime')} minutes")
                                print(f"Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                print("=" * 60)
                                
                                return task_result
                            else:
                                print("❌ createTask returned null")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   • {error.get('message')}")
                                if 'extensions' in error:
                                    print(f"     Type: {error['extensions'].get('classification')}")
                        
                        else:
                            print("❌ Unexpected response:")
                            print(json.dumps(result, indent=2))
                    
                    else:
                        print(f"❌ HTTP Error: {response_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
            
            print("-" * 30)
    
    print("\n💥 All tests failed - no task could be created")
    return None

async def main():
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = await create_minimal_task()
    
    if result:
        print(f"\n🎉 SUCCESS! Task created with ID: {result.get('taskId')}")
    else:
        print(f"\n❌ All task creation attempts failed")

if __name__ == "__main__":
    asyncio.run(main())