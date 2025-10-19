#!/usr/bin/env python3
"""
Get real IDs from SuperOps to use for task creation
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def get_real_ids():
    """Get real technician and group IDs from SuperOps"""
    
    api_url = "https://api.superops.ai/it"
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print("🔍 Getting Real IDs from SuperOps")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Get technicians
        print("👥 Getting technicians...")
        tech_query = {
            "query": """
                query {
                    getTechnicianList {
                        technicians {
                            userId
                            firstName
                            lastName
                            email
                        }
                    }
                }
            """
        }
        
        async with session.post(api_url, json=tech_query, headers=headers) as response:
            response_text = await response.text()
            print(f"📡 Technician response: {response_text}")
            
            if response.status == 200:
                try:
                    result = json.loads(response_text)
                    
                    if result and "data" in result and result["data"] and "getTechnicianList" in result["data"]:
                        techs = result["data"]["getTechnicianList"]["technicians"]
                        print(f"✅ Found {len(techs)} technicians:")
                        
                        for i, tech in enumerate(techs[:5]):  # Show first 5
                            print(f"   {i+1}. {tech['userId']}: {tech['firstName']} {tech['lastName']} ({tech['email']})")
                        
                        if techs:
                            first_tech_id = techs[0]['userId']
                            print(f"\n🎯 Using technician ID: {first_tech_id}")
                        else:
                            first_tech_id = None
                    elif result and "errors" in result:
                        print("❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   • {error.get('message')}")
                        first_tech_id = None
                    else:
                        print("❌ No technicians found or unexpected response format")
                        print(f"Response: {result}")
                        first_tech_id = None
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    first_tech_id = None
            else:
                print(f"❌ Failed to get technicians: {response.status}")
                first_tech_id = None
        
        # Get tech groups
        print(f"\n🏢 Getting tech groups...")
        group_query = {
            "query": """
                query {
                    getTechnicianGroupList {
                        technicianGroups {
                            groupId
                            groupName
                            description
                        }
                    }
                }
            """
        }
        
        async with session.post(api_url, json=group_query, headers=headers) as response:
            if response.status == 200:
                result = json.loads(await response.text())
                
                if "data" in result and "getTechnicianGroupList" in result["data"]:
                    groups = result["data"]["getTechnicianGroupList"]["technicianGroups"]
                    print(f"✅ Found {len(groups)} tech groups:")
                    
                    for i, group in enumerate(groups[:5]):  # Show first 5
                        print(f"   {i+1}. {group['groupId']}: {group['groupName']}")
                    
                    if groups:
                        first_group_id = groups[0]['groupId']
                        print(f"\n🎯 Using group ID: {first_group_id}")
                else:
                    print("❌ No tech groups found")
                    first_group_id = None
            else:
                print(f"❌ Failed to get tech groups: {response.status}")
                first_group_id = None
        
        # Get tasks to see workItem structure
        print(f"\n📋 Getting existing tasks to understand workItem structure...")
        task_query = {
            "query": """
                query {
                    getTaskList {
                        tasks {
                            taskId
                            title
                            workItem {
                                workId
                                module
                            }
                        }
                    }
                }
            """
        }
        
        async with session.post(api_url, json=task_query, headers=headers) as response:
            if response.status == 200:
                result = json.loads(await response.text())
                
                if "data" in result and "getTaskList" in result["data"]:
                    tasks = result["data"]["getTaskList"]["tasks"]
                    print(f"✅ Found {len(tasks)} existing tasks:")
                    
                    work_items = []
                    for i, task in enumerate(tasks[:5]):  # Show first 5
                        work_item = task.get('workItem', {})
                        work_id = work_item.get('workId', 'N/A')
                        module = work_item.get('module', 'N/A')
                        print(f"   {i+1}. {task['taskId']}: {task['title'][:50]}...")
                        print(f"      WorkItem: {work_id} (module: {module})")
                        
                        if work_id != 'N/A':
                            work_items.append(work_item)
                    
                    if work_items:
                        first_work_item = work_items[0]
                        print(f"\n🎯 Using workItem: {first_work_item}")
                else:
                    print("❌ No tasks found")
                    first_work_item = None
            else:
                print(f"❌ Failed to get tasks: {response.status}")
                first_work_item = None
        
        # Now try to create a task with real IDs
        if first_tech_id and first_group_id:
            print(f"\n🚀 Creating task with real IDs...")
            
            create_task_mutation = {
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
                        "title": "API Test Task - Real IDs",
                        "description": "<p>Task created with real IDs from SuperOps system</p>",
                        "estimatedTime": 60,
                        "status": "In Progress",
                        "scheduledStartDate": "2025-10-17T15:00",
                        "technician": {
                            "userId": first_tech_id
                        },
                        "techGroup": {
                            "groupId": first_group_id
                        }
                    }
                }
            }
            
            # Add workItem if we have one
            if first_work_item:
                create_task_mutation["variables"]["input"]["workItem"] = first_work_item
            
            print(f"📤 Sending task creation with real IDs...")
            print(f"👤 Technician: {first_tech_id}")
            print(f"🏢 Group: {first_group_id}")
            if first_work_item:
                print(f"📋 WorkItem: {first_work_item}")
            
            async with session.post(api_url, json=create_task_mutation, headers=headers) as response:
                response_text = await response.text()
                print(f"\n📡 Response Status: {response.status}")
                print(f"📡 Response: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and result["data"] and "createTask" in result["data"]:
                        task_result = result["data"]["createTask"]
                        if task_result:
                            print("\n" + "=" * 60)
                            print("✅ TASK CREATED SUCCESSFULLY!")
                            print("=" * 60)
                            print(f"🆔 Task ID: {task_result.get('taskId')}")
                            print(f"📝 Title: {task_result.get('title')}")
                            print(f"📄 Description: {task_result.get('description')}")
                            print(f"📊 Status: {task_result.get('status')}")
                            print(f"⏱️  Estimated Time: {task_result.get('estimatedTime')} minutes")
                            print("=" * 60)
                            return task_result
                        else:
                            print("❌ createTask returned null")
                    
                    elif "errors" in result:
                        print("❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   • {error.get('message')}")
                    
                    else:
                        print("❌ Unexpected response format")
                        print(json.dumps(result, indent=2))
                
                else:
                    print(f"❌ HTTP Error: {response.status}")
        
        else:
            print("❌ Could not get required IDs for task creation")

async def main():
    await get_real_ids()

if __name__ == "__main__":
    asyncio.run(main())