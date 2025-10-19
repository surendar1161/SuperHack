#!/usr/bin/env python3
"""
Test SuperOps GraphQL schema to find correct field names
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def explore_schema():
    """Explore SuperOps GraphQL schema"""
    
    api_url = "https://api.superops.ai/it"
    api_key = os.getenv("SUPEROPS_API_KEY")
    customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN", "hackathonsuperhack")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print("🔍 Exploring SuperOps GraphQL Schema")
    print("=" * 50)
    
    # Get Query type fields
    query_fields_query = {
        "query": """
            {
                __schema {
                    queryType {
                        fields {
                            name
                            description
                            type {
                                name
                                kind
                            }
                        }
                    }
                }
            }
        """
    }
    
    async with aiohttp.ClientSession() as session:
        print("📋 Getting available Query fields...")
        
        async with session.post(
            api_url,
            json=query_fields_query,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15)
        ) as response:
            
            if response.status == 200:
                result = json.loads(await response.text())
                
                if "data" in result and result["data"]["__schema"]["queryType"]["fields"]:
                    fields = result["data"]["__schema"]["queryType"]["fields"]
                    
                    print(f"✅ Found {len(fields)} Query fields:")
                    
                    # Look for relevant fields
                    relevant_fields = []
                    for field in fields:
                        field_name = field["name"]
                        if any(keyword in field_name.lower() for keyword in ["task", "tech", "user", "group", "work"]):
                            relevant_fields.append(field)
                    
                    print(f"\n🎯 Relevant fields ({len(relevant_fields)}):")
                    for field in relevant_fields[:10]:  # Show first 10
                        print(f"   • {field['name']}: {field.get('type', {}).get('name', 'Unknown')}")
                    
                    # Look for mutation fields
                    print(f"\n🔍 Looking for Mutation fields...")
                    
        # Get Mutation type fields
        mutation_fields_query = {
            "query": """
                {
                    __schema {
                        mutationType {
                            fields {
                                name
                                description
                                type {
                                    name
                                }
                            }
                        }
                    }
                }
            """
        }
        
        async with session.post(
            api_url,
            json=mutation_fields_query,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15)
        ) as response:
            
            if response.status == 200:
                result = json.loads(await response.text())
                
                if "data" in result and result["data"]["__schema"]["mutationType"]["fields"]:
                    fields = result["data"]["__schema"]["mutationType"]["fields"]
                    
                    print(f"\n🔧 Found {len(fields)} Mutation fields:")
                    
                    # Look for task-related mutations
                    task_mutations = []
                    for field in fields:
                        field_name = field["name"]
                        if "task" in field_name.lower():
                            task_mutations.append(field)
                    
                    print(f"\n🎯 Task-related mutations ({len(task_mutations)}):")
                    for field in task_mutations:
                        print(f"   • {field['name']}: {field.get('type', {}).get('name', 'Unknown')}")
        
        # Get CreateTaskInput details
        print(f"\n🔍 Getting CreateTaskInput details...")
        
        input_type_query = {
            "query": """
                {
                    __type(name: "CreateTaskInput") {
                        name
                        inputFields {
                            name
                            type {
                                name
                                kind
                                ofType {
                                    name
                                }
                            }
                            defaultValue
                        }
                    }
                }
            """
        }
        
        async with session.post(
            api_url,
            json=input_type_query,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15)
        ) as response:
            
            if response.status == 200:
                result = json.loads(await response.text())
                
                if "data" in result and result["data"]["__type"]:
                    input_type = result["data"]["__type"]
                    
                    if input_type and "inputFields" in input_type:
                        fields = input_type["inputFields"]
                        
                        print(f"\n📋 CreateTaskInput fields ({len(fields)}):")
                        for field in fields:
                            field_name = field["name"]
                            field_type = field.get("type", {})
                            type_name = field_type.get("name") or field_type.get("ofType", {}).get("name", "Unknown")
                            default_val = field.get("defaultValue", "None")
                            
                            print(f"   • {field_name}: {type_name} (default: {default_val})")

async def main():
    await explore_schema()

if __name__ == "__main__":
    asyncio.run(main())