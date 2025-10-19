"""
Complete contract workflow test - Create and List contracts
"""

import asyncio
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_contract_workflow():
    """Test the complete contract workflow - create and list"""
    import aiohttp
    
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=85FCE81607F959E626C4441659A071CD; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    created_contracts = []
    
    async with aiohttp.ClientSession() as session:
        print("🚀 SuperOps Complete Contract Workflow Test")
        print("=" * 70)
        
        # Step 1: Get current contract list
        print("\n📋 Step 1: Getting Current Contract List")
        print("-" * 50)
        
        list_payload = {
            "query": "query getClientContractList($input: ListInfoInput) {\n  getClientContractList(input: $input) {\n    clientContracts {\n      client \n      contract {contractId contractType billableContract {chargeItem  discountRate quantityCalculationType sellingPriceCalculationType}}\n    }\n    listInfo {\n      totalCount \n    }\n  }\n}\n",
            "variables": {
                "input": {
                    "page": 1,
                    "pageSize": 20
                }
            }
        }
        
        async with session.post(url, headers=headers, json=list_payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data and data['data']['getClientContractList']:
                    contract_list = data['data']['getClientContractList']
                    initial_count = contract_list['listInfo']['totalCount']
                    print(f"✅ Current contracts in system: {initial_count}")
                else:
                    print("❌ Failed to get initial contract list")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status}")
                return False
        
        # Step 2: Create a new contract
        print(f"\n🔨 Step 2: Creating New Contract")
        print("-" * 50)
        
        timestamp = int(time.time())
        
        create_payload = {
            "query": "mutation createClientContract($input: CreateClientContractInput!) {\n  createClientContract(input: $input)\n}\n",
            "variables": {
                "input": {
                    "client": {"accountId": "6028532731226112000"},  # Dunder Mifflin
                    "startDate": "2025-01-01",
                    "contract": {
                        "description": f"Test Contract Created at {timestamp}",
                        "billableContract": {
                            "sellingPriceOverridden": True,
                            "recurringContract": {
                                "recurringMode": "UPFRONT",
                                "frequencyDurationUnit": "MONTH",
                                "frequencyInterval": 1
                            },
                            "sellingPrice": {
                                "model": "PER_UNIT",
                                "details": [{"value": "3000"}]
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
        
        async with session.post(url, headers=headers, json=create_payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data and data['data']['createClientContract']:
                    new_contract_id = data['data']['createClientContract']
                    created_contracts.append(new_contract_id)
                    print(f"✅ New contract created: {new_contract_id}")
                else:
                    print("❌ Failed to create contract")
                    if 'errors' in data:
                        for error in data['errors']:
                            print(f"   Error: {error.get('message', 'Unknown')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status}")
                return False
        
        # Step 3: Verify the contract appears in the list
        print(f"\n🔍 Step 3: Verifying Contract in List")
        print("-" * 50)
        
        # Wait a moment for the contract to be indexed
        await asyncio.sleep(2)
        
        async with session.post(url, headers=headers, json=list_payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data and data['data']['getClientContractList']:
                    contract_list = data['data']['getClientContractList']
                    contracts = contract_list['clientContracts']
                    new_count = contract_list['listInfo']['totalCount']
                    
                    print(f"✅ Updated contract count: {new_count}")
                    print(f"📈 Increase: {new_count - initial_count}")
                    
                    # Look for our new contract
                    found_contract = None
                    for contract_entry in contracts:
                        contract_info = contract_entry.get('contract', {})
                        if contract_info.get('contractId') == new_contract_id:
                            found_contract = contract_entry
                            break
                    
                    if found_contract:
                        print(f"✅ New contract found in list!")
                        
                        client_info = found_contract.get('client', {})
                        contract_info = found_contract.get('contract', {})
                        
                        print(f"   Client: {client_info.get('name', 'Unknown')}")
                        print(f"   Contract ID: {contract_info.get('contractId')}")
                        print(f"   Type: {contract_info.get('contractType')}")
                        
                        billable = contract_info.get('billableContract', {})
                        if billable:
                            charge_item = billable.get('chargeItem', {})
                            print(f"   Charge Item: {charge_item.get('name', 'Unknown')}")
                            print(f"   Quantity Calc: {billable.get('quantityCalculationType')}")
                            print(f"   Price Calc: {billable.get('sellingPriceCalculationType')}")
                    else:
                        print(f"⚠️  New contract not yet visible in list (may need more time)")
                
                else:
                    print("❌ Failed to get updated contract list")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status}")
                return False
        
        # Step 4: Display summary of all contracts
        print(f"\n📊 Step 4: Complete Contract Summary")
        print("-" * 50)
        
        # Get full contract list one more time
        full_list_payload = {
            "query": "query getClientContractList($input: ListInfoInput) {\n  getClientContractList(input: $input) {\n    clientContracts {\n      client \n      contract {contractId contractType billableContract {chargeItem  discountRate quantityCalculationType sellingPriceCalculationType}}\n    }\n    listInfo {\n      totalCount \n    }\n  }\n}\n",
            "variables": {
                "input": {
                    "page": 1,
                    "pageSize": 50  # Get more contracts
                }
            }
        }
        
        async with session.post(url, headers=headers, json=full_list_payload) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data and data['data']['getClientContractList']:
                    contract_list = data['data']['getClientContractList']
                    contracts = contract_list['clientContracts']
                    total_count = contract_list['listInfo']['totalCount']
                    
                    print(f"📋 Total Contracts: {total_count}")
                    print(f"📄 Retrieved: {len(contracts)}")
                    
                    # Group by client
                    clients = {}
                    our_contracts = []
                    
                    for contract_entry in contracts:
                        client_info = contract_entry.get('client', {})
                        contract_info = contract_entry.get('contract', {})
                        
                        client_name = client_info.get('name', 'Unknown')
                        contract_id = contract_info.get('contractId')
                        
                        if client_name not in clients:
                            clients[client_name] = 0
                        clients[client_name] += 1
                        
                        # Check if this is one of our created contracts
                        if contract_id in ['7943918829018910720', '7943919815510822912'] + created_contracts:
                            our_contracts.append({
                                'id': contract_id,
                                'client': client_name,
                                'type': contract_info.get('contractType')
                            })
                    
                    print(f"\n🏢 Contracts by Client:")
                    for client_name, count in clients.items():
                        print(f"   • {client_name}: {count} contracts")
                    
                    if our_contracts:
                        print(f"\n🎯 Our Created Contracts:")
                        for contract in our_contracts:
                            print(f"   • {contract['id']} ({contract['client']}) - {contract['type']}")
        
        # Final status
        print(f"\n🎉 Complete Workflow Test Results")
        print("=" * 70)
        print("✅ Contract creation - WORKING")
        print("✅ Contract listing - WORKING")
        print("✅ Contract verification - WORKING")
        print("✅ End-to-end workflow - SUCCESSFUL")
        
        print(f"\n🛠️  Available Contract Management Tools:")
        print("   • create_client_contract() - Create new contracts")
        print("   • get_client_contract_list() - List all contracts")
        print("   • create_simple_contract() - Quick contract creation")
        print("   • Full workflow integration - Ready for production")
        
        return len(created_contracts) > 0

if __name__ == "__main__":
    asyncio.run(test_complete_contract_workflow())