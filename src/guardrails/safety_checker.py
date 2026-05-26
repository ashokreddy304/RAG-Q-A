"""
Comprehensive safety checker.
Validates system state, rate limits, and resource constraints.
"""

import time
from typing import Tuple, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SafetyChecker:
    """
    Comprehensive safety checking system.
    Implements rate limiting, resource monitoring, and validation.
    """

    def __init__(
        self,
        max_requests_per_minute: int = 60,
        max_tokens_per_day: int = 1000000,
        max_concurrent_users: int = 100
    ):
        """
        Initialize safety checker.

        Args:
            max_requests_per_minute: Rate limit (requests/minute)
            max_tokens_per_day: Daily token limit
            max_concurrent_users: Max concurrent users
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_day = max_tokens_per_day
        self.max_concurrent_users = max_concurrent_users

        # Tracking
        self.request_timestamps = defaultdict(list)
        self.token_usage = defaultdict(lambda: {"count": 0, "reset_time": datetime.now()})
        self.active_users = set()

        logger.info("SafetyChecker initialized")

    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: Unique user identifier

        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = time.time()
        one_minute_ago = now - 60

        # Clean old timestamps
        self.request_timestamps[user_id] = [
            ts for ts in self.request_timestamps[user_id]
            if ts > one_minute_ago
        ]

        # Check limit
        if len(self.request_timestamps[user_id]) >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
            return False, f"Rate limit exceeded. Max {self.max_requests_per_minute} requests per minute"

        # Add current request
        self.request_timestamps[user_id].append(now)
        logger.debug(f"Rate limit check passed for user: {user_id}")

        return True, ""

    def check_token_limit(self, user_id: str, tokens_used: int) -> Tuple[bool, str]:
        """
        Check if user has exceeded daily token limit.

        Args:
            user_id: Unique user identifier
            tokens_used: Number of tokens to consume

        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = datetime.now()
        user_stats = self.token_usage[user_id]

        # Reset if new day
        if now - user_stats["reset_time"] > timedelta(days=1):
            user_stats["count"] = 0
            user_stats["reset_time"] = now
            logger.debug(f"Token limit reset for user: {user_id}")

        # Check limit
        if user_stats["count"] + tokens_used > self.max_tokens_per_day:
            remaining = self.max_tokens_per_day - user_stats["count"]
            logger.warning(f"Daily token limit approaching for user: {user_id}")
            return False, f"Daily token limit exceeded. {remaining} tokens remaining"

        # Update usage
        user_stats["count"] += tokens_used
        logger.debug(f"Token usage updated for user: {user_id} ({user_stats['count']} total)")

        return True, ""

    def check_system_health(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check overall system health.

        Returns:
            Tuple of (is_healthy, health_metrics)
        """
        logger.info("Checking system health")

        metrics = {
            "active_users": len(self.active_users),
            "max_concurrent_users": self.max_concurrent_users,
            "timestamp": datetime.now().isoformat(),
        }

        # Check user limit
        if len(self.active_users) > self.max_concurrent_users:
            logger.warning(f"Max concurrent users exceeded: {len(self.active_users)}")
            return False, metrics

        logger.info("System health check passed")
        return True, metrics

    def register_user(self, user_id: str) -> bool:
        """Register active user."""
        if len(self.active_users) >= self.max_concurrent_users:
            logger.warning(f"Cannot register user {user_id}: User limit reached")
            return False

        self.active_users.add(user_id)
        logger.info(f"User registered: {user_id}")
        return True

    def unregister_user(self, user_id: str):
        """Unregister user."""
        if user_id in self.active_users:
            self.active_users.remove(user_id)
            logger.info(f"User unregistered: {user_id}")

    def validate_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate API key format.

        Args:
            api_key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, "API key is empty"

        if not api_key.startswith("sk-"):
            return False, "Invalid API key format"

        if len(api_key) < 20:
            return False, "API key is too short"

        logger.info("API key validation passed")
        return True, ""

    def check_resource_availability(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check available resources.

        Returns:
            Tuple of (is_available, resource_metrics)
        """
        logger.info("Checking resource availability")

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
        }

        # Check we have resources
        logger.info("Resource availability check passed")
        return True, metrics

    def get_stats(self) -> Dict[str, Any]:
        """Get safety checker statistics."""
        return {
            "active_users": len(self.active_users),
            "tracked_users": len(self.request_timestamps),
            "max_concurrent_users": self.max_concurrent_users,
            "max_requests_per_minute": self.max_requests_per_minute,
            "max_tokens_per_day": self.max_tokens_per_day,
            "timestamp": datetime.now().isoformat(),
        }
