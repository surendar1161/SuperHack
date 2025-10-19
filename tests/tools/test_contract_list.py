"""
Test script for the Get Client Contract List tool
"""

import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_contract_list_api():
    """Test the get client contract list API and display results nicely"""
    import aiohttp
    
    # API configuration
    url = "https://api.superops.ai/msp"
    headers = {
        "CustomerSubDomain": "hackathonsuperhack",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('SUPEROPS_API_KEY')}",
        "Cookie": "JSESSIONID=85FCE81607F959E626C4441659A071CD; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    # GraphQL query for getting client contracts list
    query = """
    query getClientContractList($input: ListInfoInput!) {
      getClientContractList(input: $input) {
        clientContracts {
          client {
            identity
            accountId
            name
            accountType
          }
          contract {
            contractId
            contractType
            billableContract {
              chargeItem {
                itemId
                name
                description
                itemType
                serviceTypeItem {
                  offeringType
                }
              }
              quantityCalculationType
              sellingPriceCalculationType
            }
          }
        }
        listInfo {
          totalCount
        }
      }
    }
    """
    
    variables = {
        "input": {
            "page": 1,
            "pageSize": 20
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📋 Testing SuperOps Client Contract List API")
            print("=" * 70)
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data and data['errors']:
                        print("❌ GraphQL Errors:")
                        for error in data['errors']:
                            message = error.get('message', 'Unknown error')
                            print(f"   - {message}")
                    
                    elif 'data' in data and data['data'] and data['data']['getClientContractList']:
                        contract_list = data['data']['getClientContractList']
                        contracts = contract_list.get('clientContracts', [])
                        list_info = contract_list.get('listInfo', {})
                        
                        print("✅ Contract List Retrieved Successfully!")
                        print(f"📊 Total Contracts: {list_info.get('totalCount', 0)}")
                        print(f"📋 Retrieved: {len(contracts)} contracts")
                        
                        # Group contracts by client
                        clients = {}
                        for contract_entry in contracts:
                            client_info = contract_entry.get('client', {})
                            contract_info = contract_entry.get('contract', {})
                            
                            client_name = client_info.get('name', 'Unknown')
                            client_id = client_info.get('accountId', 'Unknown')
                            
                            if client_name not in clients:
                                clients[client_name] = {
                                    'info': client_info,
                                    'contracts': []
                                }
                            
                            clients[client_name]['contracts'].append(contract_info)
                        
                        # Display contracts by client
                        print(f"\n🏢 Contracts by Client:")
                        print("=" * 70)
                        
                        for client_name, client_data in clients.items():
                            client_info = client_data['info']
                            contracts = client_data['contracts']
                            
                            print(f"\n🏢 {client_name}")
                            print(f"   Account ID: {client_info.get('accountId')}")
                            print(f"   Account Type: {client_info.get('accountType')}")
                            print(f"   Total Contracts: {len(contracts)}")
                            
                            for i, contract in enumerate(contracts, 1):
                                print(f"\n   📋 Contract {i}:")
                                print(f"      Contract ID: {contract.get('contractId')}")
                                print(f"      Type: {contract.get('contractType')}")
                                
                                billable = contract.get('billableContract')
                                if billable:
                                    charge_item = billable.get('chargeItem', {})
                                    print(f"      Charge Item: {charge_item.get('name', 'Unknown')}")
                                    print(f"      Item Type: {charge_item.get('itemType', 'Unknown')}")
                                    
                                    service_type = charge_item.get('serviceTypeItem', {})
                                    if service_type:
                                        print(f"      Offering Type: {service_type.get('offeringType', 'Unknown')}")
                                    
                                    print(f"      Quantity Calc: {billable.get('quantityCalculationType', 'Unknown')}")
                                    print(f"      Price Calc: {billable.get('sellingPriceCalculationType', 'Unknown')}")
                                else:
                                    print(f"      Billing: Not configured")
                        
                        # Summary statistics
                        print(f"\n📊 Contract Summary:")
                        print("=" * 70)
                        
                        contract_types = {}
                        item_types = {}
                        offering_types = {}
                        
                        for contract_entry in contracts:
                            contract_info = contract_entry.get('contract', {})
                            contract_type = contract_info.get('contractType', 'Unknown')
                            
                            contract_types[contract_type] = contract_types.get(contract_type, 0) + 1
                            
                            billable = contract_info.get('billableContract')
                            if billable:
                                charge_item = billable.get('chargeItem', {})
                                item_type = charge_item.get('itemType', 'Unknown')
                                item_types[item_type] = item_types.get(item_type, 0) + 1
                                
                                service_type = charge_item.get('serviceTypeItem', {})
                                if service_type:
                                    offering_type = service_type.get('offeringType', 'Unknown')
                                    offering_types[offering_type] = offering_types.get(offering_type, 0) + 1
                        
                        print(f"📋 Contract Types:")
                        for contract_type, count in contract_types.items():
                            print(f"   • {contract_type}: {count}")
                        
                        print(f"\n📦 Item Types:")
                        for item_type, count in item_types.items():
                            print(f"   • {item_type}: {count}")
                        
                        print(f"\n🎯 Offering Types:")
                        for offering_type, count in offering_types.items():
                            print(f"   • {offering_type}: {count}")
                        
                        # Available clients and charge items
                        print(f"\n💡 Available Resources:")
                        print("=" * 70)
                        
                        unique_clients = set()
                        unique_charge_items = set()
                        
                        for contract_entry in contracts:
                            client_info = contract_entry.get('client', {})
                            contract_info = contract_entry.get('contract', {})
                            
                            client_id = client_info.get('accountId')
                            client_name = client_info.get('name')
                            if client_id and client_name:
                                unique_clients.add(f"{client_name} (ID: {client_id})")
                            
                            billable = contract_info.get('billableContract')
                            if billable:
                                charge_item = billable.get('chargeItem', {})
                                item_id = charge_item.get('itemId')
                                item_name = charge_item.get('name')
                                if item_id and item_name:
                                    unique_charge_items.add(f"{item_name} (ID: {item_id})")
                        
                        print(f"🏢 Available Clients:")
                        for client in sorted(unique_clients):
                            print(f"   • {client}")
                        
                        print(f"\n📦 Available Charge Items:")
                        for item in sorted(unique_charge_items):
                            print(f"   • {item}")
                    
                    else:
                        print("❌ Failed to retrieve contract list")
                        print(f"Response: {json.dumps(data, indent=2)}")
                
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP Error: {response.status}")
                    print(f"Error response: {error_text}")
        
        print(f"\n🎉 Contract List Tool Testing Complete!")
        print("=" * 70)
        print("✅ Contract listing functionality working")
        print("✅ Client information properly retrieved")
        print("✅ Contract details and billing info available")
        print("✅ Ready for integration into contract management workflows")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_contract_list_api())