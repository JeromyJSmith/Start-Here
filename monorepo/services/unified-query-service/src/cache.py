"""
Cache implementation for query results
"""

import asyncio
import time
from typing import Dict, Any, Optional
from collections import OrderedDict

import aiocache
from aiocache import Cache
from aiocache.serializers import JsonSerializer

from .config import settings


class QueryCache:
    """LRU cache for query results"""
    
    def __init__(self):
        cache_config = settings.CACHE_CONFIG.get("query_cache", {})
        
        # Use aiocache with Redis backend if available
        if settings.REDIS_URL:
            self.cache = Cache(
                Cache.REDIS,
                endpoint=settings.REDIS_URL.split("://")[1].split(":")[0],
                port=int(settings.REDIS_URL.split(":")[-1]),
                ttl=cache_config.get("ttl", 300),
                serializer=JsonSerializer()
            )
        else:
            # Fallback to memory cache
            self.cache = Cache(
                Cache.MEMORY,
                ttl=cache_config.get("ttl", 300),
                serializer=JsonSerializer()
            )
        
        self.max_size = cache_config.get("max_size", 1000)
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache"""
        result = await self.cache.get(key)
        
        if result:
            self.hits += 1
        else:
            self.misses += 1
        
        return result
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """Set item in cache"""
        await self.cache.set(key, value, ttl=ttl)
    
    async def clear(self):
        """Clear all cache entries"""
        await self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }