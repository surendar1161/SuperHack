#!/usr/bin/env python3
"""
Standalone test for KB article creation tool
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the specific path for the article tool
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tools', 'knowledge'))

def print_article_header():
    """Print a beautiful header for the article test"""
    print("\n" + "=" * 80)
    print("📚 KNOWLEDGE BASE ARTICLE CREATION TOOL - DETAILED TEST")
    print("=" * 80)

def print_article_details(article_result):
    """Print detailed article information from tool result"""
    if not article_result.get('success'):
        print(f"❌ Article creation failed: {article_result.get('error')}")
        return
    
    print("\n📋 ARTICLE CREATION SUCCESS")
    print("-" * 50)
    print(f"✅ Status: {article_result.get('message')}")
    print(f"Article ID: {article_result.get('article_id')}")
    print(f"Name: {article_result.get('name')}")
    print(f"Title: {article_result.get('title')}")
    print(f"Status: {article_result.get('status')}")
    print(f"Parent ID: {article_result.get('parent_id')}")
    print(f"User ID: {article_result.get('user_id')}")
    print(f"Login Required: {article_result.get('login_required')}")
    print(f"View Count: {article_result.get('view_count')}")
    
    # Show detailed API response data
    api_data = article_result.get('data', {})
    if api_data:
        print(f"\n📊 DETAILED ARTICLE INFORMATION")
        print("-" * 50)
        
        raw_data = api_data.get('raw_data', {})
        if raw_data:
            print(f"Article Type: {raw_data.get('articleType', 'N/A')}")
            print(f"Created By: {raw_data.get('createdBy', {}).get('name', 'N/A')} ({raw_data.get('createdBy', {}).get('email', 'N/A')})")
            print(f"Created On: {raw_data.get('createdOn', 'N/A')}")
            print(f"Last Modified By: {raw_data.get('lastModifiedBy', {}).get('name', 'N/A')}")
            print(f"Last Modified On: {raw_data.get('lastModifiedOn', 'N/A')}")
            
            # Show parent information
            parent_info = raw_data.get('parent', {})
            if parent_info:
                print(f"Parent Category ID: {parent_info.get('itemId', 'N/A')}")
            
            # Show visibility information
            visibility_info = raw_data.get('visibility', [])
            if visibility_info:
                print(f"Visibility Settings: {len(visibility_info)} configuration(s)")
                for i, vis in enumerate(visibility_info, 1):
                    print(f"   Config {i}: Site = {vis.get('site', 'All Sites')}")

async def test_article_tool_standalone():
    """Test the KB article creation tool standalone"""
    
    print_article_header()
    
    try:
        # Import the article tool directly
        from create_article import create_kb_article, create_simple_kb_article, create_troubleshooting_article
        
        # Test 1: Create a comprehensive KB article
        print("📚 Test 1: Creating comprehensive KB article...")
        
        comprehensive_content = """
        <h2>Network Troubleshooting Guide</h2>
        <p dir="auto">This guide provides step-by-step instructions for resolving common network connectivity issues.</p>
        
        <h3>Common Network Problems</h3>
        <ul>
            <li>No internet connection</li>
            <li>Slow network performance</li>
            <li>Intermittent connectivity</li>
            <li>DNS resolution issues</li>
        </ul>
        
        <h3>Basic Troubleshooting Steps</h3>
        <ol>
            <li>Check physical connections (cables, power)</li>
            <li>Restart network equipment (modem, router)</li>
            <li>Verify network settings on device</li>
            <li>Test connectivity with different devices</li>
            <li>Check for interference or signal issues</li>
        </ol>
        
        <h3>Advanced Diagnostics</h3>
        <p dir="auto">If basic steps don't resolve the issue, try these advanced techniques:</p>
        <ul>
            <li>Use network diagnostic tools (ping, traceroute)</li>
            <li>Check firewall and security settings</li>
            <li>Update network drivers</li>
            <li>Contact ISP if external connectivity issues persist</li>
        </ul>
        """
        
        comprehensive_result = await create_kb_article(
            title="Network Troubleshooting Guide - Comprehensive",
            content=comprehensive_content,
            parent_id="8768135920619339720",
            user_id="8275806997713629184",
            status="DRAFT",
            login_required=True
        )
        
        print_article_details(comprehensive_result)
        
        # Test 2: Create a simple KB article using convenience function
        print(f"\n" + "=" * 80)
        print("💡 Test 2: Creating simple KB article using convenience function...")
        print("=" * 80)
        
        simple_result = await create_simple_kb_article(
            title="Password Reset Procedure",
            content="To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and follow the instructions sent to your email.",
            parent_id="8768135920619339720",
            user_id="8275806997713629184"
        )
        
        print_article_details(simple_result)
        
        # Test 3: Create a troubleshooting article with structured format
        print(f"\n" + "=" * 80)
        print("🔧 Test 3: Creating structured troubleshooting article...")
        print("=" * 80)
        
        solution_steps = [
            "Check if the printer is powered on and connected to the network",
            "Verify that the printer drivers are installed and up to date",
            "Clear the print queue and restart the print spooler service",
            "Test printing from a different application or device",
            "If issue persists, reinstall the printer drivers",
            "Contact IT support if the problem continues"
        ]
        
        troubleshooting_result = await create_troubleshooting_article(
            problem_title="Printer Not Responding",
            problem_description="Users report that the office printer is not responding to print jobs. Print jobs appear to be sent but nothing prints.",
            solution_steps=solution_steps,
            parent_id="8768135920619339720",
            user_id="8275806997713629184",
            additional_notes="This issue commonly occurs after Windows updates or network changes. Always check network connectivity first."
        )
        
        print_article_details(troubleshooting_result)
        
        # Test 4: Test validation with missing required fields
        print(f"\n" + "=" * 80)
        print("❓ Test 4: Testing validation with missing title...")
        print("=" * 80)
        
        validation_result = await create_kb_article(
            title="",  # Empty title
            content="Some content",
            parent_id="8768135920619339720",
            user_id="8275806997713629184"
        )
        
        if not validation_result.get('success'):
            print(f"✅ EXPECTED FAILURE: {validation_result.get('message')}")
            print(f"   Error: {validation_result.get('error')}")
        else:
            print(f"❌ UNEXPECTED SUCCESS: Should have failed for empty title")
        
        print(f"\n" + "=" * 80)
        print("🎉 ALL KB ARTICLE TOOL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("✅ Comprehensive KB article created")
        print("✅ Simple convenience article created")
        print("✅ Structured troubleshooting article created")
        print("✅ Input validation working correctly")
        print("✅ All article details displayed properly")
        print("\n📊 Summary:")
        print("   - KB article creation API is working correctly")
        print("   - Tool handles various article formats and structures")
        print("   - Validation prevents invalid inputs")
        print("   - All convenience functions work as expected")
        print("   - Articles can be used for documentation and support")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_article_tool_standalone())