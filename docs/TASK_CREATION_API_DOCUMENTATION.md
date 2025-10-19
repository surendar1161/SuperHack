# SuperOps Task Creation API Documentation

## 📋 Overview

This document provides comprehensive information about creating tasks in SuperOps using their GraphQL API, including working examples, test data, and troubleshooting information.

## 🔗 API Endpoints

### Working Endpoint
- **URL**: `https://api.superops.ai/msp`
- **Method**: POST (GraphQL)
- **Content-Type**: `application/json`

### Failed Endpoint (Do Not Use)
- **URL**: `https://api.superops.ai/it` ❌
- **Issue**: Returns "Internal Server Error(s) while executing query"

## 🔐 Authentication

### Required Headers
```json
{
  "Authorization": "Bearer {API_KEY}",
  "Content-Type": "application/json",
  "CustomerSubDomain": "hackathonsuperhack",
  "Cookie": "JSESSIONID={SESSION_ID}; ingress_cookie={INGRESS_COOKIE}"
}
```

### Working Authentication Values
```bash
API_KEY="api-eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI4Mjc1ODA2OTk3NzEzNjI5MTg0IiwicmFuZG9taXplciI6InHvv73vv73vv71FXHUwMDFGbu-_vXzvv70ifQ.hrvThcHoUKeQETGkYcVmfanhm5aFQ8KMwBZjgRvL_r9iiYkYT7Q7b29dYWOBVHizEdqS8kKlRuedDpq31MGS5uEQxspclFUVckZk4BetgUf4-v9mz-3mOQCGsAi5ATz1VBtScw08n3IT45uA071Klm0MLdVQ83AWM8Te0RX3KEBMDVfmUdII6ktQZhyNHH6rZ3dXhCdQSqO3kxGyY38r2BqFU_LTYqmIJVB3dg33HM5abvFuYog74j-k23GZPthjEE1_DN039T1yN2gHUkwqwWSxVFSVVIw2l8MBtUYOrCEgXLSM80zA_6ud4n8N2yq63DhnyL3EWmteGjvRAa4ePA"
CUSTOMER_SUBDOMAIN="hackathonsuperhack"
SESSION_ID="6F9D92167B22016E3CBF367CA6172882"
INGRESS_COOKIE="1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed"
```

## 📝 GraphQL Mutation

### Complete Mutation Schema
```graphql
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
```

## 🧪 Test Data Examples

### Example 1: Software Installation Task
```json
{
  "input": {
    "title": "Install Microsoft Office Suite",
    "description": "Install and configure Microsoft Office 365 on user workstation",
    "status": "Open",
    "estimatedTime": 180,
    "scheduledStartDate": "2024-12-01T09:00:00",
    "dueDate": "2024-12-01T17:00:00",
    "technician": {
      "userId": 8275806997713629000
    },
    "module": "TICKET",
    "ticket": {
      "ticketId": 8951254566344270000
    }
  }
}
```

### Example 2: Hardware Maintenance Task
```json
{
  "input": {
    "title": "Replace Server Hard Drive",
    "description": "Replace failing hard drive in production server and restore from backup",
    "status": "In Progress",
    "estimatedTime": 240,
    "scheduledStartDate": "2024-12-02T08:00:00",
    "dueDate": "2024-12-02T16:00:00",
    "technician": {
      "userId": 8275806997713629000
    },
    "module": "TICKET",
    "ticket": {
      "ticketId": 8951254566344270000
    }
  }
}
```

### Example 3: Network Configuration Task
```json
{
  "input": {
    "title": "Configure VPN Access for Remote User",
    "description": "Set up secure VPN connection for new remote employee including client configuration",
    "status": "Open",
    "estimatedTime": 90,
    "scheduledStartDate": "2024-12-03T10:00:00",
    "dueDate": "2024-12-03T14:00:00",
    "technician": {
      "userId": 8275806997713629000
    },
    "module": "TICKET",
    "ticket": {
      "ticketId": 8951254566344270000
    }
  }
}
```

### Example 4: Security Update Task
```json
{
  "input": {
    "title": "Apply Critical Security Patches",
    "description": "Install latest security updates on all Windows workstations in accounting department",
    "status": "Open",
    "estimatedTime": 300,
    "scheduledStartDate": "2024-12-04T18:00:00",
    "dueDate": "2024-12-05T06:00:00",
    "technician": {
      "userId": 8275806997713629000
    },
    "module": "TICKET",
    "ticket": {
      "ticketId": 8951254566344270000
    }
  }
}
```

### Example 5: User Training Task
```json
{
  "input": {
    "title": "Conduct New Employee IT Orientation",
    "description": "Provide comprehensive IT orientation for new hire including system access and security training",
    "status": "Open",
    "estimatedTime": 120,
    "scheduledStartDate": "2024-12-05T13:00:00",
    "dueDate": "2024-12-05T15:00:00",
    "technician": {
      "userId": 8275806997713629000
    },
    "module": "TICKET",
    "ticket": {
      "ticketId": 8951254566344270000
    }
  }
}
```

## 📊 Field Specifications

### Required Fields
- `title` (string): Task title/summary
- `status` (string): Task status - Options: "Open", "In Progress", "Completed", "Cancelled"

### Optional Fields
- `description` (string): Detailed task description
- `estimatedTime` (integer): Estimated time in minutes
- `scheduledStartDate` (ISO 8601 string): When task should start
- `dueDate` (ISO 8601 string): When task should be completed
- `technician.userId` (integer): Assigned technician ID
- `module` (string): Module type - typically "TICKET"
- `ticket.ticketId` (integer): Associated ticket ID

### Status Options
- `"Open"`: Task created but not started
- `"In Progress"`: Task currently being worked on
- `"Completed"`: Task finished successfully
- `"Cancelled"`: Task cancelled/abandoned

## 🔧 Working cURL Example

```bash
curl --location 'https://api.superops.ai/msp' \
--header 'CustomerSubDomain: hackathonsuperhack' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer api-eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiI4Mjc1ODA2OTk3NzEzNjI5MTg0IiwicmFuZG9taXplciI6InHvv73vv73vv71FXHUwMDFGbu-_vXzvv70ifQ.hrvThcHoUKeQETGkYcVmfanhm5aFQ8KMwBZjgRvL_r9iiYkYT7Q7b29dYWOBVHizEdqS8kKlRuedDpq31MGS5uEQxspclFUVckZk4BetgUf4-v9mz-3mOQCGsAi5ATz1VBtScw08n3IT45uA071Klm0MLdVQ83AWM8Te0RX3KEBMDVfmUdII6ktQZhyNHH6rZ3dXhCdQSqO3kxGyY38r2BqFU_LTYqmIJVB3dg33HM5abvFuYog74j-k23GZPthjEE1_DN039T1yN2gHUkwqwWSxVFSVVIw2l8MBtUYOrCEgXLSM80zA_6ud4n8N2yq63DhnyL3EWmteGjvRAa4ePA' \
--header 'Cookie: JSESSIONID=6F9D92167B22016E3CBF367CA6172882; ingress_cookie=1760247754.189.36.304549|d873aaecd3f140ed08e66d6c109ebbed' \
--data '{
  "query": "mutation createTask($input: CreateTaskInput!) {\n  createTask(input: $input) {\n    taskId\n    displayId\n    title\n    description\n    status\n    estimatedTime\n    scheduledStartDate\n    dueDate\n    overdue\n    actualStartDate\n    actualEndDate\n    technician\n    techGroup\n    module\n    ticket\n    workItem \n  }\n}",
  "variables": {
    "input": {
      "title": "Install Microsoft Office Suite",
      "description": "Install and configure Microsoft Office 365 on user workstation",
      "status": "Open",
      "estimatedTime": 180,
      "scheduledStartDate": "2024-12-01T09:00:00",
      "dueDate": "2024-12-01T17:00:00",
      "technician": {
        "userId": 8275806997713629000
      },
      "module": "TICKET",
      "ticket": {
        "ticketId": 8951254566344270000
      }
    }
  }
}'
```

## ⚠️ Known Issues

### Issue 1: Internal Server Error
**Problem**: Even with correct format, API returns:
```json
{
  "errors": [
    {
      "message": "Internal Server Error(s) while executing query"
    }
  ],
  "data": {
    "createTask": null
  }
}
```

**Possible Causes**:
1. Invalid ticket ID or technician ID
2. Server-side validation issues
3. Database constraints not met
4. API endpoint issues

### Issue 2: ID Validation
**Problem**: Hard to determine valid ticket/technician IDs
**Solution**: Query existing tickets and technicians first

## 🧪 Testing Strategy

### Step 1: Validate Authentication
Test basic connectivity with a simple query

### Step 2: Get Valid IDs
Query for existing tickets and technicians to get valid IDs

### Step 3: Test Minimal Task Creation
Start with minimal required fields only

### Step 4: Add Optional Fields
Gradually add optional fields to identify issues

## 📈 Success Response Format

```json
{
  "data": {
    "createTask": {
      "taskId": "1234567890123456789",
      "displayId": "TSK-001",
      "title": "Install Microsoft Office Suite",
      "description": "Install and configure Microsoft Office 365 on user workstation",
      "status": "Open",
      "estimatedTime": 180,
      "scheduledStartDate": "2024-12-01T09:00:00",
      "dueDate": "2024-12-01T17:00:00",
      "overdue": false,
      "actualStartDate": null,
      "actualEndDate": null,
      "technician": {
        "userId": 8275806997713629000,
        "firstName": "John",
        "lastName": "Doe"
      },
      "techGroup": null,
      "module": "TICKET",
      "ticket": {
        "ticketId": 8951254566344270000
      },
      "workItem": null
    }
  }
}
```

## 🔍 Troubleshooting Checklist

- [ ] Verify API endpoint is `https://api.superops.ai/msp`
- [ ] Check authentication headers are complete
- [ ] Validate ticket ID exists and is accessible
- [ ] Validate technician ID exists and is active
- [ ] Ensure date formats are ISO 8601 compliant
- [ ] Check status value is from allowed list
- [ ] Verify estimatedTime is positive integer
- [ ] Test with minimal required fields first

## 📚 Related Documentation

- [SuperOps API Documentation](https://api.superops.ai/docs)
- [GraphQL Specification](https://graphql.org/learn/)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)

---

**Last Updated**: October 17, 2024  
**Status**: Under Investigation - Internal Server Errors Occurring