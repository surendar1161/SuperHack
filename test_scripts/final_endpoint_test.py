#!/usr/bin/env python3
"""
Final Comprehensive Endpoint Test - Tests all tools with proper async handling
"""
import asyncio
import sys
import os
from datetime import datetime
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EndpointTestLogger:
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

async def test_all_endpoints():
    logger = EndpointTestLogger()
    
    print("🧪 Starting Comprehensive Endpoint Testing")
    print("=" * 60)
    
    # Test Task Management Agent
    print("\n🤖 Task Management Agent")
    print("-" * 40)
    
    # Test create_task
    print("🔧 Testing create_task...")
    try:
        from src.tools.task.create_task import create_task
        result = await create_task(
            title="Endpoint Test - Security Software Installation",
            description="Testing create_task endpoint functionality",
            estimated_time=120,
            status="In Progress"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS - Task ID: {result.get('task_id')}")
            logger.log("Task Management Agent", "create_task", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Task Management Agent", "create_task", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Task Management Agent", "create_task", "FAILED", error=str(e))
    
    # Test create_ticket
    print("🔧 Testing create_ticket...")
    try:
        from src.tools.ticket.create_ticket import create_ticket
        result = await create_ticket(
            subject="Endpoint Test - Network Infrastructure Issue",
            description="Testing create_ticket endpoint functionality",
            priority="Medium"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS - Ticket ID: {result.get('ticket_id')}")
            logger.log("Task Management Agent", "create_ticket", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Task Management Agent", "create_ticket", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Task Management Agent", "create_ticket", "FAILED", error=str(e))
    
    # Test update_ticket
    print("🔧 Testing update_ticket...")
    try:
        from src.tools.ticket.update_ticket import update_ticket
        result = await update_ticket(
            ticket_id="12345",
            status="In Progress",
            notes="Testing update_ticket endpoint"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS")
            logger.log("Task Management Agent", "update_ticket", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Task Management Agent", "update_ticket", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Task Management Agent", "update_ticket", "FAILED", error=str(e))
    
    # Test User Management Agent
    print("\n🤖 User Management Agent")
    print("-" * 40)
    
    # Test get_technicians
    print("🔧 Testing get_technicians...")
    try:
        from src.tools.user.get_technicians import get_technicians
        result = await get_technicians()
        if result and result.get('success'):
            print(f"   ✅ SUCCESS - Found {len(result.get('technicians', []))} technicians")
            logger.log("User Management Agent", "get_technicians", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("User Management Agent", "get_technicians", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("User Management Agent", "get_technicians", "FAILED", error=str(e))
    
    # Test create_technician
    print("🔧 Testing create_technician...")
    try:
        from src.tools.user.create_technician import create_technician
        result = await create_technician(
            first_name="Endpoint",
            last_name="Test"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS - Tech ID: {result.get('technician_id')}")
            print(f"       Email: {result.get('email')}")
            logger.log("User Management Agent", "create_technician", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("User Management Agent", "create_technician", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("User Management Agent", "create_technician", "FAILED", error=str(e))
    
    # Test create_client_user
    print("🔧 Testing create_client_user...")
    try:
        from src.tools.user.create_client_user import create_client_user
        result = await create_client_user(
            first_name="Endpoint",
            last_name="TestClient"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS - User ID: {result.get('user_id')}")
            print(f"       Email: {result.get('email')}")
            logger.log("User Management Agent", "create_client_user", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("User Management Agent", "create_client_user", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("User Management Agent", "create_client_user", "FAILED", error=str(e))
    
    # Test Analytics Agent
    print("\n🤖 Analytics Agent")
    print("-" * 40)
    
    # Test performance_metrics
    print("🔧 Testing performance_metrics...")
    try:
        from src.tools.analytics.performance_metrics import performance_metrics
        result = await performance_metrics()
        if result and result.get('success'):
            print(f"   ✅ SUCCESS")
            logger.log("Analytics Agent", "performance_metrics", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Analytics Agent", "performance_metrics", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Analytics Agent", "performance_metrics", "FAILED", error=str(e))
    
    # Test view_analytics
    print("🔧 Testing view_analytics...")
    try:
        from src.tools.analytics.view_analytics import view_analytics
        result = await view_analytics()
        if result and result.get('success'):
            print(f"   ✅ SUCCESS")
            logger.log("Analytics Agent", "view_analytics", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Analytics Agent", "view_analytics", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Analytics Agent", "view_analytics", "FAILED", error=str(e))
    
    # Test Workflow Agent
    print("\n🤖 Workflow Agent")
    print("-" * 40)
    
    # Test log_work
    print("🔧 Testing log_work...")
    try:
        from src.tools.tracking.log_work import log_work
        result = await log_work(
            ticket_id="12345",
            time_spent=120,
            description="Testing log_work endpoint",
            work_type="Investigation"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS")
            logger.log("Workflow Agent", "log_work", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Workflow Agent", "log_work", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Workflow Agent", "log_work", "FAILED", error=str(e))
    
    # Test track_time
    print("🔧 Testing track_time...")
    try:
        from src.tools.tracking.track_time import track_time
        result = await track_time(
            ticket_id="12345",
            time_spent=60,
            description="Testing track_time endpoint"
        )
        if result and result.get('success'):
            print(f"   ✅ SUCCESS")
            logger.log("Workflow Agent", "track_time", "SUCCESS", result)
        else:
            print(f"   ⚠️ API ISSUE: {result.get('error', 'Unknown')[:50]}...")
            logger.log("Workflow Agent", "track_time", "API_ISSUE", result)
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:50]}...")
        logger.log("Workflow Agent", "track_time", "FAILED", error=str(e))
    
    # Generate report
    successful = len([r for r in logger.results if r["status"] == "SUCCESS"])
    total = len(logger.results)
    
    report = f"""# 📊 Comprehensive Endpoint Test Report

## 🎯 Test Summary
- **Total Tests**: {total}
- **Successful**: {successful} ✅
- **Failed**: {len([r for r in logger.results if r["status"] == "FAILED"])} ❌
- **API Issues**: {len([r for r in logger.results if r["status"] == "API_ISSUE"])} ⚠️
- **Success Rate**: {(successful/total*100):.1f}%
- **Test Duration**: {(datetime.now() - logger.start_time).total_seconds():.2f}s

## 🤖 Agent → Tool → API Response Matrix

### 🔧 Task Management Agent

| Tool | Status | API Response | Details |
|------|--------|-------------|---------|"""
    
    # Add results for each agent
    agents = {}
    for result in logger.results:
        agent = result["agent"]
        if agent not in agents:
            agents[agent] = []
        agents[agent].append(result)
    
    for agent_name, tools in agents.items():
        if agent_name != "Task Management Agent":
            report += f"\n\n### 🔧 {agent_name}\n\n"
            report += "| Tool | Status | API Response | Details |\n"
            report += "|------|--------|-------------|---------|\n"
        
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
                error_msg = tool.get("error", "Unknown error")
                if isinstance(error_msg, str):
                    details = error_msg[:50] + "..." if len(error_msg) > 50 else error_msg
                else:
                    details = "API Issue"
            
            report += f"| **{tool['tool']}** | {status_icon} {tool['status']} | {tool['status']} | {details} |\n"
    
    report += f"""

## 📋 Detailed Test Results

"""
    
    for result in logger.results:
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌" if result["status"] == "FAILED" else "⚠️"
        report += f"\n### {status_icon} {result['agent']} → {result['tool']}\n"
        report += f"- **Status**: {result['status']}\n"
        report += f"- **Timestamp**: {result['timestamp']}\n"
        
        if result["response"]:
            response_str = json.dumps(result['response'], indent=2)
            if len(response_str) > 300:
                response_str = response_str[:300] + "..."
            report += f"- **Response**: ```json\n{response_str}\n```\n"
        
        if result["error"]:
            report += f"- **Error**: {result['error']}\n"
    
    report += f"""

## 🎉 Summary

The SuperOps IT Technician Agent system has been comprehensively tested across all major functional areas:

- **Task Management**: Ticket and task creation/management
- **User Management**: Technician and client user operations  
- **Analytics**: Performance monitoring and reporting
- **Workflow**: Time tracking and work logging

**Overall System Status**: {"✅ OPERATIONAL" if successful > total/2 else "⚠️ NEEDS ATTENTION"}

---

**Last Updated**: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}  
**Test Environment**: SuperOps API Integration  
**Agent Framework**: Multi-Agent Architecture
"""
    
    # Save report
    with open("docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("📊 Test Complete!")
    print(f"Total Tests: {total}")
    print(f"Success Rate: {(successful/total*100):.1f}%")
    print("Report saved to: docs/COMPREHENSIVE_ENDPOINT_TEST_REPORT.md")
    
    return logger

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())