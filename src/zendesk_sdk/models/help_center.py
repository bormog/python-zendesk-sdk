"""Help Center models for Zendesk API."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .base import ZendeskModel


class Category(ZendeskModel):
    """Help Center Category model.

    Categories are the top-level containers in Help Center hierarchy.
    They contain Sections, which in turn contain Articles.
    """

    id: Optional[int] = Field(None, description="Automatically assigned when created")
    url: Optional[str] = Field(None, description="The API url of this category")
    html_url: Optional[str] = Field(None, description="The url of this category in Help Center")
    position: Optional[int] = Field(None, description="The position of this category relative to others")
    created_at: Optional[datetime] = Field(None, description="When this record was created")
    updated_at: Optional[datetime] = Field(None, description="When this record was last updated")
    name: Optional[str] = Field(None, description="The name of the category")
    description: Optional[str] = Field(None, description="The description of the category")
    locale: Optional[str] = Field(None, description="The locale of the category")
    source_locale: Optional[str] = Field(None, description="The source (default) locale of the category")
    outdated: Optional[bool] = Field(None, description="Whether the category is outdated")


class Section(ZendeskModel):
    """Help Center Section model.

    Sections belong to Categories and contain Articles.
    """

    id: Optional[int] = Field(None, description="Automatically assigned when created")
    url: Optional[str] = Field(None, description="The API url of this section")
    html_url: Optional[str] = Field(None, description="The url of this section in Help Center")
    category_id: Optional[int] = Field(None, description="The id of the category this section belongs to")
    position: Optional[int] = Field(None, description="The position of this section relative to others")
    sorting: Optional[str] = Field(None, description="The sorting method for articles in this section")
    created_at: Optional[datetime] = Field(None, description="When this record was created")
    updated_at: Optional[datetime] = Field(None, description="When this record was last updated")
    name: Optional[str] = Field(None, description="The name of the section")
    description: Optional[str] = Field(None, description="The description of the section")
    locale: Optional[str] = Field(None, description="The locale of the section")
    source_locale: Optional[str] = Field(None, description="The source (default) locale of the section")
    outdated: Optional[bool] = Field(None, description="Whether the section is outdated")
    parent_section_id: Optional[int] = Field(None, description="The id of the parent section (Enterprise only)")
    theme_template: Optional[str] = Field(None, description="The theme template name for the section")


class Article(ZendeskModel):
    """Help Center Article model.

    Articles are the content items in Help Center.
    They belong to Sections and contain the actual help content.
    """

    id: Optional[int] = Field(None, description="Automatically assigned when created")
    url: Optional[str] = Field(None, description="The API url of this article")
    html_url: Optional[str] = Field(None, description="The url of this article in Help Center")
    author_id: Optional[int] = Field(None, description="The id of the user who wrote the article")
    comments_disabled: Optional[bool] = Field(None, description="True if comments are disabled")
    draft: Optional[bool] = Field(None, description="True if the article is a draft")
    promoted: Optional[bool] = Field(None, description="True if the article is promoted")
    position: Optional[int] = Field(None, description="The position of this article relative to others")
    vote_sum: Optional[int] = Field(None, description="The sum of votes on this article")
    vote_count: Optional[int] = Field(None, description="The total number of votes on this article")
    section_id: Optional[int] = Field(None, description="The id of the section this article belongs to")
    created_at: Optional[datetime] = Field(None, description="When this record was created")
    updated_at: Optional[datetime] = Field(None, description="When this record was last updated")
    edited_at: Optional[datetime] = Field(None, description="When the article was last edited")
    name: Optional[str] = Field(None, description="The title of the article (alias for title)")
    title: Optional[str] = Field(None, description="The title of the article")
    body: Optional[str] = Field(None, description="The body of the article in HTML")
    source_locale: Optional[str] = Field(None, description="The source (default) locale of the article")
    locale: Optional[str] = Field(None, description="The locale of the article")
    outdated: Optional[bool] = Field(None, description="Whether the article translation is outdated")
    permission_group_id: Optional[int] = Field(None, description="The id of the permission group")
    user_segment_id: Optional[int] = Field(None, description="The id of the user segment")
    user_segment_ids: Optional[List[int]] = Field(None, description="The ids of user segments")
    label_names: Optional[List[str]] = Field(None, description="The list of labels for the article")
    content_tag_ids: Optional[List[str]] = Field(None, description="The list of content tag ids")
    # Search-specific fields
    result_type: Optional[str] = Field(None, description="Result type in search results (always 'article')")
    snippet: Optional[str] = Field(None, description="Matching snippet in search results with <em> tags")
