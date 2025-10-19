#!/usr/bin/env python3
"""
Comprehensive Endpoint Test - Tests all tools with agent tracking
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class EndpointTestLogger:
    def __init__(self):
        self.test_results = []
        self.agent_tool_mapping = {}
        self.start_time = datetime.now()
    
    def log_test(self, agent_name: str, tool_name: str, status: str, 
                 response_data: Dict = None, error: str = None, 
                 execution_time: float = None):
        """Log test execution results"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "tool": tool_name,
            "status": status,
            "response_data": response_data,
            "error": error,
            "execution_time": execution_time
        }
        self.test_results.append(result)
        
        # Track agent-tool mapping
        if agent_name not in self.agent_tool_mapping:
            self.agent_tool_mapping[agent_name] = []
        self.agent_tool_mapping[agent_name].append({
            "tool": tool_name,
            "status": status,
            "response": response_data
        })
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "SUCCESS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        api_issues = len([r for r in self.test_results if r["status"] == "API_ISSUE"])
        
        report = f"""
# 📊 Comprehensive Endpoint Test Report

## 🎯 **Test Summary**
- **Total Tests**: {total_tests}
- **Successful**: {successful_tests} ✅
- **Failed**: {failed_tests} ❌
- **API Issues**: {api_issues} ⚠️
- **Success Rate**: {(successful_tests/total_tests*100):.1f}%
- **Test Duration**: {(datetime.now() - self.start_time).total_seconds():.2f}s

## 🤖 **Agent → Tool → API Response Matrix**

"""
        
        for agent_name, tools in self.agent_tool_mapping.items():
            report += f"\n### 🔧 **{agent_name}**\n\n"
            report += "| Tool | Status | API Response | Details |\n"
            report += "|------|--------|-------------|---------|\n"
            
            for tool_info in tools:
                status_icon = "✅" if tool_info["status"] == "SUCCESS" else "❌" if tool_info["status"] == "FAILED" else "⚠️"
                response_summary = \"Success\" if tool_info[\"status\"] == \"SUCCESS\" else tool_info.get(\"response\", {}).get(\"error\", \"Unknown\")[:50]
                
                report += f"| **{tool_info['tool']}** | {status_icon} {tool_info['status']} | {response_summary} | "
                
                if tool_info["response"]:
                    if tool_info["status"] == "SUCCESS":
                        if "user_id" in tool_info["response"]:
                            report += f"User ID: {tool_info['response']['user_id']} |\n"
                        elif "technician_id" in tool_info["response"]:
                            report += f"Tech ID: {tool_info['response']['technician_id']} |\n"
                        elif "ticket_id" in tool_info["response"]:
                            report += f"Ticket ID: {tool_info['response']['ticket_id']} |\n"
                        elif "task_id" in tool_info["response"]:
                            report += f"Task ID: {tool_info['response']['task_id']} |\n"
                        else:
                            report += "Success |\n"
                    else:
                        error_msg = tool_info['response'].get('error', 'Unknown') if isinstance(tool_info['response'], dict) else 'Unknown'
                        report += f"Error: {str(error_msg)[:30]}... |\n"
                else:
                    report += "No response data |\n"
        
        # Add detailed test results
        report += "\n\n## 📋 **Detailed Test Results**\n\n"
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌" if result["status"] == "FAILED" else "⚠️"
            report += f"\n### {status_icon} **{result['agent']} → {result['tool']}**\n"
            report += f"- **Status**: {result['status']}\n"
            report += f"- **Timestamp**: {result['timestamp']}\n"
            
            if result["execution_time"]:
                report += f"- **Execution Time**: {result['execution_time']:.2f}s\n"
            
            if result["response_data"]:
                report += f"- **Response**: {json.dumps(result['response_data'], indent=2)[:200]}...\n"
            
            if result["error"]:
                report += f"- **Error**: {result['error']}\n"
        
        return report

async def test_all_endpoints():
    \"\"\"Test all available endpoints with agent tracking\"\"\"
    logger = EndpointTestLogger()
    
    console.print(Panel.fit(
        "🧪 [bold blue]Comprehensive Endpoint Testing[/bold blue]\n" +
        "Testing all tools across multiple agents with API response tracking",
        border_style="blue"
    ))
    
    # Test categories with their respective agents
    test_categories = [
        {
            \"agent\": \"Task Management Agent\",
            \"tests\": [
                (\"create_task\", \"src.tools.task.create_task\"),
                (\"create_ticket\", \"src.tools.ticket.create_ticket\"),
                (\"update_ticket\", \"src.tools.ticket.update_ticket\"),
                (\"assign_ticket\", \"src.tools.ticket.assign_ticket\"),
            ]
        },
        {
            \"agent\": \"User Management Agent\", 
            \"tests\": [
                (\"get_technicians\", \"src.tools.user.get_technicians\"),
                (\"create_technician\", \"src.tools.user.create_technician\"),
                (\"create_client_user\", \"src.tools.user.create_client_user\"),
            ]
        },
        {
            \"agent\": \"Analytics Agent\",
            \"tests\": [
                (\"get_all_alerts\", \"src.tools.analytics.get_all_alerts\"),
                (\"performance_metrics\", \"src.tools.analytics.performance_metrics\"),
                (\"view_analytics\", \"src.tools.analytics.view_analytics\"),
            ]
        },
        {
            \"agent\": \"Workflow Agent\",
            \"tests\": [
                (\"log_work\", \"src.tools.tracking.log_work\"),
                (\"track_time\", \"src.tools.tracking.track_time\"),
                (\"monitor_progress\", \"src.tools.tracking.monitor_progress\"),
            ]
        },
        {
            \"agent\": \"Knowledge Agent\",
            \"tests\": [
                (\"create_article\", \"src.tools.knowledge.create_article\"),
                (\"analyze_request\", \"src.tools.analysis.analyze_request\"),
                (\"generate_suggestions\", \"src.tools.analysis.generate_suggestions\"),
            ]
        },
        {
            \"agent\": \"Billing Agent\",
            \"tests\": [
                (\"create_quote\", \"src.tools.billing.create_quote\"),
                (\"create_invoice\", \"src.tools.billing.create_invoice\"),
                (\"create_contract\", \"src.tools.billing.create_contract\"),
            ]
        }
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn(\"[progress.description]{task.description}\"),
        console=console,
    ) as progress:
        
        for category in test_categories:
            agent_name = category[\"agent\"]
            
            task = progress.add_task(f\"Testing {agent_name}...\", total=len(category[\"tests\"]))
            
            console.print(f"\n🤖 [bold cyan]{agent_name}[/bold cyan]")
            console.print("=" * 50)
            
            for tool_name, module_path in category[\"tests\"]:
                start_time = datetime.now()
                
                try:
                    console.print(f"🔧 Testing {tool_name}...")
                    
                    # Import the tool function
                    module_parts = module_path.split('.')
                    module = __import__(module_path, fromlist=[tool_name])
                    tool_func = getattr(module, tool_name)
                    
                    # Execute tool with appropriate test parameters
                    result = await execute_tool_test(tool_name, tool_func)
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    if result and result.get('success'):
                        console.print(f"   ✅ {tool_name} - SUCCESS")
                        logger.log_test(agent_name, tool_name, "SUCCESS", 
                                      result, execution_time=execution_time)
                    elif result:
                        console.print(f"   ⚠️ {tool_name} - API ISSUE: {result.get('error', 'Unknown')[:50]}...")
                        logger.log_test(agent_name, tool_name, "API_ISSUE", 
                                      result, execution_time=execution_time)
                    else:
                        console.print(f"   ❌ {tool_name} - NO RESPONSE")
                        logger.log_test(agent_name, tool_name, "FAILED", 
                                      error="No response from tool", execution_time=execution_time)
                        
                except Exception as e:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    console.print(f"   ❌ {tool_name} - ERROR: {str(e)[:50]}...")
                    logger.log_test(agent_name, tool_name, "FAILED", 
                                  error=str(e), execution_time=execution_time)
                
                progress.update(task, advance=1)
                await asyncio.sleep(0.1)  # Small delay between tests
    
    # Generate and save report
    report = logger.generate_report()
    
    # Save report to file
    with open("docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    console.print("\n" + "=" * 60)
    console.print(Panel.fit(
        f"📊 [bold green]Test Complete![/bold green]\n" +
        f"Total Tests: {len(logger.test_results)}\n" +
        f"Success Rate: {(len([r for r in logger.test_results if r['status'] == 'SUCCESS'])/len(logger.test_results)*100):.1f}%\n" +
        f"Report saved to: docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md",
        border_style="green"
    ))
    
    return logger

async def execute_tool_test(tool_name: str, tool_func) -> Dict[str, Any]:
    \"\"\"Execute individual tool test with appropriate parameters\"\"\"
    
    # Define test parameters for each tool
    test_params = {
        \"create_task\": {
            \"title\": \"Endpoint Test - Security Software Installation\",
            \"description\": \"Testing create_task endpoint functionality\",
            \"estimated_time\": 120,
            \"status\": \"In Progress\"
        },
        \"create_ticket\": {
            \"subject\": \"Endpoint Test - Network Infrastructure Issue\",
            \"description\": \"Testing create_ticket endpoint functionality\",
            \"priority\": \"Medium\",
            \"category\": \"Network\"
        },
        \"update_ticket\": {
            \"ticket_id\": \"12345\",
            \"status\": \"In Progress\",
            \"notes\": \"Testing update_ticket endpoint\"
        },
        \"assign_ticket\": {
            \"ticket_id\": \"12345\",
            \"technician_id\": \"7206852887935602688\",
            \"notes\": \"Testing assign_ticket endpoint\"
        },
        \"get_technicians\": {},
        \"create_technician\": {
            \"first_name\": \"Endpoint\",
            \"last_name\": \"Test\"
        },
        \"create_client_user\": {
            \"first_name\": \"Endpoint\",
            \"last_name\": \"TestClient\"
        },
        \"get_all_alerts\": {},
        \"performance_metrics\": {
            \"metric_type\": \"response_time\",
            \"time_period\": \"last_24h\"
        },
        \"view_analytics\": {
            \"report_type\": \"ticket_summary\",
            \"date_range\": \"last_week\"
        },
        \"log_work\": {
            \"ticket_id\": \"12345\",
            \"time_spent\": 120,
            \"description\": \"Testing log_work endpoint\",
            \"work_type\": \"Investigation\"
        },
        \"track_time\": {
            \"ticket_id\": \"12345\",
            \"minutes\": 60,
            \"description\": \"Testing track_time endpoint\"
        },
        \"monitor_progress\": {
            \"ticket_id\": \"12345\"
        },
        \"create_article\": {
            \"title\": \"Endpoint Test Article\",
            \"content\": \"Testing create_article endpoint functionality\",
            \"category\": \"Troubleshooting\"
        },
        \"analyze_request\": {
            \"request_text\": \"My computer is running slowly and I can't access the network\",
            \"priority\": \"Medium\"
        },
        \"generate_suggestions\": {
            \"issue_description\": \"Network connectivity problems\",
            \"category\": \"Network\"
        },
        \"create_quote\": {
            \"client_id\": \"7206852887935602688\",
            \"description\": \"Testing create_quote endpoint\",
            \"amount\": 1500.00
        },
        \"create_invoice\": {
            \"client_id\": \"7206852887935602688\",
            \"description\": \"Testing create_invoice endpoint\",
            \"amount\": 2000.00
        },
        \"create_contract\": {
            \"client_id\": \"7206852887935602688\",
            \"contract_type\": \"Service Agreement\",
            \"duration\": 12
        }
    }
    
    params = test_params.get(tool_name, {})
    
    try:
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**params)
        else:
            result = tool_func(**params)
        return result
    except Exception as e:
        return {\"success\": False, \"error\": str(e)}

if __name__ == \"__main__\":
    asyncio.run(test_all_endpoints())