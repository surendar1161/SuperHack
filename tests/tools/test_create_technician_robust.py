"""
Robust test script for the Create Technician tool with unique emails
"""

import asyncio
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_technician_robust():
    """Test the create technician API with unique emails and better error handling"""
    import aiohttp
    
    # API configuration
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=5917F30300327B707B9C60EDC399DC6D; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Generate unique timestamp for emails
    timestamp = int(time.time())
    
    # Test cases with unique emails
    test_cases = [
        {
            "name": "Create basic technician with unique email",
            "input": {
                "firstName": "Alice",
                "lastName": "Johnson",
                "email": f"alice.johnson.{timestamp}@testdomain.com",
                "contactNumber": "555-111-2222",
                "emailSignature": "Best regards,\nAlice Johnson",
                "role": {"roleId": 3}
            }
        },
        {
            "name": "Create technician with minimal fields",
            "input": {
                "firstName": "Bob",
                "lastName": "Smith",
                "email": f"bob.smith.{timestamp}@testdomain.com",
                "contactNumber": "555-333-4444",
                "role": {"roleId": 3}
            }
        },
        {
            "name": "Create technician with designation",
            "input": {
                "firstName": "Carol",
                "lastName": "Davis",
                "email": f"carol.davis.{timestamp}@testdomain.com",
                "contactNumber": "555-555-6666",
                "designation": "Senior IT Technician",
                "emailSignature": "Carol Davis\nSenior IT Technician\nIT Support Team",
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
    
    created_technicians = []
    
    async with aiohttp.ClientSession() as session:
        print("🔧 Testing SuperOps Create Technician API (Robust)")
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
                        
                        if 'errors' in data and data['errors']:
                            print("❌ GraphQL Errors:")
                            for error in data['errors']:
                                message = error.get('message', 'Unknown error')
                                print(f"   - {message}")
                                
                                # Handle specific error types
                                if 'extensions' in error:
                                    extensions = error['extensions']
                                    classification = extensions.get('classification', 'Unknown')
                                    print(f"     Classification: {classification}")
                                    
                                    if 'clientError' in extensions:
                                        client_errors = extensions['clientError']
                                        for client_error in client_errors:
                                            code = client_error.get('code', 'unknown')
                                            if code == 'unique_validation_failed':
                                                attributes = client_error.get('param', {}).get('attributes', [])
                                                print(f"     Unique validation failed for: {', '.join(attributes)}")
                        
                        # Check if technician was created successfully
                        if 'data' in data and data['data'] and data['data']['createTechnician']:
                            print("✅ Success!")
                            technician = data['data']['createTechnician']
                            created_technicians.append(technician)
                            
                            print(f"   👤 Created Technician:")
                            print(f"     User ID: {technician.get('userId')}")
                            print(f"     Name: {technician.get('name')}")
                            print(f"     Email: {technician.get('email')}")
                            print(f"     Contact: {technician.get('contactNumber')}")
                            print(f"     Designation: {technician.get('designation', 'Not specified')}")
                            
                            role_info = technician.get('role', {})
                            if isinstance(role_info, dict):
                                print(f"     Role: {role_info.get('name', 'Unknown')} (ID: {role_info.get('roleId', 'Unknown')})")
                            else:
                                print(f"     Role: {role_info}")
                        else:
                            print("❌ Failed to create technician")
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP Error: {response.status}")
                        print(f"Error response: {error_text}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        print(f"\n🎉 Testing completed!")
        print(f"\n📊 Results Summary:")
        print(f"   Total tests: {len(test_cases)}")
        print(f"   Successful creations: {len(created_technicians)}")
        
        if created_technicians:
            print(f"\n👥 Successfully Created Technicians:")
            for tech in created_technicians:
                print(f"   - {tech['name']} (ID: {tech['userId']}, Email: {tech['email']})")
        
        print(f"\n💡 Key Findings:")
        print(f"   - Email addresses must be unique across the system")
        print(f"   - Minimal required fields: firstName, lastName, email, contactNumber, role")
        print(f"   - Role ID 3 corresponds to 'Technician' role")
        print(f"   - Optional fields: designation, emailSignature, businessFunction, team")
        print(f"   - API returns complete technician profile including generated user ID")

if __name__ == "__main__":
    asyncio.run(test_create_technician_robust())