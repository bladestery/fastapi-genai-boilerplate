"""Simple in-memory caching setup using aiocache."""

from aiocache import Cache

# Initialize an in-memory cache with a Time-To-Live (TTL) of 600 seconds (10 minutes)
cache = Cache(Cache.MEMORY, ttl=600)
