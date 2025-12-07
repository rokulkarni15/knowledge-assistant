import redis.asyncio as redis
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self.client = None
    
    async def connect(self):
        """Connect to Redis"""
        if self.client is None:
            try:
                self.client = await redis.from_url(self.url, decode_responses=True)
                logger.info("Connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.client = None
    
    async def get(self, key: str):
        """Get value from cache"""
        if self.client is None:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                logger.info(f"Cache HIT: {key[:30]}...")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key[:30]}...")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration (seconds)"""
        if self.client is None:
            return
        
        try:
            await self.client.set(key, json.dumps(value), ex=expire)
            logger.debug(f"💾 Cached: {key[:30]}... (TTL: {expire}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if self.client is None:
            return
        
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def make_key(self, prefix: str, *args) -> str:
        """Create cache key from components"""
        combined = f"{prefix}:{':'.join(str(a) for a in args)}"
        # Use hash for consistent key length
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()