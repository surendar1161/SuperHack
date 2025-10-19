#!/usr/bin/env python3
"""
Test task creation using the existing SuperOps client
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

# Direct imports to avoid circular dependencies
from dotenv import load_dotenv
load_dotenv()

class SimpleConfig:
    """Simple configuration class"""
    def __init__(self):
        self.superops_api_key = os.getenv("SUPEROPS_API_KEY")
        self.superops_customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")

# Import the SuperOps client directly
import aiohttp
import json
from typing import Any, Dict

class SimpleSuperOpsClient:
    """Simplified SuperOps client for testing"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        self.api_url = "https://api.superops.ai/it"
        self.headers = {
            "Authorization": f"Bearer {self.config.superops_api_key}",
            "Content-Type": "application/json",
            "CustomerSubDomain": self.config.superops_customer_subdomain,
            "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
        }
    
    async def connect(self):
        """Initialize connection"""
        self.session = aiohttp.ClientSession()
        print("✅ Connected to SuperOps API")
    
    async def create_task(self, input_data):
        """Create a task using the working format"""
        try:
            mutation = {
                "query": """
                    mutation createTask($input: CreateTaskInput!) {
                        createTask(input: $input) {
                            taskId
                            title
                            description
                            status
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "title": input_data.get("title", "API Created Task"),
                        "description": input_data.get("description", "<p>Task created via API</p>"),
                        "estimatedTime": input_data.get("estimatedTime", 180),
                        "status": input_data.get("status", "In Progress"),
                        "scheduledStartDate": input_data.get("scheduledStartDate", "2025-10-17T00:00"),
                        "techGroup": {
                            "groupId": input_data.get("techGroupId", "6410137295585656832")
                        },
                        "technician": {
                            "userId": input_data.get("technicianId", "5066433879474626560")
                        },
                        "workItem": {
                            "workId": input_data.get("workId", "6028540472074190848"),
                            "module": input_data.get("module", "TICKET")
                        }
                    }
                }
            }
            
            print("📤 Sending GraphQL mutation...")
            print(f"📋 Mutation: {json.dumps(mutation, indent=2)}")
            
            async with self.session.post(
                self.api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                print(f"\n📡 Response Status: {response.status}")
                print(f"📡 Response Text: {response_text}")
                
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
                            print("=" * 60)
                            return task_result
                        else:
                            print("❌ createTask returned null")
                            return None
                    
                    elif "errors" in result:
                        print("❌ GraphQL Errors:")
                        for error in result["errors"]:
                            print(f"   • {error.get('message')}")
                        return None
                    
                    else:
                        print("❌ Unexpected response format")
                        print(json.dumps(result, indent=2))
                        return None
                
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

async def test_task_creation():
    """Test task creation"""
    print("🚀 SuperOps Task Creation Test via Client")
    print("=" * 60)
    
    config = SimpleConfig()
    client = SimpleSuperOpsClient(config)
    
    try:
        await client.connect()
        
        # Task data
        task_data = {
            "title": "Test Task via Client - API Integration",
            "description": "<p>This task was created using the SuperOps client to test task creation functionality.</p>",
            "estimatedTime": 120,
            "status": "In Progress",
            "scheduledStartDate": "2025-10-17T10:00",
            "techGroupId": "6410137295585656832",
            "technicianId": "5066433879474626560", 
            "workId": "6028540472074190848",
            "module": "TICKET"
        }
        
        print(f"📝 Creating task: {task_data['title']}")
        
        result = await client.create_task(task_data)
        
        if result:
            print(f"\n🎉 SUCCESS! Task created with ID: {result.get('taskId')}")
            return result
        else:
            print(f"\n💥 FAILED - Task creation unsuccessful")
            return None
            
    finally:
        await client.close()

async def main():
    """Main function"""
    print(f"🕐 Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = await test_task_creation()
    
    if result:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    asyncio.run(main())