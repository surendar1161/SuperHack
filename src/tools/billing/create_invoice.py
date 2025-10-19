"""Create invoice tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date

# For now, we'll use a simple decorator until strands is available
def tool(func):
    """Simple tool decorator placeholder"""
    return func

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_invoice")

def get_logger(name):
    """Simple logger placeholder"""
    return logging.getLogger(name)

class SimpleSuperOpsClient:
    """Simplified SuperOps client for invoice creation"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        
        # Headers for MSP API
        self.headers = {
            "Authorization": f"Bearer {self.config.superops_api_key}",
            "Content-Type": "application/json",
            "CustomerSubDomain": self.config.superops_customer_subdomain,
            "Cookie": "JSESSIONID=C8136EE789722E75C5C0806BB154EDC6; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
        }
    
    async def create_invoice(self, input_data):
        """Create an invoice using SuperOps MSP API"""
        import aiohttp
        import json
        
        mutation = {
            "query": """
                mutation createInvoice($input: CreateInvoiceInput!) {
                    createInvoice(input: $input) {
                        invoiceId
                        displayId
                        client
                        site
                        invoiceDate
                        dueDate
                        statusEnum
                        sentToClient
                        discountAmount
                        additionalDiscount
                        additionalDiscountRate
                        totalAmount
                        notes
                        items { 
                            serviceItem 
                            discountRate 
                            taxAmount 
                        } 
                        paymentDate
                        totalAmount
                        paymentMethod
                        paymentReference
                        invoicePaymentTerm
                    }
                }
            """,
            "variables": {
                "input": input_data
            }
        }
        
        msp_api_url = "https://api.superops.ai/msp"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    result = json.loads(response_text)
                    
                    if "data" in result and result["data"] and "createInvoice" in result["data"]:
                        invoice_result = result["data"]["createInvoice"]
                        
                        if invoice_result:
                            return {
                                "id": invoice_result.get("invoiceId"),
                                "invoiceId": invoice_result.get("invoiceId"),
                                "displayId": invoice_result.get("displayId"),
                                "client": invoice_result.get("client"),
                                "site": invoice_result.get("site"),
                                "invoiceDate": invoice_result.get("invoiceDate"),
                                "dueDate": invoice_result.get("dueDate"),
                                "status": invoice_result.get("statusEnum"),
                                "totalAmount": invoice_result.get("totalAmount"),
                                "items": invoice_result.get("items"),
                                "notes": invoice_result.get("notes"),
                                "raw_data": invoice_result
                            }
                    elif "errors" in result:
                        error_messages = [err.get("message", str(err)) for err in result["errors"]]
                        error_msg = "; ".join(error_messages)
                        raise Exception(f"GraphQL errors: {error_msg}")
                    else:
                        raise Exception(f"Unexpected response format: {result}")
                else:
                    raise Exception(f"HTTP error {response.status}: {response_text}")
        
        return None


@tool
async def create_invoice(
    client_id: str = None,  # For backward compatibility
    client_account_id: str = None,
    description: str = "Professional IT Services",
    amount: float = 100.0,
    site_id: str = "7206852887969157120",  # Default site ID
    service_item_id: str = "4478246199507894272",  # Default service item ID
    invoice_date: str = None,
    due_date: str = None,
    items: List[Dict[str, Any]] = None,
    status: str = "DRAFT",
    title: Optional[str] = None,
    memo: Optional[str] = None,
    footer: Optional[str] = None,
    additional_discount: Optional[str] = None,
    additional_discount_rate: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new invoice in SuperOps billing system
    
    Args:
        client_account_id: The account ID of the client to bill
        site_id: The site ID where services were provided
        invoice_date: Invoice date in YYYY-MM-DD format (e.g., "2025-01-01")
        due_date: Payment due date in YYYY-MM-DD format (e.g., "2025-02-01")
        items: List of invoice items, each containing:
            - billed_date: Date when service was provided (YYYY-MM-DD)
            - service_item_id: ID of the service item to bill
            - details: Description of the service provided
            - quantity: Quantity of service units (as string)
            - unit_price: Price per unit (as string)
            - discount_rate: Discount percentage (as string, optional)
            - discount_amount: Fixed discount amount (as string, optional)
            - taxable: Whether the item is taxable (boolean, default: true)
        status: Invoice status - DRAFT, SENT, PAID, etc. (default: "DRAFT")
        title: Invoice title/subject (optional)
        memo: Internal memo/notes (optional)
        footer: Footer text for the invoice (optional)
        additional_discount: Additional discount amount for entire invoice (optional)
        additional_discount_rate: Additional discount rate for entire invoice (optional)
        
    Returns:
        Dictionary containing invoice creation results with success status, invoice ID, and details
    """
    try:
        # Handle backward compatibility for parameter names
        if client_id and not client_account_id:
            client_account_id = client_id
        elif not client_account_id:
            return {
                "success": False,
                "error": "Either client_id or client_account_id must be provided",
                "message": "Invoice creation failed - no client specified"
            }
        
        logger.info(f"Creating invoice for client {client_account_id}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
        
            # Set default dates if not provided
            if not invoice_date:
                from datetime import date
                invoice_date = date.today().strftime("%Y-%m-%d")
            
            if not due_date:
                from datetime import timedelta
                invoice_dt = datetime.strptime(invoice_date, "%Y-%m-%d").date()
                due_dt = invoice_dt + timedelta(days=30)
                due_date = due_dt.strftime("%Y-%m-%d")
            
            # Validate date formats
            try:
                datetime.strptime(invoice_date, "%Y-%m-%d")
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"Invalid date format. Use YYYY-MM-DD format: {e}",
                    "message": "Invoice creation failed due to invalid date format"
                }
            
            # Create default items if not provided
            if not items or len(items) == 0:
                items = [{
                    "billed_date": invoice_date,
                    "service_item_id": service_item_id,
                    "details": description,
                    "quantity": "1",
                    "unit_price": str(amount),
                    "discount_rate": "0",
                    "discount_amount": "0",
                    "taxable": True
                }]
        
            # Format items for SuperOps API
            formatted_items = []
            for item in items:
                # Validate required fields
                required_fields = ["billed_date", "service_item_id", "details", "quantity", "unit_price"]
                for field in required_fields:
                    if field not in item:
                        return {
                            "success": False,
                            "error": f"Missing required field '{field}' in invoice item",
                            "message": "Invoice creation failed due to missing item fields"
                        }
                
                # Validate billed_date format
                try:
                    datetime.strptime(item["billed_date"], "%Y-%m-%d")
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid billed_date format in item. Use YYYY-MM-DD format",
                        "message": "Invoice creation failed due to invalid item date format"
                    }
                
                formatted_item = {
                    "billedDate": item["billed_date"],
                    "serviceItem": {
                        "itemId": item["service_item_id"]
                    },
                    "details": item["details"],
                    "quantity": str(item["quantity"]),
                    "unitPrice": str(item["unit_price"]),
                    "taxable": item.get("taxable", True)
                }
                
                # Add optional discount fields
                if "discount_rate" in item:
                    formatted_item["discountRate"] = str(item["discount_rate"])
                if "discount_amount" in item:
                    formatted_item["discountAmount"] = str(item["discount_amount"])
                
                formatted_items.append(formatted_item)
        
            # Build invoice input data according to SuperOps API format
            invoice_input = {
                "client": {
                    "accountId": client_account_id
                },
                "site": {
                    "id": site_id
                },
                "statusEnum": status.upper(),
                "invoiceDate": invoice_date,
                "dueDate": due_date,
                "addItems": formatted_items
            }
            
            # Add optional fields
            if additional_discount:
                invoice_input["additionalDiscount"] = str(additional_discount)
            if additional_discount_rate:
                invoice_input["additionalDiscountRate"] = str(additional_discount_rate)
            if memo:
                invoice_input["memo"] = memo
            if title:
                invoice_input["title"] = title
            if footer:
                invoice_input["footer"] = footer
            
            # GraphQL mutation matching the working curl format
            mutation = """
            mutation createInvoice($input: CreateInvoiceInput!) {
              createInvoice(input: $input) {
                invoiceId
                displayId
                client
                site
                invoiceDate
                dueDate
                statusEnum
                sentToClient
                discountAmount
                additionalDiscount
                additionalDiscountRate
                totalAmount
                notes
                items { serviceItem discountRate taxAmount } 
                paymentDate
                totalAmount
                paymentMethod
                paymentReference
                invoicePaymentTerm
              }
            }
            """
            
            variables = {
                "input": invoice_input
            }
            
            # Execute the GraphQL mutation
            result = await client.execute_graphql_query(mutation, variables)
        
            if result and "data" in result and result["data"]["createInvoice"]:
                invoice_data = result["data"]["createInvoice"]
                invoice_id = invoice_data.get('invoiceId')
                display_id = invoice_data.get('displayId')
                total_amount = invoice_data.get('totalAmount')
                
                logger.info(f"Successfully created invoice: {display_id} (ID: {invoice_id})")
                
                return {
                    "success": True,
                    "invoice_id": invoice_id,
                    "display_id": display_id,
                    "client_account_id": client_account_id,
                    "site_id": site_id,
                    "invoice_date": invoice_date,
                    "due_date": due_date,
                    "status": status,
                    "total_amount": total_amount,
                    "items_count": len(items),
                    "amount": amount,
                    "description": description,
                    "message": f"Invoice created successfully: {display_id}",
                    "data": invoice_data
                }
            else:
                logger.error("Invoice creation returned no result")
                return {
                    "success": False,
                    "error": "No result returned from SuperOps API",
                    "message": "Invoice creation failed - no response from API"
                }
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create invoice due to unexpected error"
        }


@tool
async def create_simple_invoice(
    client_account_id: str,
    site_id: str,
    service_item_id: str,
    service_description: str,
    quantity: float = 1.0,
    unit_price: float = 100.0,
    invoice_date: Optional[str] = None,
    due_date: Optional[str] = None,
    discount_rate: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a simple invoice with a single service item (convenience function)
    
    Args:
        client_account_id: The account ID of the client to bill
        site_id: The site ID where services were provided
        service_item_id: ID of the service item to bill
        service_description: Description of the service provided
        quantity: Quantity of service units (default: 1.0)
        unit_price: Price per unit (default: 100.0)
        invoice_date: Invoice date in YYYY-MM-DD format (default: today)
        due_date: Payment due date in YYYY-MM-DD format (default: 30 days from today)
        discount_rate: Discount percentage (optional)
        
    Returns:
        Dictionary containing invoice creation results
    """
    try:
        # Set default dates if not provided
        if not invoice_date:
            invoice_date = date.today().strftime("%Y-%m-%d")
        
        if not due_date:
            # Default to 30 days from invoice date
            from datetime import timedelta
            invoice_dt = datetime.strptime(invoice_date, "%Y-%m-%d").date()
            due_dt = invoice_dt + timedelta(days=30)
            due_date = due_dt.strftime("%Y-%m-%d")
        
        # Create single item
        item = {
            "billed_date": invoice_date,
            "service_item_id": service_item_id,
            "details": service_description,
            "quantity": quantity,
            "unit_price": unit_price,
            "taxable": True
        }
        
        # Add discount if provided
        if discount_rate is not None:
            item["discount_rate"] = discount_rate
        
        # Call the main create_invoice function
        return await create_invoice(
            client_account_id=client_account_id,
            site_id=site_id,
            invoice_date=invoice_date,
            due_date=due_date,
            items=[item],
            status="DRAFT",
            title=f"Service Invoice - {service_description}"
        )
        
    except Exception as e:
        logger.error(f"Failed to create simple invoice: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create simple invoice"
        }