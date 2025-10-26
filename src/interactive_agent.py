#!/usr/bin/env python3
"""
Interactive SuperOps IT Technician Agent CLI
Provides a user-friendly menu system to interact with all agents and tools
"""
import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

console = Console()

class InteractiveAgent:
    """Interactive CLI for SuperOps IT Technician Agent System"""
    
    def __init__(self):
        self.console = Console()
        self.agents = {
            "1": {
                "name": "User Management Agent",
                "description": "Manage technicians, users, and roles",
                "tools": {
                    "1": {"name": "Get Technicians", "func": "get_technicians", "params": []},
                    "2": {"name": "Create Technician", "func": "create_technician", "params": ["first_name", "last_name"]},
                    "3": {"name": "Create Client Organization", "func": "create_client", "params": ["name", "stage", "status", "account_manager_id"]},
                    "4": {"name": "Create Client User", "func": "create_client_user", "params": ["first_name", "last_name", "email", "client_account_id"]},
                    "5": {"name": "Get Client User", "func": "get_client_user", "params": ["user_id"]},
                    "6": {"name": "Get Requester Roles", "func": "get_requester_roles", "params": []}
                }
            },
            "2": {
                "name": "Task Management Agent",
                "description": "Handle tasks and tickets",
                "tools": {
                    "1": {"name": "Create Task", "func": "create_task", "params": ["title", "description", "estimated_time", "status"]},
                    "2": {"name": "Create Ticket", "func": "create_ticket", "params": ["title", "description", "priority"]},
                    "3": {"name": "Update Ticket", "func": "update_ticket", "params": ["ticket_id", "status"]},
                    "4": {"name": "Add Ticket Note", "func": "create_ticket_note", "params": ["ticket_id", "content", "privacy_type"]}
                }
            },
            "3": {
                "name": "Workflow Agent",
                "description": "Time tracking and work logging",
                "tools": {
                    "1": {"name": "Log Work", "func": "log_work", "params": ["ticket_id", "time_spent", "description", "work_type"]},
                    "2": {"name": "Track Time", "func": "track_time", "params": ["ticket_id", "time_spent", "description"]}
                }
            },
            "4": {
                "name": "Analytics Agent",
                "description": "Performance metrics and monitoring",
                "tools": {
                    "1": {"name": "Performance Metrics", "func": "performance_metrics", "params": []},
                    "2": {"name": "View Analytics", "func": "view_analytics", "params": ["dashboard_type"]},
                    "3": {"name": "Create Alert", "func": "create_alert", "params": ["asset_id", "message", "description", "severity"]}
                }
            },
            "5": {
                "name": "Knowledge Agent",
                "description": "AI analysis and knowledge management",
                "tools": {
                    "1": {"name": "Create Article", "func": "create_article", "params": ["title", "content", "category"]},
                    "2": {"name": "Analyze Request", "func": "analyze_request", "params": ["request_text", "priority"]},
                    "3": {"name": "Generate Suggestions", "func": "generate_suggestions", "params": ["issue_description", "category"]},
                    "4": {"name": "Get Script List", "func": "get_script_list_by_type", "params": ["script_type", "page", "page_size"]}
                }
            },
            "6": {
                "name": "Billing Agent",
                "description": "Quotes, invoices, and billing",
                "tools": {
                    "1": {"name": "Create Quote", "func": "create_quote", "params": ["client_id", "description", "amount"]},
                    "2": {"name": "Create Invoice", "func": "create_invoice", "params": ["client_id", "description", "amount"]},
                    "3": {"name": "Get Payment Terms", "func": "get_payment_terms", "params": []},
                    "4": {"name": "Get Offered Items", "func": "get_offered_items", "params": ["page", "page_size"]}
                }
            }
        }
        
        # Default values for common parameters
        self.defaults = {
            "client_id": "7206852887935602688",
            "user_id": "7206852888145317888",
            "asset_id": "4293925678745489408",
            "ticket_id": "8951918998690930688",
            "page": "1",
            "page_size": "10",
            "priority": "High",
            "severity": "High",
            "status": "In Progress",
            "work_type": "Investigation",
            "category": "Network",
            "dashboard_type": "ticket_summary",
            "script_type": "WINDOWS",
            "title": "Demo Task Oct 26 2025 - System Maintenance",
            "description": "Demo work performed on October 26, 2025",
            "content": "Investigation update Oct 26 2025: Network access points need replacement",
            "message": "High CPU Usage Alert Oct 26 2025",
            "first_name": "Demo",
            "last_name": "Technician Oct 26 2025",
            "name": "Demo Client Org Oct 26 2025"
        }

    def display_header(self):
        """Display the application header"""
        header = Text("🚀 SuperOps IT Technician Agent System", style="bold blue")
        subtitle = Text("Interactive CLI - Choose agents and tools to execute", style="italic")
        
        panel = Panel.fit(
            f"{header}\n{subtitle}",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def display_agents_menu(self):
        """Display the main agents menu"""
        table = Table(title="🤖 Available Agents", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Agent", style="green", width=25)
        table.add_column("Description", style="white", width=40)
        table.add_column("Tools", style="yellow", width=8)
        
        for key, agent in self.agents.items():
            table.add_row(
                key,
                agent["name"],
                agent["description"],
                str(len(agent["tools"]))
            )
        
        table.add_row("0", "Exit", "Exit the application", "")
        
        self.console.print(table)
        self.console.print()

    def display_tools_menu(self, agent_key: str):
        """Display tools menu for selected agent"""
        agent = self.agents[agent_key]
        
        table = Table(title=f"🔧 {agent['name']} - Available Tools", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Tool", style="green", width=30)
        table.add_column("Parameters", style="white", width=50)
        
        for key, tool in agent["tools"].items():
            params_str = ", ".join(tool["params"]) if tool["params"] else "No parameters required"
            table.add_row(
                key,
                tool["name"],
                params_str
            )
        
        table.add_row("0", "Back to Agents Menu", "")
        
        self.console.print(table)
        self.console.print()

    def get_user_input(self, param_name: str, param_type: str = "str") -> str:
        """Get user input for a parameter with smart defaults"""
        default_value = self.defaults.get(param_name, "")
        
        if default_value:
            prompt_text = f"Enter {param_name.replace('_', ' ')} [default: {default_value}]"
        else:
            prompt_text = f"Enter {param_name.replace('_', ' ')}"
        
        user_input = Prompt.ask(prompt_text, default=default_value if default_value else None)
        
        # Type conversion
        if param_type == "int":
            try:
                return int(user_input)
            except ValueError:
                return int(default_value) if default_value else 0
        elif param_type == "float":
            try:
                return float(user_input)
            except ValueError:
                return float(default_value) if default_value else 0.0
        
        return user_input

    async def execute_tool(self, agent_key: str, tool_key: str):
        """Execute the selected tool with user inputs"""
        agent = self.agents[agent_key]
        tool = agent["tools"][tool_key]
        
        self.console.print(f"\n🎯 Executing: {tool['name']}", style="bold green")
        self.console.print(f"Agent: {agent['name']}", style="blue")
        
        # Collect parameters
        params = {}
        if tool["params"]:
            self.console.print("\n📝 Please provide the following parameters:")
            for param in tool["params"]:
                if param in ["time_spent", "estimated_time"]:
                    params[param] = self.get_user_input(param, "int")
                elif param in ["amount"]:
                    params[param] = self.get_user_input(param, "float")
                else:
                    params[param] = self.get_user_input(param)
        
        # Show execution spinner
        with self.console.status(f"[bold green]Executing {tool['name']}...", spinner="dots"):
            start_time = time.time()
            
            try:
                # Import and execute the appropriate tool
                result = await self._execute_tool_function(tool["func"], params)
                execution_time = time.time() - start_time
                
                # Display results
                self._display_results(tool["name"], result, execution_time)
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.console.print(f"\n❌ Error executing {tool['name']}: {str(e)}", style="bold red")
                self.console.print(f"⏱️ Execution Time: {execution_time:.2f}s", style="dim")

    async def _execute_tool_function(self, func_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual tool function"""
        
        # User Management Tools
        if func_name == "get_technicians":
            from src.tools.user.get_technicians import get_technicians
            return await get_technicians()
            
        elif func_name == "create_technician":
            from src.tools.user.create_technician import create_technician
            return await create_technician(
                first_name=params.get("first_name", "Demo"),
                last_name=params.get("last_name", "User")
            )
            
        elif func_name == "create_client":
            from src.tools.user.create_client import create_client
            import time as time_module
            unique_suffix = str(int(time_module.time()))[-6:]
            default_name = f"Demo Client Org {unique_suffix}"
            return await create_client(
                name=params.get("name", default_name),
                stage=params.get("stage", "Active"),
                status=params.get("status", "Paid"),
                account_manager_id=params.get("account_manager_id", "8275806997713629184")
            )
            
        elif func_name == "create_client_user":
            from src.tools.user.create_client_user import create_client_user
            return await create_client_user(
                first_name=params.get("first_name", "Demo"),
                last_name=params.get("last_name", "Client"),
                email=params.get("email"),
                client_account_id=params.get("client_account_id", "7206852887935602688")
            )
            
        elif func_name == "get_client_user":
            from src.tools.user.get_client_user import get_client_user
            return await get_client_user(user_id=params.get("user_id"))
            
        elif func_name == "get_requester_roles":
            from src.tools.user.get_requester_roles import get_requester_roles
            return await get_requester_roles()
        
        # Task Management Tools
        elif func_name == "create_task":
            from src.tools.task.create_task import create_task
            return await create_task(
                title=params.get("title"),
                description=params.get("description"),
                estimated_time=params.get("estimated_time", 60),
                status=params.get("status", "In Progress")
            )
            
        elif func_name == "create_ticket":
            from src.tools.ticket.create_ticket import create_ticket
            return await create_ticket(
                title=params.get("title"),
                description=params.get("description"),
                priority=params.get("priority", "High")
            )
            
        elif func_name == "update_ticket":
            from src.tools.ticket.update_ticket import update_ticket
            return await update_ticket(
                ticket_id=params.get("ticket_id"),
                status=params.get("status", "In Progress")
            )
            
        elif func_name == "create_ticket_note":
            from src.tools.ticket.create_ticket_note import create_ticket_note
            return await create_ticket_note(
                ticket_id=params.get("ticket_id"),
                content=params.get("content", "Investigation update and progress notes"),
                privacy_type=params.get("privacy_type", "PUBLIC")
            )
        
        # Workflow Tools
        elif func_name == "log_work":
            from src.tools.tracking.log_work import log_work
            return await log_work(
                ticket_id=params.get("ticket_id"),
                time_spent=params.get("time_spent", 60),
                description=params.get("description"),
                work_type=params.get("work_type", "Investigation")
            )
            
        elif func_name == "track_time":
            from src.tools.tracking.track_time import track_time
            return await track_time(
                ticket_id=params.get("ticket_id"),
                time_spent=params.get("time_spent", 30),
                description=params.get("description")
            )
        
        # Analytics Tools
        elif func_name == "performance_metrics":
            from src.tools.analytics.performance_metrics import performance_metrics
            return await performance_metrics()
            
        elif func_name == "view_analytics":
            from src.tools.analytics.view_analytics import view_analytics
            return await view_analytics(params.get("dashboard_type", "ticket_summary"))
            
        elif func_name == "create_alert":
            from src.tools.analytics.create_alert import create_alert
            return await create_alert(
                asset_id=params.get("asset_id"),
                message=params.get("message"),
                description=params.get("description"),
                severity=params.get("severity", "High")
            )
        
        # Knowledge Tools
        elif func_name == "create_article":
            from src.tools.knowledge.create_article import create_article
            return await create_article(
                title=params.get("title"),
                content=params.get("content"),
                category=params.get("category", "General")
            )
            
        elif func_name == "analyze_request":
            from src.tools.analysis.analyze_request import analyze_request
            return await analyze_request(
                request_text=params.get("request_text"),
                priority=params.get("priority", "Medium")
            )
            
        elif func_name == "generate_suggestions":
            from src.tools.analysis.generate_suggestions import generate_suggestions
            return await generate_suggestions(
                issue_description=params.get("issue_description"),
                category=params.get("category", "General")
            )
            
        elif func_name == "get_script_list_by_type":
            from src.tools.knowledge.get_script_list import get_script_list_by_type
            return await get_script_list_by_type(
                script_type=params.get("script_type", "WINDOWS"),
                page=params.get("page", 1),
                page_size=params.get("page_size", 10)
            )
        
        # Billing Tools
        elif func_name == "create_quote":
            from src.tools.billing.create_quote import create_quote
            return await create_quote(
                client_id=params.get("client_id"),
                description=params.get("description"),
                amount=params.get("amount", 1000.0)
            )
            
        elif func_name == "create_invoice":
            from src.tools.billing.create_invoice import create_invoice
            return await create_invoice(
                client_id=params.get("client_id"),
                description=params.get("description"),
                amount=params.get("amount", 500.0)
            )
            
        elif func_name == "get_payment_terms":
            from src.tools.billing.get_payment_terms import get_payment_terms
            return await get_payment_terms()
            
        elif func_name == "get_offered_items":
            from src.tools.billing.get_offered_items import get_offered_items
            return await get_offered_items(
                page=params.get("page", 1),
                page_size=params.get("page_size", 10)
            )
        
        else:
            raise ValueError(f"Unknown tool function: {func_name}")

    def _display_results(self, tool_name: str, result: Dict[str, Any], execution_time: float):
        """Display the execution results in a formatted way"""
        
        if result.get("success"):
            self.console.print(f"\n✅ {tool_name} - SUCCESS", style="bold green")
        else:
            self.console.print(f"\n❌ {tool_name} - FAILED", style="bold red")
        
        self.console.print(f"⏱️ Execution Time: {execution_time:.2f}s", style="dim")
        
        # Create results table
        table = Table(title="📋 Results", show_header=True, header_style="bold cyan")
        table.add_column("Field", style="yellow", width=20)
        table.add_column("Value", style="white", width=60)
        
        # Display key results
        for key, value in result.items():
            if key in ["success", "error"]:
                continue
            
            # Format different types of values
            if isinstance(value, list):
                display_value = f"List with {len(value)} items"
                if len(value) > 0 and isinstance(value[0], dict):
                    # Show first item details if it's a list of dicts
                    if "name" in value[0]:
                        display_value += f" (e.g., {value[0]['name']})"
                    elif "id" in value[0]:
                        display_value += f" (first ID: {value[0]['id']})"
            elif isinstance(value, dict):
                display_value = f"Object with {len(value)} fields"
                if "id" in value:
                    display_value += f" (ID: {value['id']})"
                elif "name" in value:
                    display_value += f" (Name: {value['name']})"
            else:
                display_value = str(value)
                # Truncate long strings
                if len(display_value) > 60:
                    display_value = display_value[:57] + "..."
            
            table.add_row(key.replace("_", " ").title(), display_value)
        
        if result.get("error"):
            table.add_row("Error", result["error"])
        
        self.console.print(table)
        self.console.print()

    async def run(self):
        """Main interactive loop"""
        self.display_header()
        
        while True:
            try:
                # Display agents menu
                self.display_agents_menu()
                
                # Get agent selection
                agent_choice = Prompt.ask("Select an agent (0 to exit)", choices=list(self.agents.keys()) + ["0"])
                
                if agent_choice == "0":
                    self.console.print("👋 Goodbye! Thanks for using SuperOps IT Technician Agent System!", style="bold blue")
                    break
                
                # Display tools menu for selected agent
                while True:
                    self.console.clear()
                    self.display_header()
                    self.display_tools_menu(agent_choice)
                    
                    # Get tool selection
                    tool_choices = list(self.agents[agent_choice]["tools"].keys()) + ["0"]
                    tool_choice = Prompt.ask("Select a tool (0 to go back)", choices=tool_choices)
                    
                    if tool_choice == "0":
                        break
                    
                    # Execute the selected tool
                    await self.execute_tool(agent_choice, tool_choice)
                    
                    # Ask if user wants to continue
                    if not Confirm.ask("\nWould you like to execute another tool?"):
                        break
                
                self.console.clear()
                
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Goodbye! Thanks for using SuperOps IT Technician Agent System!", style="bold blue")
                break
            except Exception as e:
                self.console.print(f"\n❌ An error occurred: {str(e)}", style="bold red")
                if not Confirm.ask("Would you like to continue?"):
                    break

def main():
    """Main entry point"""
    try:
        agent = InteractiveAgent()
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        console.print("\n\n👋 Goodbye! Thanks for using SuperOps IT Technician Agent System!", style="bold blue")
    except Exception as e:
        console.print(f"\n❌ Fatal error: {str(e)}", style="bold red")

if __name__ == "__main__":
    main()