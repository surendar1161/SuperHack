"""GraphQL mutations for SuperOps API"""

# Ticket Mutations based on WORKING SuperOps API format
# Reference: Working curl command from user
CREATE_TICKET_MUTATION = """
mutation createTicket($input: CreateTicketInput!) {
    createTicket(input: $input) {
        ticketId
        status
        subject
        requester
        technician
        site
        requestType
        source
        department
    }
}
"""

# Task Mutations based on WORKING SuperOps API format
# Reference: Working curl command for task creation
CREATE_TASK_MUTATION = """
mutation createTask($input: CreateTaskInput!) {
    createTask(input: $input) {
        taskId
        title
        description
        status
    }
}
"""

UPDATE_TICKET_MUTATION = """
mutation updateTicket($id: ID!, $input: UpdateTicketInput!) {
    updateTicket(id: $id, input: $input) {
        id
        number
        subject
        description
        status
        priority
        category
        assignee {
            id
            name
            email
        }
        updatedAt
    }
}
"""

ASSIGN_TICKET_MUTATION = """
mutation assignTicket($id: ID!, $assigneeId: ID!) {
    assignTicket(id: $id, assigneeId: $assigneeId) {
        id
        number
        assignee {
            id
            name
            email
        }
        updatedAt
    }
}
"""

RESOLVE_TICKET_MUTATION = """
mutation resolveTicket($id: ID!, $resolution: String!) {
    resolveTicket(id: $id, resolution: $resolution) {
        id
        number
        status
        resolution
        updatedAt
    }
}
"""

CLOSE_TICKET_MUTATION = """
mutation CloseTicket($ticketId: ID!, $notes: String) {
    closeTicket(ticketId: $ticketId, notes: $notes) {
        id
        number
        status
        updatedAt
    }
}
"""

REOPEN_TICKET_MUTATION = """
mutation ReopenTicket($ticketId: ID!, $reason: String!) {
    reopenTicket(ticketId: $ticketId, reason: $reason) {
        id
        number
        status
        reopenedCount
        updatedAt
    }
}
"""

# Time Tracking Mutations
LOG_TIME_MUTATION = """
mutation LogTimeEntry($input: TimeEntryInput!) {
    logTimeEntry(input: $input) {
        id
        ticketId
        duration
        description
        billable
        createdAt
        user {
            id
            name
        }
    }
}
"""

UPDATE_TIME_ENTRY_MUTATION = """
mutation UpdateTimeEntry($id: ID!, $input: UpdateTimeEntryInput!) {
    updateTimeEntry(id: $id, input: $input) {
        id
        ticketId
        duration
        description
        billable
        updatedAt
    }
}
"""

DELETE_TIME_ENTRY_MUTATION = """
mutation DeleteTimeEntry($id: ID!) {
    deleteTimeEntry(id: $id) {
        success
        message
    }
}
"""

# Work Log Mutations
ADD_WORKLOG_MUTATION = """
mutation AddWorkLog($input: WorkLogInput!) {
    addWorkLog(input: $input) {
        id
        ticketId
        description
        timeSpent
        visibility
        createdAt
        user {
            id
            name
        }
    }
}
"""

UPDATE_WORKLOG_MUTATION = """
mutation UpdateWorkLog($id: ID!, $input: UpdateWorkLogInput!) {
    updateWorkLog(id: $id, input: $input) {
        id
        ticketId
        description
        timeSpent
        visibility
        updatedAt
    }
}
"""

DELETE_WORKLOG_MUTATION = """
mutation DeleteWorkLog($id: ID!) {
    deleteWorkLog(id: $id) {
        success
        message
    }
}
"""

# Comment Mutations
ADD_COMMENT_MUTATION = """
mutation AddComment($input: CommentInput!) {
    addComment(input: $input) {
        id
        ticketId
        content
        visibility
        createdAt
        user {
            id
            name
        }
    }
}
"""

UPDATE_COMMENT_MUTATION = """
mutation UpdateComment($id: ID!, $content: String!) {
    updateComment(id: $id, content: $content) {
        id
        content
        updatedAt
    }
}
"""

DELETE_COMMENT_MUTATION = """
mutation DeleteComment($id: ID!) {
    deleteComment(id: $id) {
        success
        message
    }
}
"""

# User Mutations
CREATE_USER_MUTATION = """
mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
        id
        name
        email
        role
        department
        isActive
    }
}
"""

UPDATE_USER_MUTATION = """
mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
    updateUser(id: $id, input: $input) {
        id
        name
        email
        role
        department
        skills
        maxConcurrentTickets
        isActive
        updatedAt
    }
}
"""

DEACTIVATE_USER_MUTATION = """
mutation DeactivateUser($id: ID!) {
    deactivateUser(id: $id) {
        id
        isActive
        updatedAt
    }
}
"""