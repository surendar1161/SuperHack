#!/usr/bin/env python3
"""
Simple Comprehensive Endpoint Test - Tests all tools with agent tracking
"""
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleTestLogger:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def log(self, agent, tool, status, response=None, error=None):
        self.results.append({
            "agent": agent,
            "tool": tool, 
            "status": status,
            "response": response,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_report(self):
        successful = len([r for r in self.results if r["status"] == "SUCCESS"])
        total = len(self.results)
        
        report = f"""# 📊 Comprehensive Endpoint Test Report

## Test Summary
- Total Tests: {total}
- Successful: {successful}
- Success Rate: {(successful/total*100):.1f}%
- Duration: {(datetime.now() - self.start_time).total_seconds():.2f}s

## Agent → Tool → API Response Matrix

"""
        
        # Group by agent
        agents = {}
        for result in self.results:
            agent = result["agent"]
            if agent not in agents:
                agents[agent] = []
            agents[agent].append(result)
        
        for agent_name, tools in agents.items():
            report += f"\n### {agent_name}\n\n"
            report += "| Tool | Status | Response | Details |\n"
            report += "|------|--------|----------|----------|\n"
            
            for tool in tools:
                status_icon = "✅" if tool["status"] == "SUCCESS" else "❌" if tool["status"] == "FAILED" else "⚠️"
                
                if tool["response"] and tool["status"] == "SUCCESS":
                    if "user_id" in tool["response"]:
                        details = f"User ID: {tool['response']['user_id']}"
                    elif "technician_id" in tool["response"]:
                        details = f"Tech ID: {tool['response']['technician_id']}"
                    elif "ticket_id" in tool["response"]:
                        details = f"Ticket ID: {tool['response']['ticket_id']}"
                    elif "task_id" in tool["response"]:
                        details = f"Task ID: {tool['response']['task_id']}"
                    else:
                        details = "Success"
                else:
                    details = tool.get("error", "Unknown error")[:50] if tool["status"] == "FAILED" else "API Issue"
                
                report += f"| {tool['tool']} | {status_icon} {tool['status']} | {tool['status']} | {details} |\n"
        
        report += "\n## Detailed Results\n\n"
        for result in self.results:
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌" if result["status"] == "FAILED" else "⚠️"
            report += f"\n### {status_icon} {result['agent']} → {result['tool']}\n"
            report += f"- Status: {result['status']}\n"
            if result["response"]:
                report += f"- Response: {json.dumps(result['response'], indent=2)[:200]}...\n"
            if result["error"]:
                report += f"- Error: {result['error']}\n"
        
        return report

async def test_all_endpoints():
    logger = SimpleTestLogger()
    
    print("🧪 Starting Comprehensive Endpoint Testing")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        {
            "agent": "Task Management Agent",
            "tests": [
                ("create_task", "src.tools.task.create_task"),
                ("create_ticket", "src.tools.ticket.create_ticket"),
                ("update_ticket", "src.tools.ticket.update_ticket"),
            ]
        },
        {
            "agent": "User Management Agent", 
            "tests": [
                ("get_technicians", "src.tools.user.get_technicians"),
                ("create_technician", "src.tools.user.create_technician"),
                ("create_client_user", "src.tools.user.create_client_user"),
            ]
        },
        {
            "agent": "Analytics Agent",
            "tests": [
                ("performance_metrics", "src.tools.analytics.performance_metrics"),
                ("view_analytics", "src.tools.analytics.view_analytics"),
            ]
        },
        {
            "agent": "Workflow Agent",
            "tests": [
                ("log_work", "src.tools.tracking.log_work"),
                ("track_time", "src.tools.tracking.track_time"),
            ]
        }
    ]
    
    for category in test_categories:
        agent_name = category["agent"]
        print(f"\n🤖 {agent_name}")
        print("-" * 40)
        
        for tool_name, module_path in category["tests"]:
            print(f"🔧 Testing {tool_name}...")
            
            try:
                # Import and execute tool
                module = __import__(module_path, fromlist=[tool_name])
                tool_func = getattr(module, tool_name)
                
                # Get test parameters
                params = get_test_params(tool_name)
                
                # Execute tool
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**params)
                else:
                    result = tool_func(**params)
                
                if result and result.get('success'):
                    print(f"   ✅ SUCCESS")
                    logger.log(agent_name, tool_name, "SUCCESS", result)
                elif result:
                    print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
                    logger.log(agent_name, tool_name, "API_ISSUE", result)
                else:
                    print(f"   ❌ NO RESPONSE")
                    logger.log(agent_name, tool_name, "FAILED", error="No response")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)[:50]}...")
                logger.log(agent_name, tool_name, "FAILED", error=str(e))
            
            await asyncio.sleep(0.1)
    
    # Generate report
    report = logger.generate_report()
    
    # Save report
    with open("docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("📊 Test Complete!")
    print(f"Total Tests: {len(logger.results)}")
    successful = len([r for r in logger.results if r["status"] == "SUCCESS"])
    print(f"Success Rate: {(successful/len(logger.results)*100):.1f}%")
    print("Report saved to: docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md")
    
    return logger

def get_test_params(tool_name):
    """Get test parameters for each tool"""
    params = {
        "create_task": {
            "title": "Endpoint Test - Security Software Installation",
            "description": "Testing create_task endpoint functionality",
            "estimated_time": 120,
            "status": "In Progress"
        },
        "create_ticket": {
            "subject": "Endpoint Test - Network Infrastructure Issue",
            "description": "Testing create_ticket endpoint functionality",
            "priority": "Medium",
            "category": "Network"
        },
        "update_ticket": {
            "ticket_id": "12345",
            "status": "In Progress",
            "notes": "Testing update_ticket endpoint"
        },
        "get_technicians": {},
        "create_technician": {
            "first_name": "Endpoint",
            "last_name": "Test"
        },
        "create_client_user": {
            "first_name": "Endpoint",
            "last_name": "TestClient"
        },
        "performance_metrics": {
            "metric_type": "response_time",
            "time_period": "last_24h"
        },
        "view_analytics": {
            "report_type": "ticket_summary",
            "date_range": "last_week"
        },
        "log_work": {
            "ticket_id": "12345",
            "time_spent": 120,
            "description": "Testing log_work endpoint",
            "work_type": "Investigation"
        },
        "track_time": {
            "ticket_id": "12345",
            "minutes": 60,
            "description": "Testing track_time endpoint"
        }
    }
    
    return params.get(tool_name, {})

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())