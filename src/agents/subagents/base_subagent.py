"""
Base class for all subagents in the IT Technician Agent system
Provides common functionality for scalable, distributed agent architecture
"""

import asyncio
import logging
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from ..config import AgentConfig
from ...utils.logger import get_logger

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    id: str
    timestamp: datetime
    source_agent: str
    target_topic: str
    message_type: str
    payload: Dict[str, Any]
    priority: int = 5  # 1=highest, 10=lowest
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AgentMetrics:
    """Metrics tracking for agent performance"""
    messages_processed: int = 0
    messages_failed: int = 0
    average_processing_time: float = 0.0
    last_activity: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0

class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self) -> bool:
        """Acquire permission to make a request"""
        now = datetime.now()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if (now - req_time).seconds < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    async def wait_for_slot(self):
        """Wait until a slot becomes available"""
        while not await self.acquire():
            await asyncio.sleep(1)

class BaseSubagent(ABC):
    """Base class for all subagents"""
    
    def __init__(self, config: AgentConfig, agent_name: str):
        self.config = config
        self.agent_name = agent_name
        self.logger = get_logger(f"SubAgent.{agent_name}")
        
        # Agent state
        self.is_running = False
        self.metrics = AgentMetrics()
        self.message_queue = asyncio.Queue()
        self.subscriptions = set()
        self.publications = set()
        
        # Scalability features
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter()
        self.worker_pool = ThreadPoolExecutor(max_workers=self._get_worker_count())
        
        # Communication
        self.session = None
        self.message_handlers = {}
        
        self.logger.info(f"Initialized {agent_name} subagent")
    
    @abstractmethod
    def _get_worker_count(self) -> int:
        """Get optimal worker count for this agent"""
        pass
    
    @abstractmethod
    async def _initialize_agent(self):
        """Initialize agent-specific resources"""
        pass
    
    @abstractmethod
    async def _process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and optionally return response"""
        pass
    
    @abstractmethod
    async def _cleanup_agent(self):
        """Cleanup agent-specific resources"""
        pass
    
    async def start(self):
        """Start the subagent"""
        if self.is_running:
            return
        
        self.logger.info(f"Starting {self.agent_name} subagent")
        
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize agent-specific resources
            await self._initialize_agent()
            
            # Start message processing loop
            self.is_running = True
            asyncio.create_task(self._message_processing_loop())
            
            self.logger.info(f"{self.agent_name} subagent started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start {self.agent_name}: {e}")
            raise
    
    async def stop(self):
        """Stop the subagent"""
        if not self.is_running:
            return
        
        self.logger.info(f"Stopping {self.agent_name} subagent")
        
        self.is_running = False
        
        # Cleanup resources
        await self._cleanup_agent()
        
        if self.session:
            await self.session.close()
        
        self.worker_pool.shutdown(wait=True)
        
        self.logger.info(f"{self.agent_name} subagent stopped")
    
    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.is_running:
            try:
                # Get message from queue with timeout
                try:
                    message = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process message
                start_time = datetime.now()
                
                try:
                    response = await self._process_message(message)
                    
                    # Publish response if generated
                    if response:
                        await self._publish_message(response)
                    
                    # Update metrics
                    processing_time = (datetime.now() - start_time).total_seconds()
                    self._update_metrics(processing_time, success=True)
                    
                except Exception as e:
                    self.logger.error(f"Error processing message {message.id}: {e}")
                    self._update_metrics(0, success=False)
                    
                    # Handle retry logic
                    if message.retry_count < message.max_retries:
                        message.retry_count += 1
                        await asyncio.sleep(2 ** message.retry_count)  # Exponential backoff
                        await self.message_queue.put(message)
                
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(1)
    
    async def subscribe_to_topic(self, topic: str, handler: Callable = None):
        """Subscribe to a message topic"""
        self.subscriptions.add(topic)
        if handler:
            self.message_handlers[topic] = handler
        self.logger.info(f"Subscribed to topic: {topic}")
    
    async def publish_to_topic(self, topic: str):
        """Register as publisher to a topic"""
        self.publications.add(topic)
        self.logger.info(f"Registered as publisher to topic: {topic}")
    
    async def send_message(self, message: AgentMessage):
        """Send message to this agent's queue"""
        await self.message_queue.put(message)
    
    async def _publish_message(self, message: AgentMessage):
        """Publish message to target topic (mock implementation)"""
        # In a real implementation, this would publish to a message broker
        # For now, we'll just log the message
        self.logger.info(f"Publishing message to {message.target_topic}: {message.message_type}")
        self.logger.debug(f"Message payload: {json.dumps(message.payload, default=str)}")
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update agent performance metrics"""
        self.metrics.messages_processed += 1
        self.metrics.last_activity = datetime.now()
        
        if not success:
            self.metrics.messages_failed += 1
        
        # Update average processing time
        if self.metrics.average_processing_time == 0:
            self.metrics.average_processing_time = processing_time
        else:
            self.metrics.average_processing_time = (
                (self.metrics.average_processing_time + processing_time) / 2
            )
        
        # Calculate error rate
        if self.metrics.messages_processed > 0:
            self.metrics.error_rate = (
                self.metrics.messages_failed / self.metrics.messages_processed
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current agent metrics"""
        return {
            "agent_name": self.agent_name,
            "is_running": self.is_running,
            "metrics": asdict(self.metrics),
            "subscriptions": list(self.subscriptions),
            "publications": list(self.publications),
            "queue_size": self.message_queue.qsize(),
            "circuit_breaker_state": self.circuit_breaker.state
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            "agent_name": self.agent_name,
            "status": "healthy" if self.is_running and self.metrics.error_rate < 0.1 else "unhealthy",
            "uptime_seconds": (
                (datetime.now() - self.metrics.last_activity).total_seconds()
                if self.metrics.last_activity else 0
            ),
            "error_rate": self.metrics.error_rate,
            "circuit_breaker_state": self.circuit_breaker.state,
            "queue_size": self.message_queue.qsize()
        }
    
    async def execute_with_circuit_breaker(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        return self.circuit_breaker.call(func, *args, **kwargs)
    
    async def execute_with_rate_limit(self, func: Callable, *args, **kwargs):
        """Execute function with rate limiting"""
        await self.rate_limiter.wait_for_slot()
        return await func(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.agent_name}(running={self.is_running}, processed={self.metrics.messages_processed})"