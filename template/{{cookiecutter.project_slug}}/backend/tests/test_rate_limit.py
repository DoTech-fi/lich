"""
Unit tests for the in-memory rate limiter.
"""
import time

from api.middleware.rate_limit import RateLimitMiddleware


def test_sweep_evicts_stale_ips():
    mw = RateLimitMiddleware(app=None, requests_per_minute=60)
    mw.requests["1.2.3.4"] = [time.time() - 120]
    mw.requests["5.6.7.8"] = [time.time()]
    mw._last_sweep = time.time() - 61

    mw._sweep_stale(time.time())

    assert "1.2.3.4" not in mw.requests
    assert "5.6.7.8" in mw.requests


def test_sweep_is_throttled():
    mw = RateLimitMiddleware(app=None, requests_per_minute=60)
    mw.requests["1.2.3.4"] = [time.time() - 120]
    mw._last_sweep = time.time()

    mw._sweep_stale(time.time())

    assert "1.2.3.4" in mw.requests
