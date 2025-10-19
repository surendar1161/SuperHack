"""Main entry point for the SuperOps IT Technician Agent - Strands Implementation"""

import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
import typer

# Use the new Strands-based implementation
from .agents.it_technician_strands_controller import create_it_technician_controller
from .agents.config import AgentConfig
from .utils.logger import setup_logger, get_logger

# Load environment variables
load_dotenv()

console = Console()
app = typer.Typer(
    name="SuperOps IT Technician Agent",
    help="AI-powered IT Technician Agent with Strands multi-agent architecture",
    no_args_is_help=True
)

# Global controller instance
controller = None

async def initialize_controller():
    """Initialize the Strands-based IT Technical Agent controller"""
    global controller

    try:
        # Create configuration with supported parameters only
        config = AgentConfig()

        # Initialize the Strands controller
        console.print("[bold blue]🔧 Initializing Strands multi-agent system...[/bold blue]")
        controller = await create_it_technician_controller(config)

        console.print("[bold green]✅ IT Technical Agent Controller initialized successfully![/bold green]")
        return controller

    except Exception as e:
        console.print(f"[bold red]❌ Failed to initialize controller: {e}[/bold red]")
        raise

async def main_async():
    """Async main function to run the IT Technician Agent"""
    logger = get_logger("main")

    try:
        # Initialize the Strands controller
        controller = await initialize_controller()

        console.print("[bold green]🚀 SuperOps IT Technician Agent started successfully![/bold green]")
        console.print("[dim]Using Strands multi-agent graph architecture[/dim]")

        # Display system status
        metrics = controller.get_system_metrics()
        console.print(f"[bold cyan]📊 System Status:[/bold cyan]")
        console.print(f"  • Main Graph: {metrics['main_graph_status']}")
        console.print(f"  • SLA Graph: {metrics['sla_graph_status']}")
        console.print(f"  • Total Agents: {metrics['total_agents']}")

        # Example: Handle a test support request
        test_request = {
            'id': 'test_001',
            'title': 'User cannot access email',
            'description': 'User reports unable to connect to email server',
            'priority': 'medium',
            'category': 'incident',
            'reporter': {'name': 'John Doe', 'email': 'john@company.com'}
        }

        console.print("\n[bold blue]📋 Processing test support request...[/bold blue]")
        result = await controller.handle_support_request(test_request)

        console.print(f"[bold green]✅ Request processed: {result['status']}[/bold green]")
        console.print(f"[dim]Execution time: {result.get('execution_time', 0):.2f}s[/dim]")

        # Keep running and wait for interruption
        console.print("\n[bold yellow]🔄 Agent running... Press Ctrl+C to stop[/bold yellow]")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]🛑 Shutting down gracefully...[/bold yellow]")

    except Exception as e:
        logger.error(f"Failed to run agent: {e}")
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        raise

def main():
    """Main function to run the IT Technician Agent"""
    setup_logger()
    asyncio.run(main_async())

@app.command()
def start():
    """Start the IT Technician Agent with Strands architecture"""
    console.print("[bold blue]🤖 Starting SuperOps IT Technician Agent (Strands)...[/bold blue]")
    main()

@app.command()
def health_check():
    """Perform a health check on the Strands system"""
    console.print("[bold blue]🔍 Performing Strands system health check...[/bold blue]")

    async def check_health():
        try:
            controller = await initialize_controller()
            metrics = controller.get_system_metrics()

            console.print("[bold green]✅ Health Check Results:[/bold green]")
            console.print(f"  • System Status: {metrics['system_status']}")
            console.print(f"  • Main Graph: {metrics['main_graph_status']}")
            console.print(f"  • SLA Graph: {metrics['sla_graph_status']}")
            console.print(f"  • Success Rate: {metrics['execution_metrics']['success_rate_percent']}%")
            console.print(f"  • Total Requests: {metrics['execution_metrics']['total_requests']}")

            return True

        except Exception as e:
            console.print(f"[bold red]❌ Health check failed: {e}[/bold red]")
            return False

    success = asyncio.run(check_health())
    if not success:
        raise typer.Exit(1)

@app.command()
def test_request(
    title: str = typer.Option("Test issue", help="Request title"),
    priority: str = typer.Option("medium", help="Request priority"),
    description: str = typer.Option("Test support request", help="Request description")
):
    """Test the agent with a sample support request"""
    console.print("[bold blue]🧪 Testing support request processing...[/bold blue]")

    async def test_support_request():
        try:
            controller = await initialize_controller()

            test_request = {
                'id': f'test_{int(asyncio.get_event_loop().time())}',
                'title': title,
                'description': description,
                'priority': priority,
                'category': 'test',
                'reporter': {'name': 'Test User', 'email': 'test@company.com'}
            }

            console.print(f"[bold cyan]📋 Processing: {title}[/bold cyan]")
            result = await controller.handle_support_request(test_request)

            console.print(f"[bold green]✅ Result: {result['status']}[/bold green]")
            console.print(f"  • Execution time: {result.get('execution_time', 0):.2f}s")
            console.print(f"  • Request ID: {result.get('request_id')}")

            if result.get('sla_result'):
                console.print(f"  • SLA handled: Yes")

            return result['status'] == 'success'

        except Exception as e:
            console.print(f"[bold red]❌ Test failed: {e}[/bold red]")
            return False

    success = asyncio.run(test_support_request())
    if not success:
        raise typer.Exit(1)

@app.command()
def metrics():
    """Display system performance metrics"""
    console.print("[bold blue]📊 Retrieving system metrics...[/bold blue]")

    async def show_metrics():
        try:
            controller = await initialize_controller()
            metrics = controller.get_system_metrics()

            console.print("[bold green]📈 System Metrics:[/bold green]")
            console.print(f"\n[bold cyan]🔧 System Status:[/bold cyan]")
            console.print(f"  • Status: {metrics['system_status']}")
            console.print(f"  • Main Graph: {metrics['main_graph_status']}")
            console.print(f"  • SLA Graph: {metrics['sla_graph_status']}")

            console.print(f"\n[bold cyan]📋 Execution Metrics:[/bold cyan]")
            exec_metrics = metrics['execution_metrics']
            console.print(f"  • Total Requests: {exec_metrics['total_requests']}")
            console.print(f"  • Successful: {exec_metrics['successful_requests']}")
            console.print(f"  • Failed: {exec_metrics['failed_requests']}")
            console.print(f"  • Success Rate: {exec_metrics['success_rate_percent']}%")
            console.print(f"  • SLA Breaches Handled: {exec_metrics['sla_breaches_handled']}")

            console.print(f"\n[bold cyan]⚡ Performance Metrics:[/bold cyan]")
            perf_metrics = metrics['performance_metrics']
            console.print(f"  • Avg Execution Time: {perf_metrics['average_execution_time_seconds']}s")
            console.print(f"  • Recent Executions: {perf_metrics['recent_executions_count']}")

            console.print(f"\n[bold cyan]🤖 Agent Counts:[/bold cyan]")
            agent_counts = metrics['agent_counts']
            console.print(f"  • Main Agents: {agent_counts['main_agents']}")
            console.print(f"  • Subagents: {agent_counts['subagents']}")
            console.print(f"  • Active Workflows: {agent_counts['active_workflows']}")

            return True

        except Exception as e:
            console.print(f"[bold red]❌ Failed to retrieve metrics: {e}[/bold red]")
            return False

    success = asyncio.run(show_metrics())
    if not success:
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
