"""Create contract tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("create_contract")


@tool
async def create_client_contract(
    client_account_id: str,
    start_date: str,
    description: str,
    selling_price: str,
    charge_item_id: str,
    recurring_mode: str = "UPFRONT",
    frequency_duration_unit: str = "MONTH",
    frequency_interval: int = 1,
    billable_site_type: str = "HQ",
    selling_price_model: str = "PER_UNIT"
) -> Dict[str, Any]:
    """
    Create a new client contract in SuperOps
    
    Args:
        client_account_id: Account ID of the client organization
        start_date: Contract start date (YYYY-MM-DD format)
        description: Contract description
        selling_price: Price value as string
        charge_item_id: ID of the charge item
        recurring_mode: Recurring mode (default: "UPFRONT")
        frequency_duration_unit: Duration unit (default: "MONTH")
        frequency_interval: Frequency interval (default: 1)
        billable_site_type: Site type (default: "HQ")
        selling_price_model: Price model (default: "PER_UNIT")
        
    Returns:
        Dictionary containing created contract ID or error information
    """
    try:
        logger.info(f"Creating client contract for client {client_account_id}")
        
        # Initialize SuperOps client
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # GraphQL mutation for creating client contract
        mutation = """
        mutation createClientContract($input: CreateClientContractInput!) {
          createClientContract(input: $input)
        }
        """
        
        # Build input variables
        input_data = {
            "client": {
                "accountId": client_account_id
            },
            "startDate": start_date,
            "contract": {
                "description": description,
                "billableContract": {
                    "sellingPriceOverridden": True,
                    "recurringContract": {
                        "recurringMode": recurring_mode,
                        "frequencyDurationUnit": frequency_duration_unit,
                        "frequencyInterval": frequency_interval
                    },
                    "sellingPrice": {
                        "model": selling_price_model,
                        "details": [{"value": selling_price}]
                    },
                    "billableSiteType": billable_site_type,
                    "addSites": [],
                    "change": {
                        "effectiveDate": None,
                        "quantity": None,
                        "quantityChangeOperation": "BASELINE"
                    },
                    "chargeItem": {
                        "itemId": charge_item_id
                    }
                }
            }
        }
        
        variables = {"input": input_data}
        
        # Execute the GraphQL mutation
        response = await client.execute_graphql_query(
            query=mutation,
            variables=variables
        )
        
        if not response or 'data' not in response:
            logger.error("No data received from SuperOps API")
            return {
                "success": False,
                "error": "No data received from SuperOps API",
                "contract_id": None
            }
        
        # Check for GraphQL errors
        if 'errors' in response:
            error_messages = [error.get('message', 'Unknown error') for error in response['errors']]
            logger.error(f"GraphQL errors: {error_messages}")
            return {
                "success": False,
                "error": f"GraphQL errors: {', '.join(error_messages)}",
                "contract_id": None
            }
        
        contract_id = response['data'].get('createClientContract')
        
        if not contract_id:
            logger.error("No contract ID returned from mutation")
            return {
                "success": False,
                "error": "No contract ID returned from mutation",
                "contract_id": None
            }
        
        logger.info(f"Successfully created contract with ID: {contract_id}")
        
        return {
            "success": True,
            "contract_id": contract_id,
            "message": f"Successfully created contract: {contract_id}"
        }
        
    except Exception as e:
        logger.error(f"Error creating contract: {e}")
        return {
            "success": False,
            "error": str(e),
            "contract_id": None
        }


@tool
async def get_client_contract_list(
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get list of client contracts from SuperOps
    
    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of contracts per page (default: 10)
        
    Returns:
        Dictionary containing contracts list and pagination info
    """
    try:
        logger.info(f"Retrieving client contracts list (page {page}, size {page_size})")
        
        # Initialize SuperOps client
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # GraphQL query for getting client contracts list (working version)
        query = """
        query getClientContractList($input: ListInfoInput) {
          getClientContractList(input: $input) {
            clientContracts {
              client 
              contract {
                contractId 
                contractType 
                billableContract {
                  chargeItem  
                  discountRate 
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
                "page": page,
                "pageSize": page_size
            }
        }
        
        response = await client.execute_graphql_query(
            query=query,
            variables=variables
        )
        
        if not response or 'data' not in response:
            return {
                "success": False,
                "error": "No data received from SuperOps API",
                "contracts": [],
                "pagination": None
            }
        
        # Check for GraphQL errors
        if 'errors' in response:
            error_messages = [error.get('message', 'Unknown error') for error in response['errors']]
            return {
                "success": False,
                "error": f"GraphQL errors: {', '.join(error_messages)}",
                "contracts": [],
                "pagination": None
            }
        
        contract_data = response['data'].get('getClientContractList', {})
        contracts = contract_data.get('clientContracts', [])
        list_info = contract_data.get('listInfo', {})
        
        logger.info(f"Successfully retrieved {len(contracts)} contracts")
        
        return {
            "success": True,
            "contracts": contracts,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": list_info.get('totalCount', 0)
            },
            "total_contracts": len(contracts)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contracts list: {e}")
        return {
            "success": False,
            "error": str(e),
            "contracts": [],
            "pagination": None
        }


@tool
async def get_client_contract(contract_id: str) -> Dict[str, Any]:
    """
    Get client contract details by ID
    
    Args:
        contract_id: The ID of the contract to retrieve
        
    Returns:
        Dictionary containing contract details or error information
    """
    try:
        logger.info(f"Retrieving contract details for ID: {contract_id}")
        
        # Initialize SuperOps client
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # GraphQL query for getting contract details
        query = """
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
        """
        
        variables = {"contractId": contract_id}
        
        response = await client.execute_graphql_query(
            query=query,
            variables=variables
        )
        
        if not response or 'data' not in response:
            return {
                "success": False,
                "error": "No data received from SuperOps API",
                "contract": None
            }
        
        # Check for GraphQL errors
        if 'errors' in response:
            error_messages = [error.get('message', 'Unknown error') for error in response['errors']]
            return {
                "success": False,
                "error": f"GraphQL errors: {', '.join(error_messages)}",
                "contract": None
            }
        
        contract = response['data'].get('getClientContract')
        
        if not contract:
            return {
                "success": False,
                "error": f"Contract with ID {contract_id} not found",
                "contract": None
            }
        
        logger.info(f"Successfully retrieved contract {contract_id}")
        
        return {
            "success": True,
            "contract": contract
        }
        
    except Exception as e:
        logger.error(f"Error retrieving contract {contract_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "contract": None
        }


@tool
async def create_simple_contract(
    client_account_id: str,
    description: str,
    selling_price: str,
    charge_item_id: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a simple client contract with minimal required information
    
    Args:
        client_account_id: Account ID of the client organization
        description: Contract description
        selling_price: Price value as string
        charge_item_id: ID of the charge item
        start_date: Contract start date (defaults to today if not provided)
        
    Returns:
        Dictionary containing created contract ID or error information
    """
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    return await create_client_contract(
        client_account_id=client_account_id,
        start_date=start_date,
        description=description,
        selling_price=selling_price,
        charge_item_id=charge_item_id
    )


@tool
async def create_and_retrieve_contract(
    client_account_id: str,
    start_date: str,
    description: str,
    selling_price: str,
    charge_item_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a contract and immediately retrieve its details
    
    Args:
        client_account_id: Account ID of the client organization
        start_date: Contract start date (YYYY-MM-DD format)
        description: Contract description
        selling_price: Price value as string
        charge_item_id: ID of the charge item
        **kwargs: Additional contract parameters
        
    Returns:
        Dictionary containing both creation result and contract details
    """
    try:
        # Create the contract
        create_result = await create_client_contract(
            client_account_id=client_account_id,
            start_date=start_date,
            description=description,
            selling_price=selling_price,
            charge_item_id=charge_item_id,
            **kwargs
        )
        
        if not create_result.get('success'):
            return {
                "success": False,
                "error": create_result.get('error'),
                "creation_result": create_result,
                "contract_details": None
            }
        
        contract_id = create_result.get('contract_id')
        
        # Retrieve the contract details
        details_result = await get_client_contract(contract_id)
        
        return {
            "success": True,
            "contract_id": contract_id,
            "creation_result": create_result,
            "contract_details": details_result.get('contract') if details_result.get('success') else None,
            "message": f"Successfully created and retrieved contract: {contract_id}"
        }
        
    except Exception as e:
        logger.error(f"Error in create_and_retrieve_contract: {e}")
        return {
            "success": False,
            "error": str(e),
            "creation_result": None,
            "contract_details": None
        }