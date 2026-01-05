"""Attachments API client."""

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from ..config import ZendeskConfig
    from ..http_client import HTTPClient


class AttachmentsClient:
    """Client for Zendesk Attachments API.

    Example:
        async with ZendeskClient(config) as client:
            # Download an attachment
            content = await client.attachments.download(attachment.content_url)
            with open("file.pdf", "wb") as f:
                f.write(content)

            # Upload a file
            with open("screenshot.png", "rb") as f:
                token = await client.attachments.upload(
                    f.read(),
                    "screenshot.png",
                    "image/png"
                )

            # Attach to a comment
            await client.tickets.comments.add(12345, "See attached", uploads=[token])
    """

    def __init__(self, http_client: "HTTPClient", config: "ZendeskConfig") -> None:
        """Initialize attachments client.

        Args:
            http_client: Shared HTTP client instance
            config: Zendesk configuration for auth
        """
        self._http = http_client
        self._config = config

    async def download(self, content_url: str) -> bytes:
        """Download attachment content from Zendesk.

        Zendesk attachment URLs require following redirects to access
        the actual file content.

        Args:
            content_url: The content_url from a CommentAttachment object

        Returns:
            Raw bytes of the attachment content

        Example:
            async for comment in client.tickets.comments.list(12345):
                for attachment in comment.attachments or []:
                    content = await client.attachments.download(attachment.content_url)
                    with open(attachment.file_name, "wb") as f:
                        f.write(content)
        """
        async with httpx.AsyncClient(follow_redirects=True) as http:
            response = await http.get(content_url)
            response.raise_for_status()
            return response.content

    async def upload(
        self,
        data: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file attachment to Zendesk.

        This uploads a file and returns a token that can be used when
        creating a ticket comment with attachments.

        Note: The token is valid for 60 minutes.

        Args:
            data: Raw bytes of the file content
            filename: Name for the uploaded file (include extension)
            content_type: MIME type of the file (default: application/octet-stream)

        Returns:
            Upload token to use with tickets.comments.add's uploads parameter

        Example:
            with open("screenshot.png", "rb") as f:
                token = await client.attachments.upload(
                    f.read(),
                    "screenshot.png",
                    "image/png"
                )

            await client.tickets.comments.add(
                ticket_id=12345,
                body="See attached screenshot",
                uploads=[token]
            )
        """
        url = f"{self._config.endpoint}/uploads.json"
        params = {"filename": filename}
        headers = {"Content-Type": content_type}

        auth = httpx.BasicAuth(
            username=self._config.auth_tuple[0],
            password=self._config.auth_tuple[1],
        )

        async with httpx.AsyncClient(auth=auth) as http:
            response = await http.post(url, params=params, headers=headers, content=data)
            response.raise_for_status()
            result = response.json()
            return result["upload"]["token"]
