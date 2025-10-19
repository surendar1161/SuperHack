#!/usr/bin/env python3
"""
Test script to get current valid ticket and technician IDs
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def get_current_ids():
    """Get current valid ticket and technician IDs"""
    
    # Configuration
    api_key = "api-eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI4Mjc1ODA2OTk3NzEzNjI5MTg0IiwicmFuZG9taXplciI6InHvv73vv73vv71FXHUwMDFGbu-_vXzvv70ifQ.hrvThcHoUKeQETGkYcVmfanhm5aFQ8KMwBZjgRvL_r9iiYkYT7Q7b29dYWOBVHizEdqS8kKlRuedDpq31MGS5uEQxspclFUVckZk4BetgUf4-v9mz-3mOQCGsAi5ATz1VBtScw08n3IT45uA071Klm0MLdVQ83AWM8Te0RX3KEBMDVfmUdII6ktQZhyNHH6rZ3dXhCdQSqO3kxGyY38r2BqFU_LTYqmIJVB3dg33HM5abvFuYog74j-k23GZPthjEE1_DN039T1yN2gHUkwqwWSxVFSVVIw2l8MBtUYOrCEgXLSM80zA_6ud4n8N2yq63DhnyL3EWmteGjvRAa4ePA"
    base_url = "https://api.superops.ai/msp"
    customer_subdomain = "hackathonsuperhack"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "CustomerSubDomain": customer_subdomain,
        "Cookie": "JSESSIONID=6F9D92167B22016E3CBF367CA6172882; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
    }
    
    print("🔍 Getting Current Valid IDs")
    print("=" * 50)
    
    # First, get recent tickets
    tickets_query = """
    query getTickets {
      tickets(first: 5) {
        edges {
          node {
            ticketId
            displayId
            title
            status
            createdAt
          }
        }
      }
    }
    """
    
    # Get technicians
    technicians_query = """
    query getTechnicians {
      technicians(first: 5) {
        edges {
          node {
            userId
            firstName
            lastName
            email
          }
        }
      }
    }
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Get tickets
            print("🎫 Getting recent tickets...")
            tickets_payload = {"query": tickets_query}
            
            async with session.post(base_url, headers=headers, json=tickets_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "errors" not in data and data.get("data", {}).get("tickets"):
                        tickets = data["data"]["tickets"]["edges"]
                        print(f"✅ Found {len(tickets)} tickets:")
                        for ticket in tickets:
                            node = ticket["node"]
                            print(f"   • ID: {node['ticketId']} | Display: {node['displayId']} | Title: {node['title']}")
                    else:
                        print("❌ No tickets found or error occurred")
                        print(f"Response: {await response.text()}")
                else:
                    print(f"❌ Failed to get tickets: {response.status}")
            
            print()
            
            # Get technicians
            print("👤 Getting technicians...")
            tech_payload = {"query": technicians_query}
            
            async with session.post(base_url, headers=headers, json=tech_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "errors" not in data and data.get("data", {}).get("technicians"):
                        technicians = data["data"]["technicians"]["edges"]
                        print(f"✅ Found {len(technicians)} technicians:")
                        for tech in technicians:
                            node = tech["node"]
                            print(f"   • ID: {node['userId']} | Name: {node['firstName']} {node['lastName']} | Email: {node['email']}")
                    else:
                        print("❌ No technicians found or error occurred")
                        print(f"Response: {await response.text()}")
                else:
                    print(f"❌ Failed to get technicians: {response.status}")
                    
    except Exception as e:
        print(f"❌ Request failed: {e}")

async def main():
    """Main function"""
    print(f"🕐 Starting ID lookup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await get_current_ids()

if __name__ == "__main__":
    asyncio.run(main())