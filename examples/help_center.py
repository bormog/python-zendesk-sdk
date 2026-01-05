"""Help Center example for Zendesk SDK.

This example demonstrates:
- Help Center hierarchy (Categories -> Sections -> Articles)
- CRUD operations for categories, sections, and articles
- Article search with snippets
- Pagination through Help Center content
- Cascade deletion with force parameter
"""

import asyncio

from zendesk_sdk import ZendeskClient, ZendeskConfig


async def main() -> None:
    # Configuration
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",
    )

    async with ZendeskClient(config) as client:
        hc = client.help_center

        # ==================== Reading Content ====================

        # List categories with pagination (no await for list())
        print("--- Categories ---")
        categories = await hc.categories.list(per_page=10).get_page()
        for cat in categories[:5]:
            print(f"Category: {cat.name} (ID: {cat.id})")

        # Get specific category
        if categories:
            category = await hc.categories.get(categories[0].id)
            print(f"\nCategory details: {category.name}")
            print(f"Description: {category.description}")

        # List sections (all or by category)
        print("\n--- Sections ---")
        sections = await hc.sections.list(per_page=10).get_page()
        for sec in sections[:5]:
            print(f"Section: {sec.name} (Category: {sec.category_id})")

        # List articles in a section
        if sections:
            section_id = sections[0].id
            articles = await hc.articles.for_section(section_id, per_page=10).get_page()
            print(f"\nArticles in section {section_id}:")
            for art in articles[:5]:
                print(f"  - {art.title}")

        # ==================== Search ====================

        # Search articles (useful for AI assistants)
        print("\n--- Article Search ---")
        search_results = await hc.articles.search("password reset", per_page=5)
        for article in search_results:
            print(f"Found: {article.title}")
            if article.snippet:
                print(f"  Snippet: {article.snippet[:100]}...")

        # ==================== CRUD Operations ====================

        # Create a category
        print("\n--- Creating Content ---")
        new_category = await hc.categories.create(
            name="API Documentation",
            description="Documentation for our REST API",
        )
        print(f"Created category: {new_category.name} (ID: {new_category.id})")

        # Create a section in the category
        new_section = await hc.sections.create(
            category_id=new_category.id,
            name="Getting Started",
            description="Quick start guides",
        )
        print(f"Created section: {new_section.name} (ID: {new_section.id})")

        # Get permission_group_id from an existing article (required for creation)
        existing_articles = await hc.articles.list(per_page=1).get_page()
        if not existing_articles:
            print("No existing articles to get permission_group_id from")
            return
        existing = await hc.articles.get(existing_articles[0].id)
        permission_group_id = existing.permission_group_id

        # Create an article in the section
        new_article = await hc.articles.create(
            section_id=new_section.id,
            title="Authentication Guide",
            body="<h1>Authentication</h1><p>Use API tokens to authenticate...</p>",
            draft=True,  # Create as draft first
            permission_group_id=permission_group_id,
            label_names=["api", "authentication", "getting-started"],
        )
        print(f"Created article: {new_article.title} (draft: {new_article.draft})")

        # Update the article
        updated_article = await hc.articles.update(
            new_article.id,
            title="Authentication Guide - Updated",
            promoted=True,  # Feature it
        )
        print(f"Updated article: {updated_article.title} (promoted: {updated_article.promoted})")

        # Delete individual article
        await hc.articles.delete(new_article.id)
        print("Deleted article")

        # Create another article for cascade delete demo
        demo_article = await hc.articles.create(
            section_id=new_section.id,
            title="Demo Article",
            body="<p>This will be deleted with the category</p>",
            draft=True,
            permission_group_id=permission_group_id,
        )
        print(f"Created demo article: {demo_article.title}")

        # Cascade delete - removes category, section, and all articles
        # force=True is required as a safety measure
        await hc.categories.delete(new_category.id, force=True)
        print("Deleted category (cascade deleted section and article)")

        # ==================== Pagination Examples ====================

        print("\n--- Pagination Examples ---")

        # Iterate through all articles
        count = 0
        async for article in hc.articles.list(per_page=10):
            count += 1
            if count <= 3:
                title = article.title[:40] if article.title else "Untitled"
                print(f"Article {count}: {title}...")
            if count >= 10:
                print(f"... and more (stopped at {count})")
                break

        # Collect articles to list
        all_articles = await hc.articles.list(limit=50).collect()
        print(f"Collected {len(all_articles)} articles")


if __name__ == "__main__":
    asyncio.run(main())
