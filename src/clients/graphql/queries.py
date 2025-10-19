"""GraphQL queries for SuperOps API"""

# Ticket Queries
GET_TICKET_QUERY = """
query GetTicket($id: ID!) {
    ticket(id: $id) {
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
        requester {
            id
            name
            email
        }
        createdAt
        updatedAt
        resolvedAt
        tags
        customFields
        timeEntries {
            id
            duration
            description
            createdAt
            user {
                id
                name
            }
        }
        workLogs {
            id
            description
            timeSpent
            createdAt
            user {
                id
                name
            }
        }
    }
}
"""

GET_TICKETS_BY_DATE_RANGE_QUERY = """
query GetTicketsByDateRange($dateRange: String!, $filters: TicketFilters) {
    ticketsByDateRange(dateRange: $dateRange, filters: $filters) {
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
        requester {
            id
            name
            email
        }
        createdAt
        updatedAt
        resolvedAt
    }
}
"""

GET_ACTIVE_TICKETS_QUERY = """
query GetActiveTickets {
    activeTickets {
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
        requester {
            id
            name
            email
        }
        createdAt
        updatedAt
    }
}
"""

GET_TICKETS_BY_ASSIGNEE_QUERY = """
query GetTicketsByAssignee($assigneeId: ID!) {
    ticketsByAssignee(assigneeId: $assigneeId) {
        id
        number
        subject
        description
        status
        priority
        category
        createdAt
        updatedAt
        requester {
            id
            name
            email
        }
    }
}
"""

GET_TICKET_ANALYTICS_QUERY = """
query GetTicketAnalytics($dateRange: String!, $filters: AnalyticsFilters) {
    ticketAnalytics(dateRange: $dateRange, filters: $filters) {
        totalTickets
        resolvedTickets
        averageResolutionTime
        ticketsByStatus {
            status
            count
        }
        ticketsByPriority {
            priority
            count
        }
        ticketsByCategory {
            category
            count
        }
        topAssignees {
            assignee {
                id
                name
            }
            ticketCount
            averageResolutionTime
        }
    }
}
"""

SEARCH_TICKETS_QUERY = """
query SearchTickets($query: String!, $filters: TicketFilters, $limit: Int, $offset: Int) {
    searchTickets(query: $query, filters: $filters, limit: $limit, offset: $offset) {
        tickets {
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
            requester {
                id
                name
                email
            }
            createdAt
            updatedAt
        }
        totalCount
        hasMore
    }
}
"""

GET_USER_QUERY = """
query GetUser($id: ID!) {
    user(id: $id) {
        id
        name
        email
        role
        department
        isActive
        skills
        maxConcurrentTickets
        currentTicketCount
    }
}
"""

GET_USERS_QUERY = """
query GetUsers($filters: UserFilters) {
    users(filters: $filters) {
        id
        name
        email
        role
        department
        isActive
        skills
        maxConcurrentTickets
        currentTicketCount
    }
}
"""

GET_TECHNICIANS_QUERY = """
query GetTechnicians {
    technicians {
        id
        name
        email
        department
        skills
        maxConcurrentTickets
        currentTicketCount
        isActive
    }
}
"""

# SLA Queries
GET_SLA_POLICIES_QUERY = """
query GetSLAPolicies {
    slaPolicies {
        id
        name
        description
        priority
        responseTimeMinutes
        resolutionTimeHours
        businessHoursOnly
        isActive
        escalationRules {
            id
            name
            triggerAfterMinutes
            escalateToRole
            escalateToUsers
            notificationTemplate
            isActive
        }
        createdAt
        updatedAt
    }
}
"""

GET_SLA_POLICY_QUERY = """
query GetSLAPolicy($id: ID!) {
    slaPolicy(id: $id) {
        id
        name
        description
        priority
        responseTimeMinutes
        resolutionTimeHours
        businessHoursOnly
        isActive
        escalationRules {
            id
            name
            triggerAfterMinutes
            escalateToRole
            escalateToUsers
            notificationTemplate
            isActive
        }
        alertRules {
            id
            name
            condition
            severity
            notificationChannels
            isActive
            cooldownMinutes
        }
        createdAt
        updatedAt
    }
}
"""

GET_TICKET_SLA_STATUS_QUERY = """
query GetTicketSLAStatus($ticketId: ID!) {
    ticketSLAStatus(ticketId: $ticketId) {
        ticketId
        ticketNumber
        slaPolicy {
            id
            name
            priority
            responseTimeMinutes
            resolutionTimeHours
            businessHoursOnly
        }
        createdAt
        firstResponseAt
        resolvedAt
        responseTimeRemaining
        resolutionTimeRemaining
        isResponseBreached
        isResolutionBreached
        breachRiskLevel
        escalationLevel
        lastUpdated
    }
}
"""

GET_SLA_BREACHES_QUERY = """
query GetSLABreaches($dateRange: String!, $filters: SLABreachFilters) {
    slaBreaches(dateRange: $dateRange, filters: $filters) {
        id
        ticketId
        ticketNumber
        breachType
        breachTime
        slaPolicy {
            id
            name
            priority
        }
        technician {
            id
            name
            email
        }
        severity
        customerImpact
        escalationRequired
        escalationLevel
        resolutionTime
        rootCause
        correctiveActions
        createdAt
    }
}
"""

GET_TECHNICIAN_SLA_METRICS_QUERY = """
query GetTechnicianSLAMetrics($technicianId: ID!, $dateRange: String!) {
    technicianSLAMetrics(technicianId: $technicianId, dateRange: $dateRange) {
        technicianId
        technicianName
        technicianEmail
        periodStart
        periodEnd
        totalTickets
        slaCompliantTickets
        responseBreaches
        resolutionBreaches
        averageResponseTime
        averageResolutionTime
        performanceTrend
        lastUpdated
    }
}
"""

GET_ALL_TECHNICIANS_SLA_METRICS_QUERY = """
query GetAllTechniciansSLAMetrics($dateRange: String!, $filters: TechnicianFilters) {
    allTechniciansSLAMetrics(dateRange: $dateRange, filters: $filters) {
        technicianId
        technicianName
        technicianEmail
        totalTickets
        slaCompliantTickets
        responseBreaches
        resolutionBreaches
        averageResponseTime
        averageResolutionTime
        complianceRate
        breachRate
        performanceTrend
    }
}
"""

# Enhanced User Queries for SLA Integration
GET_ALL_USERS_QUERY = """
query GetAllUsers($filters: UserFilters) {
    users(filters: $filters) {
        id
        name
        email
        username
        role
        department
        isActive
        skills
        maxConcurrentTickets
        currentTicketCount
        phoneNumber
        timezone
        lastLoginAt
        createdAt
        updatedAt
    }
}
"""

GET_USER_LIST_QUERY = """
query GetUserList {
    users {
        id
        name
        email
        username
        role
        department
        isActive
        phoneNumber
        timezone
        lastLoginAt
    }
}
"""

# Enhanced Ticket Queries for SLA Integration
GET_TICKETS_WITH_SLA_QUERY = """
query GetTicketsWithSLA($filters: TicketFilters, $limit: Int, $offset: Int) {
    tickets(filters: $filters, limit: $limit, offset: $offset) {
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
            username
        }
        requester {
            id
            name
            email
        }
        slaStatus {
            responseTimeRemaining
            resolutionTimeRemaining
            isResponseBreached
            isResolutionBreached
            breachRiskLevel
        }
        createdAt
        updatedAt
        resolvedAt
        firstResponseAt
        tags
        customFields
    }
}
"""

GET_URGENT_TICKETS_QUERY = """
query GetUrgentTickets {
    urgentTickets {
        id
        number
        subject
        status
        priority
        assignee {
            id
            name
            email
            username
        }
        slaStatus {
            responseTimeRemaining
            resolutionTimeRemaining
            breachRiskLevel
            isResponseBreached
            isResolutionBreached
        }
        createdAt
        updatedAt
    }
}
"""

GET_TICKETS_AT_RISK_QUERY = """
query GetTicketsAtRisk($riskLevel: String!) {
    ticketsAtRisk(riskLevel: $riskLevel) {
        id
        number
        subject
        priority
        assignee {
            id
            name
            email
            username
        }
        slaStatus {
            responseTimeRemaining
            resolutionTimeRemaining
            breachRiskLevel
        }
        createdAt
    }
}
"""

# Task Queries
GET_TASKS_QUERY = """
query GetTasks($filters: TaskFilters, $limit: Int, $offset: Int) {
    tasks(filters: $filters, limit: $limit, offset: $offset) {
        id
        title
        description
        status
        priority
        assignee {
            id
            name
            email
        }
        dueDate
        createdAt
        updatedAt
        completedAt
        tags
        relatedTickets {
            id
            number
            subject
        }
    }
}
"""

GET_OPEN_TASKS_QUERY = """
query GetOpenTasks {
    openTasks {
        id
        title
        description
        priority
        assignee {
            id
            name
            email
        }
        dueDate
        createdAt
        relatedTickets {
            id
            number
        }
    }
}
"""

GET_SCHEDULED_TASKS_QUERY = """
query GetScheduledTasks($dateRange: String!) {
    scheduledTasks(dateRange: $dateRange) {
        id
        title
        description
        priority
        assignee {
            id
            name
            email
        }
        scheduledDate
        dueDate
        createdAt
    }
}
"""

GET_COMPLETED_TASKS_QUERY = """
query GetCompletedTasks($dateRange: String!, $filters: TaskFilters) {
    completedTasks(dateRange: $dateRange, filters: $filters) {
        id
        title
        description
        assignee {
            id
            name
            email
        }
        completedAt
        createdAt
        dueDate
        completionTime
    }
}
"""

# SLA Reporting Queries
GET_SLA_REPORT_DATA_QUERY = """
query GetSLAReportData($dateRange: String!, $filters: SLAReportFilters) {
    slaReportData(dateRange: $dateRange, filters: $filters) {
        periodStart
        periodEnd
        overallMetrics {
            totalTickets
            slaCompliantTickets
            responseBreaches
            resolutionBreaches
            averageResponseTime
            averageResolutionTime
            complianceRate
            breachRate
        }
        metricsByPriority {
            priority
            totalTickets
            slaCompliantTickets
            complianceRate
            averageResponseTime
            averageResolutionTime
        }
        metricsByTechnician {
            technicianId
            technicianName
            totalTickets
            complianceRate
            breachCount
        }
        breachIncidents {
            id
            ticketId
            breachType
            breachTime
            severity
            technician {
                id
                name
            }
        }
        trends {
            complianceRateTrend
            breachRateTrend
            responseTimeTrend
            resolutionTimeTrend
        }
    }
}
"""

# Event Monitoring Queries
GET_RECENT_TICKET_EVENTS_QUERY = """
query GetRecentTicketEvents($since: String!) {
    recentTicketEvents(since: $since) {
        id
        ticketId
        eventType
        eventData
        timestamp
        user {
            id
            name
        }
    }
}
"""

GET_SLA_EVENTS_QUERY = """
query GetSLAEvents($since: String!) {
    slaEvents(since: $since) {
        id
        ticketId
        eventType
        eventData
        timestamp
        slaPolicy {
            id
            name
        }
    }
}
"""

# Mutations for Automated Actions
ADD_TICKET_COMMENT_MUTATION = """
mutation AddTicketComment($ticketId: ID!, $comment: String!, $isInternal: Boolean, $mentionUsers: [ID!]) {
    addTicketComment(ticketId: $ticketId, comment: $comment, isInternal: $isInternal, mentionUsers: $mentionUsers) {
        id
        comment
        author {
            id
            name
        }
        createdAt
        isInternal
        mentionedUsers {
            id
            name
            email
        }
    }
}
"""

UPDATE_TICKET_PRIORITY_MUTATION = """
mutation UpdateTicketPriority($ticketId: ID!, $priority: String!) {
    updateTicketPriority(ticketId: $ticketId, priority: $priority) {
        id
        priority
        updatedAt
    }
}
"""

ESCALATE_TICKET_MUTATION = """
mutation EscalateTicket($ticketId: ID!, $escalationLevel: Int!, $reason: String!) {
    escalateTicket(ticketId: $ticketId, escalationLevel: $escalationLevel, reason: $reason) {
        id
        escalationLevel
        escalationReason
        escalatedAt
        escalatedBy {
            id
            name
        }
    }
}
"""

ASSIGN_TICKET_MUTATION = """
mutation AssignTicket($ticketId: ID!, $assigneeId: ID!, $reason: String) {
    assignTicket(ticketId: $ticketId, assigneeId: $assigneeId, reason: $reason) {
        id
        assignee {
            id
            name
            email
        }
        assignedAt
        assignedBy {
            id
            name
        }
    }
}
"""

UPDATE_TICKET_STATUS_MUTATION = """
mutation UpdateTicketStatus($ticketId: ID!, $status: String!, $reason: String) {
    updateTicketStatus(ticketId: $ticketId, status: $status, reason: $reason) {
        id
        status
        updatedAt
        statusHistory {
            status
            changedAt
            changedBy {
                id
                name
            }
        }
    }
}
"""

CREATE_SLA_BREACH_RECORD_MUTATION = """
mutation CreateSLABreachRecord($input: SLABreachInput!) {
    createSLABreachRecord(input: $input) {
        id
        ticketId
        breachType
        breachTime
        severity
        escalationRequired
        createdAt
    }
}
"""

SEND_NOTIFICATION_MUTATION = """
mutation SendNotification($input: NotificationInput!) {
    sendNotification(input: $input) {
        id
        recipientId
        message
        channel
        sentAt
        status
    }
}
"""

UPDATE_SLA_POLICY_MUTATION = """
mutation UpdateSLAPolicy($id: ID!, $input: SLAPolicyInput!) {
    updateSLAPolicy(id: $id, input: $input) {
        id
        name
        responseTimeMinutes
        resolutionTimeHours
        updatedAt
    }
}
"""

# Subscription Queries for Real-time Events
TICKET_EVENTS_SUBSCRIPTION = """
subscription TicketEvents($ticketIds: [ID!]) {
    ticketEvents(ticketIds: $ticketIds) {
        id
        ticketId
        eventType
        eventData
        timestamp
        user {
            id
            name
        }
    }
}
"""

SLA_BREACH_SUBSCRIPTION = """
subscription SLABreachEvents {
    slaBreachEvents {
        id
        ticketId
        breachType
        breachTime
        severity
        slaPolicy {
            id
            name
        }
        technician {
            id
            name
            email
        }
    }
}
"""

TICKET_STATUS_SUBSCRIPTION = """
subscription TicketStatusChanges {
    ticketStatusChanges {
        ticketId
        oldStatus
        newStatus
        changedAt
        changedBy {
            id
            name
        }
    }
}
"""

TICKET_ASSIGNMENT_SUBSCRIPTION = """
subscription TicketAssignmentChanges {
    ticketAssignmentChanges {
        ticketId
        oldAssignee {
            id
            name
        }
        newAssignee {
            id
            name
        }
        assignedAt
        assignedBy {
            id
            name
        }
    }
}
"""