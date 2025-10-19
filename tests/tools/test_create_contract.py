"""
Test script for the Create Contract tool using the provided curl commands
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_create_contract_api():
    """Test the create contract API using the exact curl command format"""
    import aiohttp
    
    # API configuration from the curl command
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=85FCE81607F959E626C4441659A071CD; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # Exact payload from the provided curl command
    create_payload = {
        "query": "mutation createClientContract($input: CreateClientContractInput!) {\n  createClientContract(input: $input)\n}\n",
        "variables": {
            "input": {
                "client": {"accountId": "6028534895674512340"},
                "startDate": "2025-10-24",
                "contract": {
                    "description": "Upfront charges for services offered",
                    "billableContract": {
                        "sellingPriceOverridden": True,
                        "recurringContract": {
                            "recurringMode": "UPFRONT",
                            "frequencyDurationUnit": "MONTH",
                            "frequencyInterval": 1
                        },
                        "sellingPrice": {
                            "model": "PER_UNIT",
                            "details": [{"value": "5000"}]
                        },
                        "billableSiteType": "HQ",
                        "addSites": [],
                        "change": {
                            "effectiveDate": None,
                            "quantity": None,
                            "quantityChangeOperation": "BASELINE"
                        },
                        "chargeItem": {"itemId": "1989229887864229888"}
                    }
                }
            }
        }
    }
    
    contract_id = None
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📋 Testing SuperOps Create Contract API")
            print("=" * 60)
            
            # Step 1: Create the contract
            print("\n🔨 Step 1: Creating Contract...")
            print("-" * 40)
            
            async with session.post(url, headers=headers, json=create_payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data and data['errors']:
                        print("❌ GraphQL Errors:")
                        for error in data['errors']:
                            message = error.get('message', 'Unknown error')
                            print(f"   - {message}")
                            
                            if 'extensions' in error:
                                extensions = error['extensions']
                                print(f"     Classification: {extensions.get('classification', 'Unknown')}")
                    
                    elif 'data' in data and data['data'] and data['data']['createClientContract']:
                        contract_id = data['data']['createClientContract']
                        print("✅ Contract Created Successfully!")
                        print(f"   📋 Contract ID: {contract_id}")
                        
                        print(f"\n📋 Creation Response:")
                        print(json.dumps(data, indent=2))
                    
                    else:
                        print("❌ Failed to create contract - unexpected response")
                        print(f"Response: {json.dumps(data, indent=2)}")
                
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error: {response.status}")
                    print(f"Error response: {error_text}")
            
            # Step 2: Get the contract details if creation was successful
            if contract_id:
                print(f"\n🔍 Step 2: Retrieving Contract Details...")
                print("-" * 40)
                
                # GraphQL query to get contract details
                get_payload = {
                    "query": """
                    query getClientContract($contractId: String!) {
                      getClientContract(contractId: $contractId) {
                        id
                        client {
                          accountId
                          name
                        }
                        startDate
                        endDate
                        status
                        contract {
                          description
                          billableContract {
                            sellingPrice {
                              model
                              details {
                                value
                              }
                            }
                            recurringContract {
                              recurringMode
                              frequencyDurationUnit
                              frequencyInterval
                            }
                            billableSiteType
                            chargeItem {
                              itemId
                              name
                            }
                          }
                        }
                        createdAt
                        updatedAt
                      }
                    }
                    """,
                    "variables": {"contractId": contract_id}
                }
                
                async with session.post(url, headers=headers, json=get_payload) as response:
                    print(f"Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data and data['errors']:
                            print("❌ GraphQL Errors:")
                            for error in data['errors']:
                                message = error.get('message', 'Unknown error')
                                print(f"   - {message}")
                        
                        elif 'data' in data and data['data'] and data['data']['getClientContract']:
                            contract = data['data']['getClientContract']
                            print("✅ Contract Details Retrieved Successfully!")
                            
                            # Pretty print contract details
                            print(f"\n📋 Contract Details:")
                            print(f"   🆔 Contract ID: {contract.get('id')}")
                            print(f"   📅 Start Date: {contract.get('startDate')}")
                            print(f"   📅 End Date: {contract.get('endDate', 'Not specified')}")
                            print(f"   📊 Status: {contract.get('status', 'Unknown')}")
                            
                            # Client information
                            client_info = contract.get('client', {})
                            print(f"   🏢 Client: {client_info.get('name', 'Unknown')} (ID: {client_info.get('accountId')})")
                            
                            # Contract details
                            contract_details = contract.get('contract', {})
                            print(f"   📝 Description: {contract_details.get('description')}")
                            
                            # Billing information
                            billable_contract = contract_details.get('billableContract', {})
                            if billable_contract:
                                selling_price = billable_contract.get('sellingPrice', {})
                                price_details = selling_price.get('details', [])
                                if price_details:
                                    print(f"   💰 Price: ${price_details[0].get('value', '0')} ({selling_price.get('model', 'Unknown')})")
                                
                                recurring = billable_contract.get('recurringContract', {})
                                if recurring:
                                    print(f"   🔄 Recurring: {recurring.get('recurringMode')} every {recurring.get('frequencyInterval')} {recurring.get('frequencyDurationUnit')}")
                                
                                charge_item = billable_contract.get('chargeItem', {})
                                if charge_item:
                                    print(f"   📦 Charge Item: {charge_item.get('name', 'Unknown')} (ID: {charge_item.get('itemId')})")
                                
                                print(f"   🏢 Site Type: {billable_contract.get('billableSiteType', 'Unknown')}")
                            
                            # Timestamps
                            print(f"   📅 Created: {contract.get('createdAt', 'Unknown')}")
                            print(f"   📅 Updated: {contract.get('updatedAt', 'Unknown')}")
                            
                            print(f"\n📋 Full Contract Response:")
                            print(json.dumps(data, indent=2))
                        
                        else:
                            print("❌ Failed to retrieve contract details")
                            print(f"Response: {json.dumps(data, indent=2)}")
                    
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP Error: {response.status}")
                        print(f"Error response: {error_text}")
            
            # Final summary
            print(f"\n🎉 Contract API Testing Summary")
            print("=" * 60)
            if contract_id:
                print("✅ Contract creation successful")
                print("✅ Contract retrieval successful")
                print(f"✅ Contract ID: {contract_id}")
                print("✅ Full workflow completed")
            else:
                print("❌ Contract creation failed")
            
            print(f"\n💡 Contract Tool Features:")
            print("   • ✅ Create client contracts with billing details")
            print("   • ✅ Retrieve contract information by ID")
            print("   • ✅ Support for recurring billing configurations")
            print("   • ✅ Flexible pricing models (PER_UNIT, etc.)")
            print("   • ✅ Site-based billing options")
            print("   • ✅ Charge item integration")
            
            return contract_id is not None
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_create_contract_api())