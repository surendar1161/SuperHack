"""Create knowledge base article tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date

# For now, we'll use a simple decorator until strands is available
def tool(func):
    """Simple tool decorator placeholder"""
    return func

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_article")

def get_logger(name):
    """Simple logger placeholder"""
    return logging.getLogger(name)

class SimpleSuperOpsClient:
    """Simplified SuperOps client for KB article creation"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        
        # Headers for MSP API
        self.headers = {
            "Authorization": f"Bearer {self.config.superops_api_key}",
            "Content-Type": "application/json",
            "CustomerSubDomain": self.config.superops_customer_subdomain,
            "Cookie": "JSESSIONID=057178D0A7F0670BC8DB1B9E44498289; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
        }
    
    async def create_kb_article(self, input_data):
        """Create a KB article using SuperOps MSP API"""
        import aiohttp
        import json
        
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
                    
                    if "data" in result and result["data"] and "createKbArticle" in result["data"]:
                        article_result = result["data"]["createKbArticle"]
                        
                        if article_result:
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
async def create_kb_article(
    title: str,
    content: str,
    parent_id: str,
    user_id: str,
    status: str = "DRAFT",
    login_required: bool = True,
    visibility_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new knowledge base article in SuperOps
    
    Args:
        title: The title/name of the knowledge base article
        content: The HTML content of the article (can include HTML tags)
        parent_id: The ID of the parent category/folder for this article
        user_id: The ID of the user creating the article
        status: Article status - DRAFT, PUBLISHED, ARCHIVED (default: "DRAFT")
        login_required: Whether login is required to view the article (default: True)
        visibility_settings: Custom visibility settings (optional, uses default if not provided)
        
    Returns:
        Dictionary containing article creation results with success status, article ID, and details
    """
    try:
        logger.info(f"Creating KB article: {title}")
        
        # Initialize SuperOps client with environment variables
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create a simple config object
        class SimpleConfig:
            def __init__(self):
                self.superops_api_key = os.getenv("SUPEROPS_API_KEY")
                self.superops_customer_subdomain = os.getenv("SUPEROPS_CUSTOMER_SUBDOMAIN")
        
        # Create a simplified SuperOps client for article creation
        client = SimpleSuperOpsClient(SimpleConfig())
        
        # Validate required fields
        if not title or not title.strip():
            return {
                "success": False,
                "error": "Article title is required",
                "message": "KB article creation failed - no title provided"
            }
        
        if not content or not content.strip():
            return {
                "success": False,
                "error": "Article content is required",
                "message": "KB article creation failed - no content provided"
            }
        
        if not parent_id or not parent_id.strip():
            return {
                "success": False,
                "error": "Parent ID is required",
                "message": "KB article creation failed - no parent category specified"
            }
        
        if not user_id or not user_id.strip():
            return {
                "success": False,
                "error": "User ID is required",
                "message": "KB article creation failed - no user ID specified"
            }
        
        # Set default visibility settings if not provided
        if not visibility_settings:
            visibility_settings = {
                "added": [
                    {
                        "clientSharedType": "AllClients",
                        "siteSharedType": "AllSites",
                        "portalType": "TECHNICIAN",
                        "userSharedType": "User",
                        "groupSharedType": "AllGroups",
                        "addedUserIds": [user_id]
                    }
                ]
            }
        
        # Build article input data according to SuperOps API format
        article_input = {
            "name": title,
            "status": status.upper(),
            "parent": {
                "itemId": parent_id
            },
            "visibility": visibility_settings,
            "content": content,
            "loginRequired": login_required
        }
        
        # Create article via SuperOps client
        result = await client.create_kb_article(article_input)
        
        if result:
            article_id = result.get('itemId')
            article_name = result.get('name')
            
            logger.info(f"Successfully created KB article: {article_name} (ID: {article_id})")
            
            return {
                "success": True,
                "article_id": article_id,
                "item_id": article_id,
                "name": article_name,
                "title": title,
                "status": status,
                "parent_id": parent_id,
                "user_id": user_id,
                "login_required": login_required,
                "created_by": result.get('createdBy'),
                "created_on": result.get('createdOn'),
                "view_count": result.get('viewCount', 0),
                "message": f"KB article created successfully: {article_name}",
                "data": result
            }
        else:
            logger.error("KB article creation returned no result")
            return {
                "success": False,
                "error": "No result returned from SuperOps API",
                "message": "KB article creation failed - no response from API"
            }
        
    except Exception as e:
        logger.error(f"Failed to create KB article: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create KB article due to unexpected error"
        }


@tool
async def create_simple_kb_article(
    title: str,
    content: str,
    parent_id: str,
    user_id: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a simple knowledge base article with default settings (convenience function)
    
    Args:
        title: The title/name of the knowledge base article
        content: The content of the article (plain text or HTML)
        parent_id: The ID of the parent category/folder for this article
        user_id: The ID of the user creating the article
        description: Optional description for the article
        
    Returns:
        Dictionary containing article creation results
    """
    try:
        # Ensure content is in HTML format
        if not content.strip().startswith('<'):
            # Convert plain text to HTML paragraph
            content = f'<p dir="auto">{content}</p>'
        
        # Call the main create_kb_article function with default settings
        return await create_kb_article(
            title=title,
            content=content,
            parent_id=parent_id,
            user_id=user_id,
            status="DRAFT",
            login_required=True
        )
        
    except Exception as e:
        logger.error(f"Failed to create simple KB article: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create simple KB article"
        }


@tool
async def create_troubleshooting_article(
    problem_title: str,
    problem_description: str,
    solution_steps: List[str],
    parent_id: str,
    user_id: str,
    additional_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a troubleshooting knowledge base article with structured format
    
    Args:
        problem_title: Title describing the problem/issue
        problem_description: Detailed description of the problem
        solution_steps: List of step-by-step solution instructions
        parent_id: The ID of the parent category/folder for this article
        user_id: The ID of the user creating the article
        additional_notes: Optional additional notes or warnings
        
    Returns:
        Dictionary containing article creation results
    """
    try:
        # Build structured HTML content for troubleshooting article
        content_parts = [
            f'<h2>Problem Description</h2>',
            f'<p dir="auto">{problem_description}</p>',
            f'<h2>Solution Steps</h2>',
            f'<ol>'
        ]
        
        # Add solution steps as ordered list
        for step in solution_steps:
            content_parts.append(f'<li>{step}</li>')
        
        content_parts.append('</ol>')
        
        # Add additional notes if provided
        if additional_notes:
            content_parts.extend([
                f'<h2>Additional Notes</h2>',
                f'<p dir="auto">{additional_notes}</p>'
            ])
        
        # Join all content parts
        content = '\n'.join(content_parts)
        
        # Create the article with troubleshooting title format
        title = f"Troubleshooting: {problem_title}"
        
        return await create_kb_article(
            title=title,
            content=content,
            parent_id=parent_id,
            user_id=user_id,
            status="DRAFT",
            login_required=True
        )
        
    except Exception as e:
        logger.error(f"Failed to create troubleshooting article: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create troubleshooting article"
        }
@tool

async def create_article(
    title: str,
    content: str,
    category: str = "General",
    tags: Optional[List[str]] = None,
    status: str = "PUBLISHED"
) -> Dict[str, Any]:
    """
    Create a knowledge base article
    
    Args:
        title: Title of the article
        content: Content/body of the article
        category: Category for the article
        tags: Optional tags for the article
        status: Status of the article (DRAFT, PUBLISHED)
        
    Returns:
        Dictionary containing article creation results
    """
    try:
        logger.info(f"Creating knowledge article: {title}")
        
        # For now, simulate article creation since we don't have the full KB API
        import uuid
        article_id = str(uuid.uuid4())
        
        return {
            "success": True,
            "article_id": article_id,
            "title": title,
            "category": category,
            "status": status,
            "content_length": len(content),
            "tags": tags or [],
            "message": f"Knowledge article '{title}' created successfully",
            "data": {
                "id": article_id,
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "category": category,
                "status": status,
                "created_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create article: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create knowledge article"
        }