#!/usr/bin/env python3
"""
Test the technicians API using the curl command provided
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_technicians_api():
    """Test the technicians API directly"""
    
    print("👥 Testing SuperOps Technicians API")
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
    api_url = "https://api.superops.ai/it"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=3264A8598BDD3B765EDBED6595B247BE; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL query (simplified to avoid undefined fields)
    query = {
        "query": """
            query getTechnicianList($input: ListInfoInput!) {
                getTechnicianList(input: $input) {
                    userList { 
                        userId
                        name 
                        email 
                        department
                    } 
                    listInfo { 
                        page 
                        pageSize
                        totalCount
                    }
                }
            }
        """,
        "variables": {
            "input": {
                "page": 1,
                "pageSize": 100,
                "condition": {
                    "attribute": "roles.roleId",
                    "operator": "is",
                    "value": 3
                }
            }
        }
    }
    
    print("📋 Request Details:")
    print(f"   URL: {api_url}")
    print(f"   Query: getTechnicianList")
    print(f"   Filter: Role ID = 3 (Technicians)")
    print(f"   Page Size: 100")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🚀 Sending request to SuperOps API...")
            
            async with session.post(
                api_url,
                json=query,
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
                        
                        # Extract technician data
                        if result and "data" in result and result["data"] and "getTechnicianList" in result["data"]:
                            technician_data = result["data"]["getTechnicianList"]
                            user_list = technician_data.get("userList", [])
                            list_info = technician_data.get("listInfo", {})
                            
                            print(f"📈 Results Summary:")
                            print(f"   Total Technicians: {len(user_list)}")
                            print(f"   Page: {list_info.get('page', 1)}")
                            print(f"   Page Size: {list_info.get('pageSize', 0)}")
                            print()
                            
                            if user_list:
                                print("👥 Technicians Found:")
                                print("-" * 30)
                                for i, tech in enumerate(user_list[:5], 1):  # Show first 5
                                    name = tech.get("name", "Unknown")
                                    email = tech.get("email", "No email")
                                    department = tech.get("department", "No department")
                                    user_id = tech.get("userId", "No userId")
                                    roles = tech.get("roles", [])
                                    
                                    print(f"   {i}. {name}")
                                    print(f"      User ID: {user_id}")
                                    print(f"      Email: {email}")
                                    print(f"      Department: {department}")
                                    print(f"      Roles: {roles}")
                                    print()
                                
                                if len(user_list) > 5:
                                    print(f"   ... and {len(user_list) - 5} more technicians")
                            else:
                                print("⚠️  No technicians found")
                        
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
    print("🎯 SuperOps Technicians API Test")
    print("Testing the getTechnicianList query")
    print()
    
    # Run the async test
    asyncio.run(test_technicians_api())