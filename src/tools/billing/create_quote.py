"""Create quote tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date
from strands import tool

from ...utils.logger import get_logger

logger = get_logger("create_quote")


@tool
async def create_quote(
    client_id: str,
    description: str,
    amount: float,
    client_account_id: str = None,
    site_id: str = "7206852887969157120",
    service_item_id: str = "4478245546991632384",  # Default service item
    quote_date: str = None,
    expiry_date: str = None,
    title: str = None,
    status: str = "DRAFT"
) -> Dict[str, Any]:
    """
    Create a new quote in SuperOps billing system
    
    Args:
        client_id: The account ID of the client to quote (backward compatibility)
        description: Description of the quote
        amount: Total amount for the quote
        client_account_id: The account ID of the client to quote
        site_id: The site ID where services will be provided
        service_item_id: ID of the service item to quote
        quote_date: Quote date in YYYY-MM-DD format (default: today)
        expiry_date: Quote expiry date in YYYY-MM-DD format (default: 30 days from today)
        title: Quote title/subject (default: auto-generated)
        status: Quote status - DRAFT, SENT, ACCEPTED, etc. (default: "DRAFT")
        
    Returns:
        Dictionary containing quote creation results with success status, quote ID, and details
    """
    try:
        # Handle backward compatibility
        if client_id and not client_account_id:
            client_account_id = client_id
        
        logger.info(f"Creating quote for client {client_account_id}")
        
        # Set defaults
        if not quote_date:
            quote_date = date.today().strftime("%Y-%m-%d")
        
        if not expiry_date:
            from datetime import timedelta
            quote_dt = datetime.strptime(quote_date, "%Y-%m-%d").date()
            expiry_dt = quote_dt + timedelta(days=30)
            expiry_date = expiry_dt.strftime("%Y-%m-%d")
        
        if not title:
            title = f"Service Quote - {description}"
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # GraphQL mutation matching the working curl format
            mutation = """
            mutation createQuote($createQuote: CreateQuoteInput!) {
              createQuote(input: $createQuote) {
                quoteId
                displayId
                items {serviceItem quantity}
                title
                client
              }
            }
            """
            
            # Variables matching the working curl format
            variables = {
                "createQuote": {
                    "client": {
                        "accountId": client_account_id
                    },
                    "description": description,
                    "site": {
                        "id": site_id
                    },
                    "addItems": [
                        {
                            "serviceItem": {
                                "itemId": service_item_id
                            },
                            "quantity": 1,
                            "unitPrice": amount
                        }
                    ],
                    "statusEnum": status.upper(),
                    "quoteDate": quote_date,
                    "expiryDate": expiry_date,
                    "title": title
                }
            }
            
            # Execute the GraphQL mutation
            result = await client.execute_graphql_query(mutation, variables)
            
            if result and "data" in result and result["data"]["createQuote"]:
                quote_data = result["data"]["createQuote"]
                quote_id = quote_data.get("quoteId")
                display_id = quote_data.get("displayId")
                
                logger.info(f"Successfully created quote: {display_id} (ID: {quote_id})")
                
                return {
                    "success": True,
                    "quote_id": quote_id,
                    "display_id": display_id,
                    "client_account_id": client_account_id,
                    "description": description,
                    "amount": amount,
                    "quote_date": quote_date,
                    "expiry_date": expiry_date,
                    "status": status,
                    "title": title,
                    "message": f"Quote created successfully: {display_id}",
                    "data": quote_data
                }
            else:
                logger.error("Quote creation failed - no data returned")
                return {
                    "success": False,
                    "error": "Quote creation failed - no data returned from API"
                }
        
    except Exception as e:
        logger.error(f"Failed to create quote: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create quote"
        }