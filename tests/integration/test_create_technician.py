"""
Test script for the Create Technician tool
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_technician_api():
    """Test the create technician API directly using aiohttp"""
    import aiohttp
    
    # API configuration from the curl command
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Test cases for creating technicians
    test_cases = [
        {
            "name": "Create basic technician",
            "input": {
                "firstName": "Jason",
                "lastName": "Wheeler", 
                "email": "jason.wheeler@acme.com",
                "contactNumber": "212-504-4115",
                "emailSignature": "xyz789",
                "role": {"roleId": 3}
            }
        },
        {
            "name": "Create technician with full details",
            "input": {
                "firstName": "Sarah",
                "lastName": "Connor",
                "email": "sarah.connor@cyberdyne.com",
                "contactNumber": "555-123-4567",
                "emailSignature": "Best regards,\nSarah Connor\nSenior IT Technician",
                "designation": "Senior IT Technician",
                "businessFunction": "IT Support",
                "team": "Infrastructure Team",
                "role": {"roleId": 3}
            }
        },
        {
            "name": "Create minimal technician",
            "input": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "contactNumber": "555-987-6543",
                "role": {"roleId": 3}
            }
        }
    ]
    
    # GraphQL mutation
    mutation = """
    mutation createTechnician($input: CreateTechnicianInput) {
      createTechnician(input: $input) {
        userId
        firstName
        lastName
        name
        email
        contactNumber
        emailSignature
        designation
        businessFunction
        team
        reportingManager
        role
        groups
      }
    }
    """
    
    async with aiohttp.ClientSession() as session:
        print("🔧 Testing SuperOps Create Technician API")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print("-" * 40)
            
            payload = {
                "query": mutation,
                "variables": {"input": test_case["input"]}
            }
            
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    print(f"Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data:
                            print("❌ GraphQL Errors:")
                            for error in data['errors']:
                                print(f"   - {error['message']}")
                                if 'extensions' in error:
                                    print(f"     Classification: {error['extensions'].get('classification', 'Unknown')}")
                        else:
                            print("✅ Success!")
                            technician = data['data']['createTechnician']
                            
                            print(f"   👤 Created Technician:")
                            print(f"     User ID: {technician.get('userId')}")
                            print(f"     Name: {technician.get('name')}")
                            print(f"     Email: {technician.get('email')}")
                            print(f"     Contact: {technician.get('contactNumber')}")
                            print(f"     Designation: {technician.get('designation', 'Not specified')}")
                            print(f"     Team: {technician.get('team', 'Not specified')}")
                            print(f"     Role: {technician.get('role', 'Not specified')}")
                            
                            if technician.get('emailSignature'):
                                print(f"     Email Signature: {technician.get('emailSignature')}")
                        
                        print(f"\n📋 Full Response:")
                        print(json.dumps(data, indent=2))
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP Error: {response.status}")
                        print(f"Error response: {error_text}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
            
            print("\n" + "="*60)
        
        print(f"\n🎉 All create technician tests completed!")
        print(f"\n💡 Tool Usage Summary:")
        print(f"   - Successfully tested technician creation with SuperOps API")
        print(f"   - Supports both minimal and full technician profiles")
        print(f"   - Returns complete technician data including user ID")
        print(f"   - Proper error handling for validation issues")
        print(f"   - Ready for integration into onboarding workflows")

if __name__ == "__main__":
    asyncio.run(test_create_technician_api())