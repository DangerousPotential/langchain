from __future__ import annotations
from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.utils import get_current_tab, close_drission_browser, create_drission_browser
from typing import TYPE_CHECKING, Optional, Tuple, Union, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.utils import get_current_tab

if TYPE_CHECKING:
    from DrissionPage import Chromium


class ScreenshotToolInput(BaseModel):
    """Input schema for ScreenshotTool."""

    page_url: str = Field(
        ...,
        description="URL of the page to navigate to before taking a screenshot."
    )
    path: Optional[str] = Field(
        default="screenshot.png",
        description="Path to save the screenshot file. If not provided, defaults to 'screenshot.png'."
    )
    full_page: bool = Field(
        default=False,
        description="If set to True, captures the entire page. Defaults to False (visible portion only)."
    )
    element_selector: Optional[str] = Field(
        default=None,
        description=(
            "CSS selector for a specific element to capture. "
            "If provided, only this element will be captured."
        )
    )
    area: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = Field(
        default=None,
        description=(
            "Coordinates for capturing a specific area of the page. "
            "Format: ((left, top), (right, bottom)). Ignored if 'element_selector' is provided."
        )
    )
    as_bytes: bool = Field(
        default=False,
        description="If set to True, returns the screenshot as bytes instead of saving to a file."
    )
    as_base64: bool = Field(
        default=False,
        description="If set to True, returns the screenshot as a base64-encoded string."
    )


class ScreenshotTool(BaseBrowserTool):
    """Tool to take screenshots of a webpage, specific element, or custom area."""

    name: str = "screenshot_tool"
    description: str = (
        "Takes a screenshot of a webpage or specific part of it. Can capture the full page, "
        "a specific element, or a defined area."
    )
    args_schema: Type[BaseModel] = ScreenshotToolInput

    def _run(
        self,
        page_url: str,
        path: Optional[str] = "screenshot.png",
        full_page: bool = False,
        element_selector: Optional[str] = None,
        area: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None,
        as_bytes: bool = False,
        as_base64: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Union[str, bytes]:
        """Execute the screenshot tool synchronously."""
        if self.browser is None:
            raise ValueError(f"Browser not provided to {self.name}")
        
        tab = get_current_tab(self.browser)
        
        # Navigate to the specified page URL
        tab.get(page_url)
        
        # Determine screenshot target based on input parameters
        if element_selector:
            # Capture a specific element
            element = tab.ele(element_selector)
            if not element:
                raise ValueError(f"Element with selector '{element_selector}' not found.")
            result = element.get_screenshot(
                path=path,
                as_bytes=as_bytes,
                as_base64=as_base64
            )
        elif area:
            # Capture a specific area
            left_top, right_bottom = area
            result = tab.get_screenshot(
                path=path,
                as_bytes=as_bytes,
                as_base64=as_base64,
                left_top=left_top,
                right_bottom=right_bottom
            )
        else:
            # Capture the full page or visible portion
            result = tab.get_screenshot(
                path=path,
                full_page=full_page,
                as_bytes=as_bytes,
                as_base64=as_base64
            )
        
        # If as_bytes or as_base64 is True, return the result directly; otherwise, return the file path
        if as_bytes or as_base64:
            return result
        return f"Screenshot saved at {path}"
