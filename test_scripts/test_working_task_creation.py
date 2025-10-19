#!/usr/bin/env python3
"""
Test task creation using the working SuperOps client implementation
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def test_working_task_creation():
    """Test task creation using the exact working format from SuperOps client"""
    
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    # Use the exact working format from the SuperOps client
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Use the exact working mutation from the client
    mutation = {
        "query": """
            mutation createTask($input: CreateTaskInput!) {
                createTask(input: $input) {
                    taskId
                    title
                    description
                    status
                    estimatedTime
                    scheduledStartDate
                }
            }
        """,
        "variables": {
            "input": {
                "title": "API Test Task - Working Format",
                "description": "<p>This task was created using the working SuperOps client format to test task creation functionality.</p>",
                "estimatedTime": 120,
                "status": "In Progress",
                "scheduledStartDate": "2025-10-17T16:00",
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
    
    # Use IT API endpoint for tasks
    it_api_url = "https://api.superops.ai/it"
    
    print("📋 SuperOps Task Creation Test - Working Format")
    print("=" * 60)
    print(f"🔧 API URL: {it_api_url}")
    print(f"🏢 Customer Subdomain: {customer_subdomain}")
    print(f"📝 Title: {mutation['variables']['input']['title']}")
    print(f"⏱️  Estimated Time: {mutation['variables']['input']['estimatedTime']} minutes")
    print(f"📊 Status: {mutation['variables']['input']['status']}")
    print(f"📅 Scheduled Start: {mutation['variables']['input']['scheduledStartDate']}")
    print(f"👤 Technician ID: {mutation['variables']['input']['technician']['userId']}")
    print(f"🏢 Tech Group ID: {mutation['variables']['input']['techGroup']['groupId']}")
    print(f"📋 Work Item ID: {mutation['variables']['input']['workItem']['workId']}")
    
    async with aiohttp.ClientSession() as session:
        
        print(f"\n🚀 Creating task using working format...")
        
        try:
            async with session.post(
                it_api_url,
                json=mutation,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                print(f"\n📡 Response Status: {response.status}")
                print(f"📡 Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        print(f"📡 Parsed Response: {json.dumps(result, indent=2)}")
                        
                        if "data" in result and result["data"] and "createTask" in result["data"]:
                            create_result = result["data"]["createTask"]
                            
                            if create_result:
                                print("\n" + "=" * 60)
                                print("✅ TASK CREATED SUCCESSFULLY!")
                                print("=" * 60)
                                print(f"🆔 Task ID: {create_result.get('taskId')}")
                                print(f"📝 Title: {create_result.get('title')}")
                                print(f"📄 Description: {create_result.get('description')}")
                                print(f"📊 Status: {create_result.get('status')}")
                                print(f"⏱️  Estimated Time: {create_result.get('estimatedTime')} minutes")
                                print(f"📅 Scheduled Start: {create_result.get('scheduledStartDate')}")
                                print(f"📅 Created At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                print("=" * 60)
                                
                                # Log the successful creation
                                print("\n📋 LOGGING TASK CREATION SUCCESS:")
                                print("-" * 40)
                                print(f"SUCCESS: Task created via SuperOps IT API")
                                print(f"Task ID: {create_result.get('taskId')}")
                                print(f"Title: {create_result.get('title')}")
                                print(f"Status: {create_result.get('status')}")
                                print(f"Estimated Time: {create_result.get('estimatedTime')} minutes")
                                print(f"API Endpoint: {it_api_url}")
                                print(f"Timestamp: {datetime.now().isoformat()}")
                                print("-" * 40)
                                
                                return create_result
                            else:
                                print("❌ createTask returned null")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   • {error.get('message')}")
                                if 'extensions' in error:
                                    print(f"     Type: {error['extensions'].get('classification')}")
                                if 'locations' in error:
                                    print(f"     Location: Line {error['locations'][0].get('line')}, Column {error['locations'][0].get('column')}")
                        
                        else:
                            print("❌ Unexpected response format")
                            print(json.dumps(result, indent=2))
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"Raw response: {response_text}")
                
                else:
                    print(f"❌ HTTP Error {response.status}")
                    print(f"Response: {response_text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    return None

async def test_minimal_task_creation():
    """Test task creation with minimal required fields"""
    
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Try with minimal fields first
    minimal_tests = [
        {
            "name": "Minimal Required Fields",
            "input": {
                "title": "Minimal Task Test",
                "description": "<p>Minimal task for testing</p>",
                "status": "In Progress"
            }
        },
        {
            "name": "With Estimated Time",
            "input": {
                "title": "Task with Time",
                "description": "<p>Task with estimated time</p>",
                "status": "In Progress",
                "estimatedTime": 60
            }
        },
        {
            "name": "With Schedule Date",
            "input": {
                "title": "Scheduled Task",
                "description": "<p>Task with schedule</p>",
                "status": "In Progress",
                "estimatedTime": 90,
                "scheduledStartDate": "2025-10-17T17:00"
            }
        }
    ]
    
    it_api_url = "https://api.superops.ai/it"
    
    print(f"\n🧪 Testing Minimal Task Creation")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        for test in minimal_tests:
            print(f"\n📋 Testing: {test['name']}")
            print(f"📝 Input: {json.dumps(test['input'], indent=2)}")
            
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
                    it_api_url,
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
                                print("✅ SUCCESS! Minimal task created:")
                                print(f"   🆔 Task ID: {task_result.get('taskId')}")
                                print(f"   📝 Title: {task_result.get('title')}")
                                print(f"   📊 Status: {task_result.get('status')}")
                                
                                # Log success
                                print("\n📋 LOGGING MINIMAL TASK SUCCESS:")
                                print("-" * 30)
                                print(f"SUCCESS: Minimal task created")
                                print(f"Task ID: {task_result.get('taskId')}")
                                print(f"Title: {task_result.get('title')}")
                                print(f"Status: {task_result.get('status')}")
                                print("-" * 30)
                                
                                return task_result
                            else:
                                print("❌ createTask returned null")
                        
                        elif "errors" in result:
                            print("❌ GraphQL Errors:")
                            for error in result["errors"]:
                                print(f"   • {error.get('message')}")
                        
                    else:
                        print(f"❌ HTTP Error: {response_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
            
            print("-" * 30)
    
    return None

async def main():
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Full working format
    print("🔧 Test 1: Full Working Format")
    result1 = await test_working_task_creation()
    
    # Test 2: Minimal format
    print("\n🔧 Test 2: Minimal Format")
    result2 = await test_minimal_task_creation()
    
    if result1 or result2:
        print(f"\n🎉 SUCCESS! Task creation is working!")
        if result1:
            print(f"✅ Full Format Task ID: {result1.get('taskId')}")
        if result2:
            print(f"✅ Minimal Format Task ID: {result2.get('taskId')}")
    else:
        print(f"\n❌ Task creation failed in both formats")

if __name__ == "__main__":
    asyncio.run(main())