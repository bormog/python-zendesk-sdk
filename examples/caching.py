"""Caching example for Zendesk SDK.

This example demonstrates:
- Default caching behavior
- Custom cache configuration
- Disabling cache
- Cache statistics and control
"""

import asyncio
import time

from zendesk_sdk import CacheConfig, ZendeskClient, ZendeskConfig


async def demo_default_caching() -> None:
    """Demonstrate default caching behavior."""
    print("=== Default Caching ===")

    # Default config - caching enabled with standard TTLs
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # First call hits the API
        start = time.perf_counter()
        user = await client.users.get(12345)
        first_call = time.perf_counter() - start
        print(f"First call: {first_call:.3f}s - {user.name}")

        # Second call returns cached result
        start = time.perf_counter()
        user = await client.users.get(12345)
        second_call = time.perf_counter() - start
        print(f"Second call (cached): {second_call:.6f}s - {user.name}")

        # Check cache statistics
        info = client.users.get.cache_info()
        print(f"Cache stats: hits={info.hits}, misses={info.misses}")


async def demo_custom_cache_config() -> None:
    """Demonstrate custom cache configuration."""
    print("\n=== Custom Cache Configuration ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
        cache=CacheConfig(
            enabled=True,
            # Shorter TTL for users (1 minute instead of 5)
            user_ttl=60,
            user_maxsize=100,
            # Longer TTL for Help Center (1 hour)
            article_ttl=3600,
            category_ttl=3600,
            section_ttl=3600,
        ),
    )

    async with ZendeskClient(config) as client:
        print(f"User cache TTL: {config.cache.user_ttl}s")
        print(f"Article cache TTL: {config.cache.article_ttl}s")

        user = await client.users.get(12345)
        print(f"Fetched user: {user.name}")


async def demo_disabled_cache() -> None:
    """Demonstrate disabled caching."""
    print("\n=== Disabled Caching ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
        cache=CacheConfig(enabled=False),
    )

    async with ZendeskClient(config) as client:
        print(f"Cache enabled: {config.cache.enabled}")

        # Both calls hit the API
        _ = await client.users.get(12345)
        _ = await client.users.get(12345)
        print("Both calls hit API - no caching")

        # cache_info not available when caching is disabled
        has_cache_info = hasattr(client.users.get, "cache_info")
        print(f"Has cache_info: {has_cache_info}")


async def demo_cache_control() -> None:
    """Demonstrate cache control methods."""
    print("\n=== Cache Control ===")

    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        # Populate cache
        user = await client.users.get(12345)
        print(f"Cached user: {user.name}")

        # Check cache info
        info = client.users.get.cache_info()
        print(f"Before clear: size={info.currsize}, hits={info.hits}")

        # Invalidate specific entry
        was_cached = client.users.get.cache_invalidate(12345)
        print(f"Invalidated user 12345: {was_cached}")

        # Or clear entire cache
        client.users.get.cache_clear()
        info = client.users.get.cache_info()
        print(f"After clear: size={info.currsize}")


async def main() -> None:
    """Run all caching demos."""
    await demo_default_caching()
    await demo_custom_cache_config()
    await demo_disabled_cache()
    await demo_cache_control()


if __name__ == "__main__":
    asyncio.run(main())
