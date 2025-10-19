"""GraphQL fragments for SuperOps API"""

TICKET_FRAGMENT = """
fragment TicketFragment on Ticket {
    id
    number
    title
    description
    priority
    status
    category
    requesterEmail
    assignedTo {
        ...UserFragment
    }
    createdAt
    updatedAt
    resolvedAt
    resolutionTime
    firstResponseTime
    reopenedCount
    escalated
    tags
    customFields
}
"""

USER_FRAGMENT = """
fragment UserFragment on User {
    id
    email
    firstName
    lastName
    role
    department
    isActive
}
"""

TIME_ENTRY_FRAGMENT = """
fragment TimeEntryFragment on TimeEntry {
    id
    ticketId
    userId
    timeSpent
    description
    date
    createdAt
    updatedAt
}
"""

WORKLOG_FRAGMENT = """
fragment WorklogFragment on WorkLog {
    id
    ticketId
    activityType
    description
    timestamp
    userId
    statusUpdate
}
"""
