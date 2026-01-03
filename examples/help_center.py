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

        # List categories with pagination
        print("--- Categories ---")
        categories_paginator = await hc.get_categories(per_page=10)
        categories = await categories_paginator.get_page()
        for cat in categories[:5]:
            print(f"Category: {cat['name']} (ID: {cat['id']})")

        # Get specific category
        if categories:
            category = await hc.get_category(categories[0]["id"])
            print(f"\nCategory details: {category.name}")
            print(f"Description: {category.description}")

        # List sections (all or by category)
        print("\n--- Sections ---")
        sections_paginator = await hc.get_sections(per_page=10)
        sections = await sections_paginator.get_page()
        for sec in sections[:5]:
            print(f"Section: {sec['name']} (Category: {sec['category_id']})")

        # List articles in a section
        if sections:
            section_id = sections[0]["id"]
            articles_paginator = await hc.get_section_articles(section_id, per_page=10)
            articles = await articles_paginator.get_page()
            print(f"\nArticles in section {section_id}:")
            for art in articles[:5]:
                print(f"  - {art['title']}")

        # ==================== Search ====================

        # Search articles (useful for AI assistants)
        print("\n--- Article Search ---")
        search_results = await hc.search_articles("password reset", per_page=5)
        for article in search_results:
            print(f"Found: {article.title}")
            if article.snippet:
                print(f"  Snippet: {article.snippet[:100]}...")

        # ==================== CRUD Operations ====================

        # Create a category
        print("\n--- Creating Content ---")
        new_category = await hc.create_category(
            name="API Documentation",
            description="Documentation for our REST API",
        )
        print(f"Created category: {new_category.name} (ID: {new_category.id})")

        # Create a section in the category
        new_section = await hc.create_section(
            category_id=new_category.id,
            name="Getting Started",
            description="Quick start guides",
        )
        print(f"Created section: {new_section.name} (ID: {new_section.id})")

        # Create an article in the section
        new_article = await hc.create_article(
            section_id=new_section.id,
            title="Authentication Guide",
            body="<h1>Authentication</h1><p>Use API tokens to authenticate...</p>",
            draft=True,  # Create as draft first
            permission_group_id=252606,  # Required - get from existing articles
            label_names=["api", "authentication", "getting-started"],
        )
        print(f"Created article: {new_article.title} (draft: {new_article.draft})")

        # Update the article
        updated_article = await hc.update_article(
            new_article.id,
            title="Authentication Guide - Updated",
            draft=False,  # Publish the article
            promoted=True,  # Feature it
        )
        print(f"Updated article: {updated_article.title} (promoted: {updated_article.promoted})")

        # Delete individual article
        await hc.delete_article(new_article.id)
        print("Deleted article")

        # Create another article for cascade delete demo
        demo_article = await hc.create_article(
            section_id=new_section.id,
            title="Demo Article",
            body="<p>This will be deleted with the category</p>",
            draft=True,
            permission_group_id=252606,
        )
        print(f"Created demo article: {demo_article.title}")

        # Cascade delete - removes category, section, and all articles
        # force=True is required as a safety measure
        await hc.delete_category(new_category.id, force=True)
        print("Deleted category (cascade deleted section and article)")

        # ==================== Pagination ====================

        # Iterate through all articles with async for
        print("\n--- Pagination Example ---")
        all_articles_paginator = await hc.get_articles(per_page=10)
        count = 0
        async for article_data in all_articles_paginator:
            count += 1
            if count <= 3:
                print(f"Article {count}: {article_data['title'][:40]}...")
            if count >= 10:
                print(f"... and more (stopped at {count})")
                break


if __name__ == "__main__":
    asyncio.run(main())
