from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type, cast

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, model_validator

from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.click import ClickElementTool
from langchain_community.tools.drissionpage.get_elements import GetElementsTool
from langchain_community.tools.drissionpage.listen_network import ListenNetworkTool
from langchain_community.tools.drissionpage.screenshot import ScreenshotTool

# Import Chromium directly to avoid the need for forward references
from DrissionPage import Chromium


class DrissionBrowserToolkit(BaseToolkit):
    """Toolkit for DrissionPage browser tools."""

    browser: Optional[Chromium] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_browser_provided(cls, values: dict) -> Any:
        """Check that the arguments are valid."""
        if values.get("browser") is None:
            raise ValueError("A Chromium browser instance must be provided.")
        return values

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        tool_classes: List[Type[BaseBrowserTool]] = [
            ClickElementTool,
            GetElementsTool,
            ListenNetworkTool,
            ScreenshotTool,
        ]

        # Instantiate each tool with the shared browser instance
        tools = [tool_cls.from_browser(browser=self.browser) for tool_cls in tool_classes]
        return cast(List[BaseTool], tools)

    @classmethod
    def from_browser(cls, browser: Optional[Chromium] = None) -> DrissionBrowserToolkit:
        """Instantiate the toolkit with a DrissionPage browser.

        Args:
            browser: The DrissionPage Chromium browser instance.

        Returns:
            The toolkit.
        """
        if browser is None:
            raise ValueError("A DrissionPage browser instance is required.")
        return cls(browser=browser)


# Rebuild the model to ensure Pydantic resolves any forward references
DrissionBrowserToolkit.model_rebuild()
