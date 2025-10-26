"""SuperOps IT API client for GraphQL operations"""

import aiohttp
import json
from typing import Any, Dict, List, Optional
from ..agents.config import AgentConfig
from ..utils.logger import get_logger
from .exceptions import SuperOpsAPIError, AuthenticationError, RateLimitError

class SuperOpsClient:
    """Client for interacting with SuperOps IT GraphQL API"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.session = None

        # SuperOps MSP API endpoint (WORKING FORMAT for tasks)
        self.api_url = "https://api.superops.ai/msp"

        # Headers based on WORKING curl command
        self.headers = {
            "Authorization": f"Bearer {self.config.superops_api_key}",
            "Content-Type": "application/json",
            "CustomerSubDomain": self.config.superops_customer_subdomain,  # Required for working API
            "Cookie": "JSESSIONID=6531DF9392FD53C1F787854DCD0F9C1C; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
        }

    async def connect(self):
        """Initialize connection to SuperOps IT API"""
        try:
            self.logger.info(f"Connecting to SuperOps MSP API at: {self.api_url}")

            # Create aiohttp session with proper connector settings
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(connector=connector)

            # Test connection with a simple query
            test_query = {
                "query": "query { __typename }"
            }

            async with self.session.post(
                self.api_url,
                json=test_query,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:

                if response.status == 200:
                    self.logger.info("Successfully connected to SuperOps IT API")
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key or insufficient permissions")
                elif response.status == 403:
                    raise AuthenticationError("Access forbidden - check API permissions")
                else:
                    error_text = await response.text()
                    raise AuthenticationError(f"Connection failed: {response.status} - {error_text}")

        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to SuperOps IT API: {e}")
            raise AuthenticationError(f"Connection failed: {e}")

    async def create_ticket(self, input_data):
        """Create a new ticket using SuperOps MSP API (WORKING FORMAT)"""
        try:
            # Use the WORKING MSP API format from successful curl command
            mutation = {
                "query": """
                    mutation createTicket($input: CreateTicketInput!) {
                        createTicket(input: $input) {
                            ticketId
                            status
                            subject
                            technician
                            site
                            requestType
                            source
                            client
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "source": "FORM",
                        "subject": input_data.get("subject", "API Created Ticket"),
                        "requestType": input_data.get("requestType", "Incident"),
                        "site": {
                            "id": input_data.get("siteId", "7206852887969157120")
                        },
                        "description": input_data.get("description", "Ticket created via API"),
                        "client": {
                            "accountId": input_data.get("clientId", "7206852887935602688")
                        }
                    }
                }
            }

            self.logger.info(f"Creating ticket with input: {input_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            # Use MSP API endpoint for ticket creation (working format)
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        # Handle case where result is None or empty
                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createTicket" in result["data"]:
                            create_result = result["data"]["createTicket"]
                            self.logger.debug(f"createTicket result: {create_result}")

                            # The createTicket mutation returns the ticket data directly
                            if create_result:
                                self.logger.info(f"Successfully created ticket: {create_result}")
                                # Format the response to match expected structure
                                formatted_result = {
                                    "id": create_result.get("ticketId"),
                                    "ticketId": create_result.get("ticketId"),
                                    "subject": create_result.get("subject"),
                                    "status": create_result.get("status"),
                                    "requestType": create_result.get("requestType"),
                                    "source": create_result.get("source"),
                                    "technician": create_result.get("technician"),
                                    "site": create_result.get("site"),
                                    "department": create_result.get("department")
                                }
                                return formatted_result
                            else:
                                self.logger.error("createTicket returned null")
                                raise SuperOpsAPIError("createTicket returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for ticket creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create ticket: {e}")
            raise SuperOpsAPIError(f"Ticket creation failed: {e}")

    async def update_ticket(self, ticket_id: str, update_data: Dict) -> Optional[Dict]:
        """Update a ticket using SuperOps MSP API (WORKING FORMAT)"""
        try:
            # Use the WORKING MSP API format from successful curl command
            mutation = {
                "query": """
                    mutation updateTicket($input: UpdateTicketInput!) {
                        updateTicket(input: $input) {
                            ticketId
                            status
                            subject
                            technician
                            site
                            requestType
                            source
                            client
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "ticketId": ticket_id,
                        **update_data
                    }
                }
            }

            self.logger.info(f"Updating ticket {ticket_id} with data: {update_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            # Use MSP API endpoint for ticket updates (working format)
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Update response status: {response.status}")
                self.logger.debug(f"Update response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "updateTicket" in result["data"]:
                            update_result = result["data"]["updateTicket"]
                            self.logger.debug(f"updateTicket result: {update_result}")

                            if update_result:
                                self.logger.info(f"Successfully updated ticket: {update_result}")
                                return {
                                    "id": update_result.get("ticketId"),
                                    "ticketId": update_result.get("ticketId"),
                                    "subject": update_result.get("subject"),
                                    "status": update_result.get("status"),
                                    "technician": update_result.get("technician"),
                                    "site": update_result.get("site"),
                                    "requestType": update_result.get("requestType"),
                                    "source": update_result.get("source"),
                                    "client": update_result.get("client")
                                }
                            else:
                                self.logger.error("updateTicket returned null")
                                raise SuperOpsAPIError("updateTicket returned null")

                        elif "errors" in result:
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL update errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected update response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for ticket update")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to update ticket: {e}")
            raise SuperOpsAPIError(f"Ticket update failed: {e}")

    async def get_work_status_list(self) -> Optional[Dict]:
        """Get work status list from SuperOps MSP API metadata endpoint"""
        try:
            query = {
                "query": """
                    query getWorkStatusList {
                        getWorkStatusList {
                            statusId
                            name
                            state
                        }
                    }
                """,
                "variables": {}
            }

            self.logger.info("Getting work status list from SuperOps")
            self.logger.debug(f"GraphQL query: {json.dumps(query, indent=2)}")

            # Use MSP API endpoint for metadata queries
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=query,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Work status response status: {response.status}")
                self.logger.debug(f"Work status response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "getWorkStatusList" in result["data"]:
                            status_list = result["data"]["getWorkStatusList"]
                            self.logger.debug(f"getWorkStatusList result: {status_list}")

                            if status_list is not None:
                                self.logger.info(f"Successfully retrieved {len(status_list)} work statuses")
                                return {
                                    "statusList": status_list,
                                    "count": len(status_list)
                                }
                            else:
                                self.logger.error("getWorkStatusList returned null")
                                raise SuperOpsAPIError("getWorkStatusList returned null")

                        elif "errors" in result:
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL work status errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected work status response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for work status access")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to get work status list: {e}")
            raise SuperOpsAPIError(f"Work status retrieval failed: {e}")

    async def create_invoice(self, input_data: Dict) -> Optional[Dict]:
        """Create an invoice using SuperOps MSP API (WORKING FORMAT)"""
        try:
            # Use the WORKING MSP API format from successful curl command
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

            self.logger.info(f"Creating invoice with input: {input_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            # Use MSP API endpoint for invoice creation (working format)
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Invoice creation response status: {response.status}")
                self.logger.debug(f"Invoice creation response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createInvoice" in result["data"]:
                            invoice_result = result["data"]["createInvoice"]
                            self.logger.debug(f"createInvoice result: {invoice_result}")

                            if invoice_result:
                                self.logger.info(f"Successfully created invoice: {invoice_result}")
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
                            else:
                                self.logger.error("createInvoice returned null")
                                raise SuperOpsAPIError("createInvoice returned null")

                        elif "errors" in result:
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL invoice creation errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected invoice creation response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for invoice creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create invoice: {e}")
            raise SuperOpsAPIError(f"Invoice creation failed: {e}")

    async def create_quote(self, input_data: Dict) -> Optional[Dict]:
        """Create a quote using SuperOps MSP API (WORKING FORMAT)"""
        try:
            # Use the WORKING MSP API format from successful curl command
            mutation = {
                "query": """
                    mutation createQuote($createQuote: CreateQuoteInput!) {
                        createQuote(input: $createQuote) {
                            quoteId
                            displayId
                            title
                            description
                            quoteDate
                            expiryDate
                            statusEnum
                            totalAmount
                            client
                            site
                            items {
                                serviceItem
                                quantity
                                unitPrice
                                discountRate
                                discountAmount
                                taxAmount
                            }
                        }
                    }
                """,
                "variables": {
                    "createQuote": input_data
                }
            }

            self.logger.info(f"Creating quote with input: {input_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            # Use MSP API endpoint for quote creation (working format)
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Quote creation response status: {response.status}")
                self.logger.debug(f"Quote creation response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createQuote" in result["data"]:
                            quote_result = result["data"]["createQuote"]
                            self.logger.debug(f"createQuote result: {quote_result}")

                            if quote_result:
                                self.logger.info(f"Successfully created quote: {quote_result}")
                                return {
                                    "id": quote_result.get("quoteId"),
                                    "quoteId": quote_result.get("quoteId"),
                                    "displayId": quote_result.get("displayId"),
                                    "title": quote_result.get("title"),
                                    "description": quote_result.get("description"),
                                    "quoteDate": quote_result.get("quoteDate"),
                                    "expiryDate": quote_result.get("expiryDate"),
                                    "status": quote_result.get("statusEnum"),
                                    "totalAmount": quote_result.get("totalAmount"),
                                    "client": quote_result.get("client"),
                                    "site": quote_result.get("site"),
                                    "items": quote_result.get("items"),
                                    "createdDate": quote_result.get("createdDate"),
                                    "modifiedDate": quote_result.get("modifiedDate"),
                                    "raw_data": quote_result
                                }
                            else:
                                self.logger.error("createQuote returned null")
                                raise SuperOpsAPIError("createQuote returned null")

                        elif "errors" in result:
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL quote creation errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected quote creation response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for quote creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create quote: {e}")
            raise SuperOpsAPIError(f"Quote creation failed: {e}")

    async def create_kb_article(self, input_data: Dict) -> Optional[Dict]:
        """Create a knowledge base article using SuperOps MSP API (WORKING FORMAT)"""
        try:
            # Use the WORKING MSP API format from successful curl command
            mutation = {
                "query": """
                    mutation ($input: CreateKbArticleInput!) {
                        createKbArticle(input: $input) {
                            itemId
                            name
                            description
                            status
                            parent {itemId}
                            createdBy
                            createdOn
                            lastModifiedBy
                            lastModifiedOn
                            viewCount
                            articleType
                            visibility { site}
                            loginRequired
                        }
                    }
                """,
                "variables": {
                    "input": input_data
                }
            }

            self.logger.info(f"Creating KB article with input: {input_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            # Use MSP API endpoint for KB article creation (working format)
            msp_api_url = "https://api.superops.ai/msp"

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"KB article creation response status: {response.status}")
                self.logger.debug(f"KB article creation response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createKbArticle" in result["data"]:
                            article_result = result["data"]["createKbArticle"]
                            self.logger.debug(f"createKbArticle result: {article_result}")

                            if article_result:
                                self.logger.info(f"Successfully created KB article: {article_result}")
                                return {
                                    "id": article_result.get("itemId"),
                                    "itemId": article_result.get("itemId"),
                                    "name": article_result.get("name"),
                                    "description": article_result.get("description"),
                                    "status": article_result.get("status"),
                                    "parent": article_result.get("parent"),
                                    "createdBy": article_result.get("createdBy"),
                                    "createdOn": article_result.get("createdOn"),
                                    "lastModifiedBy": article_result.get("lastModifiedBy"),
                                    "lastModifiedOn": article_result.get("lastModifiedOn"),
                                    "viewCount": article_result.get("viewCount"),
                                    "articleType": article_result.get("articleType"),
                                    "visibility": article_result.get("visibility"),
                                    "loginRequired": article_result.get("loginRequired"),
                                    "raw_data": article_result
                                }
                            else:
                                self.logger.error("createKbArticle returned null")
                                raise SuperOpsAPIError("createKbArticle returned null")

                        elif "errors" in result:
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL KB article creation errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected KB article creation response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for KB article creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create KB article: {e}")
            raise SuperOpsAPIError(f"KB article creation failed: {e}")

    async def create_task(self, input_data):
        """Create a new task using SuperOps MSP GraphQL mutation (WORKING FORMAT)"""
        try:
            # Use the WORKING mutation format from the successful curl command
            mutation = {
                "query": """
                    mutation createTask($input: CreateTaskInput!) {
                        createTask(input: $input) {
                            taskId
                            displayId
                            title
                            description
                            status
                            estimatedTime
                            scheduledStartDate
                            dueDate
                            overdue
                            actualStartDate
                            actualEndDate
                            technician
                            techGroup
                            module
                            ticket
                            workItem 
                        }
                    }
                """,
                "variables": {
                    "input": input_data
                }
            }

            self.logger.info(f"Creating task with input: {input_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            async with self.session.post(
                self.api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        # Handle case where result is None or empty
                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createTask" in result["data"]:
                            create_result = result["data"]["createTask"]
                            self.logger.debug(f"createTask result: {create_result}")

                            # The createTask mutation returns the task data directly
                            if create_result:
                                self.logger.info(f"Successfully created task: {create_result}")
                                # Return the complete task data
                                return create_result
                            else:
                                self.logger.error("createTask returned null")
                                raise SuperOpsAPIError("createTask returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for task creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            raise SuperOpsAPIError(f"Task creation failed: {e}")

    async def log_time_entry(self, time_entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a worklog timer entry for time tracking
        
        Args:
            time_entry_data: Dictionary containing time entry information
                - ticket_id: The ticket ID to log time for
                - duration: Duration in hours
                - description: Description of work performed
                - billable: Whether the time is billable (default: True)
                - activity_type: Type of activity performed
        
        Returns:
            Dictionary containing the created timer entry details
        """
        try:
            if not self.session:
                await self.connect()

            # Extract data from time_entry_data
            ticket_id = time_entry_data.get("ticket_id")
            duration_hours = time_entry_data.get("duration", 0)
            description = time_entry_data.get("description", "")
            billable = time_entry_data.get("billable", True)
            
            # Convert hours to minutes for the API
            duration_minutes = int(duration_hours * 60)

            # GraphQL mutation for creating worklog timer entry
            mutation = {
                "query": """
                    mutation ($timerEntryInput: CreateWorklogTimerEntryInput!) {
                        createWorklogTimerEntry(input: $timerEntryInput) {
                            timerId
                            billable
                            type
                            notes
                            running
                            timespent
                            segments { 
                                segmentId 
                                startTime 
                                endTime 
                                timespent 
                                afterHours 
                            }
                        }
                    }
                """,
                "variables": {
                    "timerEntryInput": {
                        "billable": billable,
                        "notes": description,
                        "type": "AUTOMATIC",
                        "workItem": {
                            "workId": str(ticket_id),
                            "module": "TICKET"
                        }
                    }
                }
            }

            self.logger.info(f"Creating time entry for ticket {ticket_id}: {duration_hours}h ({duration_minutes}m)")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            async with self.session.post(
                self.api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createWorklogTimerEntry" in result["data"]:
                            timer_entry = result["data"]["createWorklogTimerEntry"]
                            self.logger.debug(f"createWorklogTimerEntry result: {timer_entry}")

                            if timer_entry:
                                self.logger.info(f"Successfully created time entry: {timer_entry.get('timerId')}")
                                
                                # Format the response
                                formatted_result = {
                                    "id": timer_entry.get("timerId"),
                                    "timer_id": timer_entry.get("timerId"),
                                    "billable": timer_entry.get("billable"),
                                    "type": timer_entry.get("type"),
                                    "notes": timer_entry.get("notes"),
                                    "running": timer_entry.get("running"),
                                    "time_spent": timer_entry.get("timespent"),
                                    "segments": timer_entry.get("segments", []),
                                    "ticket_id": ticket_id,
                                    "duration_hours": duration_hours,
                                    "duration_minutes": duration_minutes
                                }
                                return formatted_result
                            else:
                                self.logger.error("createWorklogTimerEntry returned null")
                                raise SuperOpsAPIError("createWorklogTimerEntry returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for time logging")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create time entry: {e}")
            raise SuperOpsAPIError(f"Time entry creation failed: {e}")

    async def update_time_entry(self, timer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a worklog timer entry
        
        Args:
            timer_id: The timer ID to update
            update_data: Dictionary containing fields to update
                - notes: Updated description/notes
                - billable: Whether the time is billable (True/False)
                - running: Whether the timer is running (True/False)
        
        Returns:
            Dictionary containing the updated timer entry details
        """
        try:
            if not self.session:
                await self.connect()

            # Build the update input from provided data
            update_input = {"timerId": timer_id}
            
            if "notes" in update_data:
                update_input["notes"] = update_data["notes"]
            if "billable" in update_data:
                update_input["billable"] = update_data["billable"]
            if "running" in update_data:
                update_input["running"] = update_data["running"]

            # GraphQL mutation for updating worklog timer entry
            mutation = {
                "query": """
                    mutation ($updateTimerInput: UpdateWorklogTimerEntryInput!) {
                        updateWorklogTimerEntry(input: $updateTimerInput) {
                            timerId
                            billable
                            type
                            notes
                            running
                            timespent
                            segments { 
                                segmentId 
                                startTime 
                                endTime 
                                timespent 
                                afterHours 
                            }
                        }
                    }
                """,
                "variables": {
                    "updateTimerInput": update_input
                }
            }

            self.logger.info(f"Updating timer entry {timer_id} with data: {update_data}")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            async with self.session.post(
                self.api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "updateWorklogTimerEntry" in result["data"]:
                            timer_entry = result["data"]["updateWorklogTimerEntry"]
                            self.logger.debug(f"updateWorklogTimerEntry result: {timer_entry}")

                            if timer_entry:
                                self.logger.info(f"Successfully updated timer entry: {timer_entry.get('timerId')}")
                                
                                # Format the response
                                formatted_result = {
                                    "id": timer_entry.get("timerId"),
                                    "timer_id": timer_entry.get("timerId"),
                                    "billable": timer_entry.get("billable"),
                                    "type": timer_entry.get("type"),
                                    "notes": timer_entry.get("notes"),
                                    "running": timer_entry.get("running"),
                                    "time_spent": timer_entry.get("timespent"),
                                    "segments": timer_entry.get("segments", [])
                                }
                                return formatted_result
                            else:
                                self.logger.error("updateWorklogTimerEntry returned null")
                                raise SuperOpsAPIError("updateWorklogTimerEntry returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for timer update")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to update timer entry: {e}")
            raise SuperOpsAPIError(f"Timer entry update failed: {e}")

    async def get_technicians(self, page: int = 1, page_size: int = 100, conditions: List[Dict] = None) -> Dict[str, Any]:
        """
        Get list of technicians from SuperOps
        
        Args:
            page: Page number for pagination
            page_size: Number of technicians per page (max 100)
            conditions: List of filter conditions
        
        Returns:
            Dictionary containing technician list and pagination info
        """
        try:
            if not self.session:
                await self.connect()

            # Default conditions to get only technicians (role ID 3)
            if conditions is None:
                conditions = [
                    {
                        "attribute": "roles.roleId",
                        "operator": "is",
                        "value": 3
                    }
                ]

            # GraphQL query for getting technician list
            query = {
                "query": """
                    query getTechnicianList($input: ListInfoInput!) {
                        getTechnicianList(input: $input) {
                            userList { 
                                userId
                                name 
                                email
                            }
                            listInfo { 
                                page 
                                pageSize
                                totalCount
                            }
                        }
                    }
                """,
                "variables": {
                    "input": {
                        "page": page,
                        "pageSize": min(page_size, 100),  # Ensure max 100
                        "condition": conditions[0] if len(conditions) == 1 else {
                            "operator": "and",
                            "conditions": conditions
                        }
                    }
                }
            }

            self.logger.info(f"Getting technicians list (page {page}, size {page_size})")
            self.logger.debug(f"GraphQL query: {json.dumps(query, indent=2)}")

            async with self.session.post(
                self.api_url,
                json=query,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "getTechnicianList" in result["data"]:
                            technician_data = result["data"]["getTechnicianList"]
                            self.logger.debug(f"getTechnicianList result: {technician_data}")

                            if technician_data:
                                user_list = technician_data.get("userList", [])
                                list_info = technician_data.get("listInfo", {})
                                
                                self.logger.info(f"Successfully retrieved {len(user_list)} technicians")
                                
                                # Format the response
                                formatted_result = {
                                    "userList": user_list,
                                    "listInfo": list_info,
                                    "total_count": len(user_list),
                                    "page": list_info.get("page", page),
                                    "page_size": list_info.get("pageSize", page_size)
                                }
                                return formatted_result
                            else:
                                self.logger.error("getTechnicianList returned null")
                                raise SuperOpsAPIError("getTechnicianList returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for technician list")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to get technicians: {e}")
            raise SuperOpsAPIError(f"Technician list retrieval failed: {e}")

    async def create_worklog_entries(self, worklog_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create worklog entries using SuperOps MSP API
        
        Args:
            worklog_entries: List of worklog entry data dictionaries
                Each entry should contain:
                - billable: Whether the work is billable (True/False)
                - afterHours: Whether work was done after hours (True/False)
                - qty: Quantity/hours worked (string)
                - unitPrice: Price per unit (string)
                - billDateTime: Date and time in ISO format
                - notes: Description of work performed
                - workItem: Dictionary with workId and module
        
        Returns:
            Dictionary containing the created worklog entries
        """
        try:
            if not self.session:
                await self.connect()

            # Use MSP API endpoint for worklog entries
            msp_api_url = "https://api.superops.ai/msp"

            # GraphQL mutation for creating worklog entries
            mutation = {
                "query": """
                    mutation createWorklogEntries($input: [CreateWorklogEntryInput!]!) {
                        createWorklogEntries(input: $input) {
                            itemId
                            status
                            serviceItem
                            billable
                            afterHours
                            qty
                            unitPrice
                            billDateTime
                            technician
                            notes
                            workItem
                        }
                    }
                """,
                "variables": {
                    "input": worklog_entries
                }
            }

            self.logger.info(f"Creating {len(worklog_entries)} worklog entries")
            self.logger.debug(f"GraphQL mutation: {json.dumps(mutation, indent=2)}")

            async with self.session.post(
                msp_api_url,
                json=mutation,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                response_text = await response.text()
                self.logger.info(f"Response status: {response.status}")
                self.logger.debug(f"Response body: {response_text}")

                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        self.logger.debug(f"Parsed JSON result: {result}")

                        if result is None:
                            self.logger.error("API returned null/empty response")
                            raise SuperOpsAPIError("API returned null response")

                        if "data" in result and result["data"] is not None and "createWorklogEntries" in result["data"]:
                            worklog_data = result["data"]["createWorklogEntries"]
                            self.logger.debug(f"createWorklogEntries result: {worklog_data}")

                            if worklog_data is not None:
                                self.logger.info(f"Successfully created {len(worklog_data)} worklog entries")
                                
                                # Format the response
                                formatted_result = {
                                    "worklog_entries": worklog_data,
                                    "total_created": len(worklog_data),
                                    "success_count": len([entry for entry in worklog_data if entry.get("status") == "success"]),
                                    "entries": worklog_data
                                }
                                return formatted_result
                            else:
                                self.logger.error("createWorklogEntries returned null")
                                raise SuperOpsAPIError("createWorklogEntries returned null")

                        elif "errors" in result:
                            # GraphQL query-level errors
                            error_messages = [err.get("message", str(err)) for err in result["errors"]]
                            error_msg = "; ".join(error_messages)
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        else:
                            self.logger.error(f"Unexpected response format: {result}")
                            raise SuperOpsAPIError(f"Unexpected response format: {result}")

                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")

                elif response.status == 401:
                    self.logger.error("Authentication failed")
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    self.logger.error("Permission denied")
                    raise AuthenticationError("Insufficient permissions for worklog creation")
                else:
                    self.logger.error(f"HTTP error {response.status}: {response_text}")
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {response_text}")

        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to create worklog entries: {e}")
            raise SuperOpsAPIError(f"Worklog entries creation failed: {e}")

    async def disconnect(self):
        """Close connection to SuperOps IT API"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("Disconnected from SuperOps IT API")
    async def close(self):
        """Properly close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("SuperOps client session closed properly")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()    

    async def execute_graphql_query(self, query: str, variables: dict = None) -> dict:
        """
        Execute a GraphQL query against the SuperOps API
        
        Args:
            query: GraphQL query string
            variables: Variables for the query
            
        Returns:
            Dictionary containing the response data
        """
        try:
            payload = {
                "query": query
            }
            
            if variables:
                payload["variables"] = variables
            
            self.logger.debug(f"Executing GraphQL query: {query[:100]}...")
            
            async with self.session.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                self.logger.debug(f"GraphQL response status: {response.status}")
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        
                        if "errors" in result:
                            error_messages = [err.get("message", str(err)) if err.get("message") else str(err) for err in result["errors"]]
                            error_messages = [msg for msg in error_messages if msg]  # Filter out None/empty values
                            error_msg = "; ".join(error_messages) if error_messages else "Unknown GraphQL error"
                            self.logger.error(f"GraphQL query errors: {error_msg}")
                            raise SuperOpsAPIError(f"GraphQL errors: {error_msg}")
                        
                        return result
                        
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response: {e}")
                        raise SuperOpsAPIError(f"Invalid JSON response: {response_text[:200]}")
                
                elif response.status == 401:
                    raise AuthenticationError("Invalid API key or expired token")
                elif response.status == 403:
                    raise AuthenticationError("Access forbidden - check API permissions")
                else:
                    error_text = await response.text()
                    raise SuperOpsAPIError(f"HTTP error {response.status}: {error_text}")
                    
        except (AuthenticationError, SuperOpsAPIError):
            raise
        except Exception as e:
            self.logger.error(f"Failed to execute GraphQL query: {e}")
            raise SuperOpsAPIError(f"GraphQL query failed: {e}")
    async def get_client_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get client user details by user ID using GraphQL
        
        Args:
            user_id: The ID of the client user to retrieve
            
        Returns:
            Dictionary containing client user details
        """
        try:
            self.logger.info(f"Getting client user details for ID: {user_id}")
            
            query = """
            query getClientUser($input: ClientUserIdentifierInput!) {
              getClientUser(input: $input) {
                userId
                firstName
                lastName
                name
                email
                contactNumber
                reportingManager
                site {
                  id
                  name
                }
                role {
                  roleId
                  name
                }
                client {
                  accountId
                  name
                }
                customFields
              }
            }
            """
            
            variables = {
                "input": {
                    "userId": user_id
                }
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["getClientUser"]:
                client_user = result["data"]["getClientUser"]
                self.logger.info(f"Successfully retrieved client user: {client_user.get('name', 'Unknown')}")
                return {
                    "success": True,
                    "client_user": client_user
                }
            else:
                self.logger.error(f"Client user {user_id} not found")
                return {
                    "success": False,
                    "error": "Client user not found"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get client user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_client_users(self, page: int = 1, page_size: int = 50, 
                              site_id: str = None, client_id: str = None, 
                              search_term: str = None) -> Dict[str, Any]:
        """
        Get list of client users with optional filtering using GraphQL
        
        Args:
            page: Page number for pagination
            page_size: Number of users per page
            site_id: Optional site ID to filter by
            client_id: Optional client ID to filter by
            search_term: Optional search term to filter by
            
        Returns:
            Dictionary containing list of client users
        """
        try:
            self.logger.info(f"Getting client users list (page {page}, size {page_size})")
            
            query = """
            query getClientUsers($input: ClientUsersInput!) {
              getClientUsers(input: $input) {
                totalCount
                users {
                  userId
                  firstName
                  lastName
                  name
                  email
                  contactNumber
                  reportingManager
                  site {
                    id
                    name
                  }
                  role {
                    roleId
                    name
                  }
                  client {
                    accountId
                    name
                  }
                }
              }
            }
            """
            
            # Build input parameters
            input_params = {
                "page": page,
                "pageSize": page_size
            }
            
            if site_id:
                input_params["siteId"] = site_id
            if client_id:
                input_params["clientId"] = client_id
            if search_term:
                input_params["searchTerm"] = search_term
            
            variables = {
                "input": input_params
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["getClientUsers"]:
                client_users_data = result["data"]["getClientUsers"]
                users = client_users_data.get("users", [])
                total_count = client_users_data.get("totalCount", 0)
                
                self.logger.info(f"Successfully retrieved {len(users)} client users (total: {total_count})")
                return {
                    "success": True,
                    "client_users": users,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size
                }
            else:
                self.logger.error("Failed to retrieve client users")
                return {
                    "success": False,
                    "error": "Failed to retrieve client users",
                    "client_users": []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get client users: {e}")
            return {
                "success": False,
                "error": str(e),
                "client_users": []
            }

    async def get_payment_terms(self) -> Dict[str, Any]:
        """
        Get list of payment terms using GraphQL
        
        Returns:
            Dictionary containing payment terms list
        """
        try:
            self.logger.info("Getting payment terms list")
            
            query = """
            query getPaymentTermList {
              getPaymentTermList {
                paymentTermId
                paymentTermName
                paymentTermValue
              }
            }
            """
            
            result = await self.execute_graphql_query(query)
            
            if result and "data" in result and result["data"]["getPaymentTermList"]:
                payment_terms = result["data"]["getPaymentTermList"]
                self.logger.info(f"Successfully retrieved {len(payment_terms)} payment terms")
                return {
                    "success": True,
                    "payment_terms": payment_terms,
                    "total_count": len(payment_terms)
                }
            else:
                self.logger.error("Failed to retrieve payment terms")
                return {
                    "success": False,
                    "error": "Failed to retrieve payment terms",
                    "payment_terms": []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get payment terms: {e}")
            return {
                "success": False,
                "error": str(e),
                "payment_terms": []
            }

    async def get_offered_items(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get list of offered items/services using GraphQL
        
        Args:
            page: Page number for pagination
            page_size: Number of items per page
            
        Returns:
            Dictionary containing offered items list
        """
        try:
            self.logger.info(f"Getting offered items list (page {page}, size {page_size})")
            
            query = """
            query getOfferedItems($input: ListInfoInput) {
              getOfferedItems(input: $input) {
                items {
                  itemId 
                  serviceItem 
                  notes 
                }
                listInfo {
                  pageSize 
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
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["getOfferedItems"]:
                offered_items_data = result["data"]["getOfferedItems"]
                items = offered_items_data.get("items", [])
                list_info = offered_items_data.get("listInfo", {})
                
                self.logger.info(f"Successfully retrieved {len(items)} offered items")
                return {
                    "success": True,
                    "offered_items": items,
                    "total_items": len(items),
                    "page": page,
                    "page_size": list_info.get("pageSize", page_size),
                    "list_info": list_info
                }
            else:
                self.logger.error("Failed to retrieve offered items")
                return {
                    "success": False,
                    "error": "Failed to retrieve offered items",
                    "offered_items": []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get offered items: {e}")
            return {
                "success": False,
                "error": str(e),
                "offered_items": []
            }

    async def get_requester_roles(self) -> Dict[str, Any]:
        """
        Get list of requester roles using GraphQL
        
        Returns:
            Dictionary containing requester roles list
        """
        try:
            self.logger.info("Getting requester roles list")
            
            query = """
            query getRequesterRoleList {
              getRequesterRoleList {
                roleId
                name
                description
                roleType {
                    roleTypeId
                    name
                }
                roleFeatureList {
                  feature{
                    name
                  }
                }
                roleUserList
              }
            }
            """
            
            result = await self.execute_graphql_query(query)
            
            if result and "data" in result and result["data"]["getRequesterRoleList"]:
                requester_roles = result["data"]["getRequesterRoleList"]
                self.logger.info(f"Successfully retrieved {len(requester_roles)} requester roles")
                return {
                    "success": True,
                    "requester_roles": requester_roles,
                    "total_roles": len(requester_roles)
                }
            else:
                self.logger.error("Failed to retrieve requester roles")
                return {
                    "success": False,
                    "error": "Failed to retrieve requester roles",
                    "requester_roles": []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get requester roles: {e}")
            return {
                "success": False,
                "error": str(e),
                "requester_roles": []
            }

    async def get_script_list_by_type(self, script_type: str = "WINDOWS", page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get script list by type using GraphQL
        
        Args:
            script_type: Type of scripts to retrieve (WINDOWS, LINUX, etc.)
            page: Page number for pagination
            page_size: Number of scripts per page
            
        Returns:
            Dictionary containing script list and metadata
        """
        try:
            self.logger.info(f"Getting script list for type: {script_type}")
            
            query = """
            query getScriptListByType($input: ScriptListByTypeInput!) {
              getScriptListByType(input: $input) {
                scripts {
                  name
                  scriptId
                  description
                  addedBy
                }
                listInfo {
                  pageSize
                }
              }
            }
            """
            
            variables = {
                "input": {
                    "type": script_type,
                    "listInfo": {
                        "page": page,
                        "pageSize": page_size
                    }
                }
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["getScriptListByType"]:
                script_data = result["data"]["getScriptListByType"]
                scripts = script_data.get("scripts", [])
                list_info = script_data.get("listInfo", {})
                
                self.logger.info(f"Successfully retrieved {len(scripts)} scripts of type {script_type}")
                return {
                    "success": True,
                    "scripts": scripts,
                    "listInfo": list_info,
                    "script_type": script_type,
                    "total_scripts": len(scripts)
                }
            else:
                self.logger.error("Failed to retrieve script list")
                return {
                    "success": False,
                    "error": "Failed to retrieve script list",
                    "scripts": []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get script list: {e}")
            return {
                "success": False,
                "error": str(e),
                "scripts": []
            }

    async def create_alert(self, asset_id: str, message: str, description: str, severity: str = "High") -> Dict[str, Any]:
        """
        Create an alert for asset threshold breach using GraphQL
        
        Args:
            asset_id: ID of the asset that triggered the alert
            message: Alert message (e.g., "High CPU Usage")
            description: Detailed description of the alert
            severity: Alert severity level (High, Medium, Low)
            
        Returns:
            Dictionary containing alert creation result
        """
        try:
            self.logger.info(f"Creating alert for asset {asset_id}: {message}")
            
            query = """
            mutation createAlert($input: CreateAlertInput!) {
              createAlert(input: $input) {
                id
                message
                createdTime
                status
                severity
                description
                asset
                policy
              }
            }
            """
            
            variables = {
                "input": {
                    "assetId": asset_id,
                    "message": message,
                    "description": description,
                    "severity": severity
                }
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["createAlert"]:
                alert_data = result["data"]["createAlert"]
                
                self.logger.info(f"Successfully created alert: {alert_data.get('id')} for asset {asset_id}")
                return {
                    "success": True,
                    "alert": alert_data
                }
            else:
                self.logger.error("Failed to create alert")
                return {
                    "success": False,
                    "error": "Failed to create alert",
                    "alert": None
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            return {
                "success": False,
                "error": str(e),
                "alert": None
            }

    async def create_client_v2(self, name: str, stage: str = "Active", status: str = "Paid",
                              account_manager_id: str = "8275806997713629184", 
                              site_name: str = None, timezone: str = "America/Los_Angeles",
                              working_24x7: bool = False) -> Dict[str, Any]:
        """
        Create a new client organization using GraphQL V2 API
        
        Args:
            name: Name of the client organization
            stage: Client stage (Active, Prospect, etc.)
            status: Client status (Paid, Trial, etc.)
            account_manager_id: User ID of the account manager
            site_name: Name of the headquarters site
            timezone: Timezone code for the site
            working_24x7: Whether the site operates 24/7
            
        Returns:
            Dictionary containing client creation result
        """
        try:
            self.logger.info(f"Creating client organization: {name}")
            
            # Generate site name if not provided
            if not site_name:
                import random
                site_name = f"{name.replace(' ', '')}HQ{random.randint(100, 999)}"
            
            query = """
            mutation createClientV2($input: CreateClientInputV2!) {
              createClientV2(input: $input) {
                accountId
                name
                stage 
                status 
                emailDomains
                accountManager 
                hqSite 
                customFields
              }
            }
            """
            
            variables = {
                "input": {
                    "name": name,
                    "stage": stage,
                    "status": status,
                    "accountManager": {
                        "userId": int(account_manager_id)
                    },
                    "hqSite": {
                        "name": site_name,
                        "working24x7": working_24x7,
                        "timezoneCode": timezone
                    }
                }
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["createClientV2"]:
                client_data = result["data"]["createClientV2"]
                
                self.logger.info(f"Successfully created client: {client_data.get('accountId')} - {name}")
                return {
                    "success": True,
                    "client": client_data
                }
            else:
                # Check for specific error types
                error_msg = "Failed to create client"
                if result and "errors" in result:
                    errors = result["errors"]
                    for error in errors:
                        if "extensions" in error and "clientError" in error["extensions"]:
                            client_errors = error["extensions"]["clientError"]
                            for client_error in client_errors:
                                if client_error.get("code") == "unique_validation_failed":
                                    if "name" in client_error.get("param", {}).get("attributes", []):
                                        error_msg = f"Client name '{name}' already exists. Please use a unique name."
                
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "client": None
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create client: {e}")
            return {
                "success": False,
                "error": str(e),
                "client": None
            }

    async def create_ticket_note(self, ticket_id: str, content: str,
                                added_by_user_id: str = "8275806997713629184",
                                privacy_type: str = "PUBLIC", 
                                added_on: str = None) -> Dict[str, Any]:
        """
        Create a note for a ticket using GraphQL
        
        Args:
            ticket_id: ID of the ticket to add note to
            content: Content of the note
            added_by_user_id: User ID of the person adding the note
            privacy_type: Privacy level (PUBLIC, PRIVATE)
            added_on: Timestamp when note was added (ISO format)
            
        Returns:
            Dictionary containing note creation result
        """
        try:
            self.logger.info(f"Creating note for ticket {ticket_id}")
            
            # Generate timestamp if not provided
            if not added_on:
                from datetime import datetime
                added_on = datetime.now().isoformat()
            
            query = """
            mutation createTicketNote($input: CreateTicketNoteInput!) {
              createTicketNote(input: $input) {
                noteId
                addedBy
                addedOn
                content
                attachments {
                 fileName
                }
                privacyType
              }
            }
            """
            
            variables = {
                "input": {
                    "ticket": {
                        "ticketId": ticket_id
                    },
                    "content": content,
                    "addedBy": {
                        "userId": int(added_by_user_id)
                    },
                    "addedOn": added_on,
                    "privacyType": privacy_type
                }
            }
            
            result = await self.execute_graphql_query(query, variables)
            
            if result and "data" in result and result["data"]["createTicketNote"]:
                note_data = result["data"]["createTicketNote"]
                
                self.logger.info(f"Successfully created note: {note_data.get('noteId')} for ticket {ticket_id}")
                return {
                    "success": True,
                    "note": note_data
                }
            else:
                self.logger.error("Failed to create ticket note")
                return {
                    "success": False,
                    "error": "Failed to create ticket note",
                    "note": None
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create ticket note: {e}")
            return {
                "success": False,
                "error": str(e),
                "note": None
            }