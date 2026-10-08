"""Rate limiter for external API calls to respect rate limits"""

import asyncio
import time
from typing import Dict
from datetime import datetime, timedelta


class RateLimiter:
    """Rate limiter that tracks calls per minute and enforces limits"""

    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.call_times: list = []
        self.last_check = time.time()

    async def wait_if_needed(self) -> None:
        """Wait if rate limit is reached"""
        now = time.time()

        # Clean old calls (older than 1 minute)
        cutoff = now - 60
        self.call_times = [t for t in self.call_times if t > cutoff]

        # Check if we've hit the limit
        if len(self.call_times) >= self.calls_per_minute:
            # Calculate how long to wait
            oldest_call = self.call_times[0]
            wait_time = 60 - (now - oldest_call)

            if wait_time > 0:
                await asyncio.sleep(wait_time)
                # Clean again after waiting
                now = time.time()
                self.call_times = [t for t in self.call_times if t > (now - 60)]

        # Record this call
        self.call_times.append(time.time())


# Rate limiters for different APIs
# Alpha Vantage: 5 calls per minute (free tier)
alpha_vantage_limiter = RateLimiter(5)

# NewsAPI: 100 requests per day (we'll implement as 5 per minute to be safe)
news_api_limiter = RateLimiter(5)

# Finnhub: 60 calls per minute (free tier)
finnhub_limiter = RateLimiter(60)
