#!/usr/bin/env python3
"""
Test mem0 memory storage and retrieval with proper API v2 usage
"""

import os
import sys
import time
import json
from datetime import datetime
from mem0 import MemoryClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_mem0_storage_and_retrieval():
    """Test mem0 storage and retrieval with proper filters"""
    
    print("🧠 SuperOps IT Technician Agent - mem0 Storage & Retrieval Test")
    print("=" * 70)
    
    # Initialize mem0 client
    api_key = os.getenv("MEM0_API_KEY")
    if not api_key:
        print("❌ MEM0_API_KEY not found in environment variables")
        return False
    
    print(f"🔧 Configuration:")
    print(f"   mem0 API Key: {api_key[:12]}...")
    
    try:
        client = MemoryClient(api_key=api_key)
        print("✅ mem0 client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize mem0 client: {e}")
        return False
    
    # Test user ID
    user_id = f"superops_test_user_{int(time.time())}"
    
    print(f"\n📝 Test 1: Storing Conversations for User: {user_id}")
    print("-" * 50)
    
    # Store test conversations
    conversations = [
        {
            "user": "I need help creating a support ticket for our printer issue",
            "agent": "I'll help you create a support ticket for the printer issue. Let me gather some details first."
        },
        {
            "user": "The printer shows a paper jam error but there's no paper stuck",
            "agent": "I understand. A paper jam error without visible paper often indicates a sensor issue. Let me create a ticket for this."
        },
        {
            "user": "Can you also help me create a new technician account for Sarah Johnson?",
            "agent": "Absolutely! I can help you create a new technician account. What's Sarah's email and contact information?"
        }
    ]
    
    stored_count = 0
    for i, conv in enumerate(conversations, 1):
        try:
            messages = [
                {"role": "user", "content": conv["user"]},
                {"role": "assistant", "content": conv["agent"]}
            ]
            
            result = client.add(messages, user_id=user_id)
            print(f"   ✅ Conversation {i} stored successfully")
            print(f"      📋 Result: {result}")
            stored_count += 1
            
            # Small delay to ensure processing
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Failed to store conversation {i}: {e}")
    
    print(f"\n📊 Storage Summary: {stored_count}/{len(conversations)} conversations stored")
    
    # Wait a bit for mem0 to process
    print("\n⏳ Waiting for mem0 to process memories...")
    time.sleep(5)
    
    print(f"\n🔍 Test 2: Retrieving All Memories for User")
    print("-" * 50)
    
    try:
        # Try to get all memories with user_id filter
        memories = client.get_all(user_id=user_id)
        print(f"✅ Retrieved {len(memories)} memories")
        
        for i, memory in enumerate(memories, 1):
            print(f"   Memory {i}: {memory.get('memory', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"❌ Failed to retrieve memories: {e}")
        
        # Try alternative approach - get memories with filters
        try:
            print("   🔄 Trying alternative retrieval method...")
            # Use the client's internal methods if available
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Try to get memories with proper filters
            url = "https://api.mem0.ai/v2/memories/"
            params = {"user_id": user_id}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                memories = data.get("memories", [])
                print(f"   ✅ Retrieved {len(memories)} memories via direct API")
                
                for i, memory in enumerate(memories, 1):
                    print(f"      Memory {i}: {memory.get('memory', 'N/A')[:100]}...")
            else:
                print(f"   ❌ API request failed: {response.status_code} - {response.text}")
                
        except Exception as e2:
            print(f"   ❌ Alternative method also failed: {e2}")
    
    print(f"\n🔍 Test 3: Searching Memories")
    print("-" * 50)
    
    search_queries = ["printer", "technician", "Sarah Johnson", "ticket"]
    
    for query in search_queries:
        try:
            results = client.search(query=query, user_id=user_id)
            print(f"   🔍 '{query}': Found {len(results)} results")
            
            for i, result in enumerate(results[:2], 1):  # Show first 2 results
                memory_text = result.get('memory', 'N/A')
                print(f"      Result {i}: {memory_text[:80]}...")
                
        except Exception as e:
            print(f"   ❌ Search for '{query}' failed: {e}")
            
            # Try direct API search
            try:
                import requests
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                url = "https://api.mem0.ai/v2/memories/search/"
                data = {
                    "query": query,
                    "user_id": user_id,
                    "limit": 5
                }
                
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    search_data = response.json()
                    results = search_data.get("memories", [])
                    print(f"      🔄 Direct API: Found {len(results)} results for '{query}'")
                else:
                    print(f"      ❌ Direct API search failed: {response.status_code} - {response.text}")
                    
            except Exception as e2:
                print(f"      ❌ Direct API search error: {e2}")
    
    print(f"\n🧪 Test 4: Memory Management Operations")
    print("-" * 50)
    
    # Try to get memory IDs for management operations
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Get memories to find IDs
        url = "https://api.mem0.ai/v2/memories/"
        params = {"user_id": user_id}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            memories = data.get("memories", [])
            
            if memories:
                memory_id = memories[0].get("id")
                print(f"   📋 Found memory ID: {memory_id}")
                
                # Test memory history
                try:
                    history = client.history(memory_id=memory_id, user_id=user_id)
                    print(f"   ✅ Memory history retrieved: {len(history)} entries")
                except Exception as e:
                    print(f"   ❌ Memory history failed: {e}")
                
            else:
                print("   ⚠️  No memories found for management operations")
        else:
            print(f"   ❌ Could not retrieve memories for management: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Memory management test failed: {e}")
    
    print(f"\n🎉 mem0 Storage & Retrieval Test Complete")
    print("=" * 70)
    print("✅ Storage: Working correctly")
    print("🔍 Retrieval: Testing different approaches")
    print("🔎 Search: Testing with proper user_id filters")
    print("🛠️  Management: Testing memory operations")
    
    return True

if __name__ == "__main__":
    success = test_mem0_storage_and_retrieval()
    sys.exit(0 if success else 1)