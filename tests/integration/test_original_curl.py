"""
Test the original curl command exactly as provided
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_original_curl():
    """Test the original curl command exactly"""
    import aiohttp
    
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=F19C4F40B60514A49265C330A7CFDE7D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Exact payload from the original curl command
    payload = {
        "query": "mutation createClientUser($input: CreateClientUserInput!) {\n  createClientUser(input: $input) {\n    userId\n    firstName\n    lastName\n    name\n    email\n    contactNumber\n    reportingManager\n    site\n    role\n    client\n    customFields\n  }\n}\n",
        "variables": {
            "input": {
                "firstName": "Ryan",
                "email": "ryan15.21howard@dundermifflin.com",
                "role": {"roleId": "5"},
                "client": {"accountId": "6028532731226112000"}
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🔄 Testing Original Curl Command")
            print("=" * 50)
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print("-" * 50)
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data and data['errors']:
                        print("❌ GraphQL Errors:")
                        for i, error in enumerate(data['errors']):
                            print(f"Error {i+1}:")
                            print(f"  Message: {error.get('message', 'None')}")
                            
                            if 'extensions' in error:
                                extensions = error['extensions']
                                print(f"  Classification: {extensions.get('classification', 'Unknown')}")
                                
                                if 'clientError' in extensions:
                                    client_errors = extensions['clientError']
                                    for j, client_error in enumerate(client_errors):
                                        print(f"  Client Error {j+1}:")
                                        print(f"    Code: '{client_error.get('code', 'empty')}'")
                                        print(f"    Param: {client_error.get('param', 'null')}")
                    
                    elif 'data' in data and data['data'] and data['data']['createClientUser']:
                        print("✅ Success!")
                        client_user = data['data']['createClientUser']
                        
                        print(f"Created Client User:")
                        for key, value in client_user.items():
                            print(f"  {key}: {value}")
                    
                    else:
                        print("❌ No valid data returned")
                    
                    print(f"\nFull Response:")
                    print(json.dumps(data, indent=2))
                
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error: {response.status}")
                    print(f"Response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_original_curl())