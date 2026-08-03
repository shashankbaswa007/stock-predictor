import time
from typing import Dict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    A simple in-memory rate limiter middleware.
    Limits each IP to 100 requests per minute.
    Note: For production, use Redis.
    """
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.rate_limit_records: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Cleanup old records (simple implementation for prototype)
        if len(self.rate_limit_records) > 10000:
            self.rate_limit_records.clear()

        if client_ip in self.rate_limit_records:
            count, start_time = self.rate_limit_records[client_ip]

            # Reset bucket if a minute has passed
            if now - start_time > 60:
                self.rate_limit_records[client_ip] = (1, now)
            else:
                if count >= self.requests_per_minute:
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Too Many Requests", "message": f"Rate limit exceeded: {self.requests_per_minute} requests per minute."}
                    )
                self.rate_limit_records[client_ip] = (count + 1, start_time)
        else:
            self.rate_limit_records[client_ip] = (1, now)

        response = await call_next(request)
        return response
