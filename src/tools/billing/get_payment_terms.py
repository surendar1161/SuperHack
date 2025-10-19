"""Get payment terms tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_payment_terms")


@tool
async def get_payment_terms() -> Dict[str, Any]:
    """
    Get list of available payment terms from SuperOps
    
    Returns:
        Dictionary containing payment terms list with success status
    """
    try:
        logger.info("Fetching payment terms list from SuperOps")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Use the exact GraphQL query from your working curl
            query = """
            query getPaymentTermList {
              getPaymentTermList {
                paymentTermId
                paymentTermName
                paymentTermValue
              }
            }
            """
            
            # Execute the GraphQL query directly
            result = await client.execute_graphql_query(query)
            
            if result and result.get("data") and result["data"].get("getPaymentTermList"):
                payment_terms = result["data"]["getPaymentTermList"]
                logger.info(f"Successfully retrieved {len(payment_terms)} payment terms")
                return {
                    "success": True,
                    "payment_terms": payment_terms,
                    "total_count": len(payment_terms),
                    "message": f"Retrieved {len(payment_terms)} payment terms"
                }
            
            logger.error(f"Failed to get payment terms: {result}")
            return {
                "success": False,
                "error": f"Failed to retrieve payment terms: {result}",
                "payment_terms": []
            }
                
    except Exception as e:
        logger.error(f"Error getting payment terms: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "payment_terms": []
        }


@tool
async def get_payment_term_by_id(
    payment_term_id: str
) -> Dict[str, Any]:
    """
    Get specific payment term by ID
    
    Args:
        payment_term_id: The ID of the payment term to retrieve
        
    Returns:
        Dictionary containing payment term details
    """
    try:
        logger.info(f"Fetching payment term details for ID: {payment_term_id}")
        
        # Get all payment terms and filter by ID
        result = await get_payment_terms()
        
        if result["success"]:
            payment_terms = result["payment_terms"]
            
            # Find the specific payment term
            for term in payment_terms:
                if term.get("paymentTermId") == payment_term_id:
                    logger.info(f"Found payment term: {term.get('paymentTermName')}")
                    return {
                        "success": True,
                        "payment_term": term,
                        "payment_term_id": term.get("paymentTermId"),
                        "payment_term_name": term.get("paymentTermName"),
                        "payment_term_value": term.get("paymentTermValue"),
                        "message": f"Retrieved payment term: {term.get('paymentTermName')}"
                    }
            
            logger.warning(f"Payment term not found: {payment_term_id}")
            return {
                "success": False,
                "error": f"Payment term not found: {payment_term_id}",
                "payment_term": None
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error getting payment term {payment_term_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "payment_term": None
        }


@tool
async def get_payment_term_by_name(
    payment_term_name: str
) -> Dict[str, Any]:
    """
    Get payment term by name (case-insensitive search)
    
    Args:
        payment_term_name: The name of the payment term to search for
        
    Returns:
        Dictionary containing payment term details
    """
    try:
        logger.info(f"Searching for payment term by name: {payment_term_name}")
        
        # Get all payment terms and filter by name
        result = await get_payment_terms()
        
        if result["success"]:
            payment_terms = result["payment_terms"]
            
            # Search for payment term by name (case-insensitive)
            search_name = payment_term_name.lower()
            matching_terms = []
            
            for term in payment_terms:
                term_name = term.get("paymentTermName", "").lower()
                if search_name in term_name:
                    matching_terms.append(term)
            
            if matching_terms:
                if len(matching_terms) == 1:
                    term = matching_terms[0]
                    logger.info(f"Found payment term: {term.get('paymentTermName')}")
                    return {
                        "success": True,
                        "payment_term": term,
                        "payment_term_id": term.get("paymentTermId"),
                        "payment_term_name": term.get("paymentTermName"),
                        "payment_term_value": term.get("paymentTermValue"),
                        "message": f"Retrieved payment term: {term.get('paymentTermName')}"
                    }
                else:
                    logger.info(f"Found {len(matching_terms)} matching payment terms")
                    return {
                        "success": True,
                        "payment_terms": matching_terms,
                        "total_matches": len(matching_terms),
                        "message": f"Found {len(matching_terms)} payment terms matching '{payment_term_name}'"
                    }
            else:
                logger.warning(f"No payment terms found matching: {payment_term_name}")
                return {
                    "success": False,
                    "error": f"No payment terms found matching: {payment_term_name}",
                    "payment_terms": []
                }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error searching payment terms: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "payment_terms": []
        }


@tool
async def get_payment_terms_summary() -> Dict[str, Any]:
    """
    Get a summary of all available payment terms with key statistics
    
    Returns:
        Dictionary containing payment terms summary and statistics
    """
    try:
        logger.info("Generating payment terms summary")
        
        # Get all payment terms
        result = await get_payment_terms()
        
        if result["success"]:
            payment_terms = result["payment_terms"]
            
            # Generate summary statistics
            total_terms = len(payment_terms)
            term_names = [term.get("paymentTermName", "") for term in payment_terms]
            term_values = [term.get("paymentTermValue", 0) for term in payment_terms if term.get("paymentTermValue")]
            
            # Calculate statistics
            avg_value = sum(term_values) / len(term_values) if term_values else 0
            min_value = min(term_values) if term_values else 0
            max_value = max(term_values) if term_values else 0
            
            summary = {
                "total_payment_terms": total_terms,
                "payment_term_names": term_names,
                "statistics": {
                    "average_value": round(avg_value, 2),
                    "minimum_value": min_value,
                    "maximum_value": max_value,
                    "terms_with_values": len(term_values)
                }
            }
            
            logger.info(f"Generated summary for {total_terms} payment terms")
            return {
                "success": True,
                "summary": summary,
                "payment_terms": payment_terms,
                "message": f"Generated summary for {total_terms} payment terms"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error generating payment terms summary: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "summary": None
        }