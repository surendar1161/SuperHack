"""
Test script using the exact curl command format
"""

import asyncio
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_exact_curl_format():
    """Test using the exact format from the provided curl command"""
    import aiohttp
    
    # API configuration - exact from curl
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=F19C4F40B60514A49265C330A7CFDE7D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Generate unique timestamp for email
    timestamp = int(time.time())
    
    # Exact payload from curl command with unique email
    payload = {
        "query": "mutation createClientUser($input: CreateClientUserInput!) {\n  createClientUser(input: $input) {\n    userId\n    firstName\n    lastName\n    name\n    email\n    contactNumber\n    reportingManager\n    site\n    role\n    client\n    customFields\n  }\n}",
        "variables": {
            "input": {
                "firstName": "Ryan",
                "email": f"ryan{timestamp}.howard@dundermifflin.com",
                "role": {"roleId": "5"},
                "client": {"accountId": "6028532731226112000"}
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🧪 Testing Exact Curl Format")
            print("=" * 50)
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("Response received!")
                    
                    if 'errors' in data and data['errors']:
                        print("❌ GraphQL Errors:")
                        for error in data['errors']:
                            message = error.get('message', 'No message')
                            print(f"   - {message}")
                            
                            if 'extensions' in error:
                                extensions = error['extensions']
                                print(f"   Extensions: {json.dumps(extensions, indent=4)}")
                    
                    elif 'data' in data and data['data'] and data['data']['createClientUser']:
                        print("✅ Success!")
                        client_user = data['data']['createClientUser']
                        
                        print(f"Created Client User:")
                        print(f"  User ID: {client_user.get('userId')}")
                        print(f"  Name: {client_user.get('name')}")
                        print(f"  Email: {client_user.get('email')}")
                        print(f"  Role: {client_user.get('role')}")
                        print(f"  Client: {client_user.get('client')}")
                    
                    else:
                        print("❌ No data returned")
                    
                    print(f"\nFull Response:")
                    print(json.dumps(data, indent=2))
                
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error: {response.status}")
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_with_lastname():
    """Test with lastName added"""
    import aiohttp
    
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=F19C4F40B60514A49265C330A7CFDE7D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    timestamp = int(time.time())
    
    payload = {
        "query": "mutation createClientUser($input: CreateClientUserInput!) {\n  createClientUser(input: $input) {\n    userId\n    firstName\n    lastName\n    name\n    email\n    contactNumber\n    reportingManager\n    site\n    role\n    client\n    customFields\n  }\n}",
        "variables": {
            "input": {
                "firstName": "Ryan",
                "lastName": "Howard",
                "email": f"ryan{timestamp}.howard@dundermifflin.com",
                "role": {"roleId": "5"},
                "client": {"accountId": "6028532731226112000"}
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("\n🧪 Testing With Last Name")
            print("=" * 50)
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data and data['errors']:
                        print("❌ GraphQL Errors:")
                        for error in data['errors']:
                            message = error.get('message', 'No message')
                            print(f"   - {message}")
                    
                    elif 'data' in data and data['data'] and data['data']['createClientUser']:
                        print("✅ Success!")
                        client_user = data['data']['createClientUser']
                        print(f"Created: {client_user.get('name')} (ID: {client_user.get('userId')})")
                    
                    else:
                        print("❌ No data returned")
                    
                    print(f"\nResponse: {json.dumps(data, indent=2)}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_exact_curl_format())
    asyncio.run(test_with_lastname())