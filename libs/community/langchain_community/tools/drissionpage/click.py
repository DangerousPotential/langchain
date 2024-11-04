from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Type

from langchain_core.callbacks import (
    CallbackManagerForToolRun
)

from pydantic import BaseModel, Field

from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.utils import get_current_tab

if TYPE_CHECKING:
    from DrissionPage import Chromium, ChromiumPage, ChromiumElement

class ClickElementToolInput(BaseModel): # type: ignore[override]
    """Input Schema for ClickElementTool."""
    selector: str = Field(
        ...,
        description=(
            "Learn the syntax at: https://drissionpage.cn/browser_control/get_elements/sheet "
            "Selector to locate the element to click. "
            "Supports DrissionPage's syntactic sugar for locating elements, including:\n"
            "- CSS selector syntax (e.g., 'css:div.classname', 'css:#id')\n"
            "- ID shortcut: '#id'\n"
            "- Class shortcut: '.classname'\n"
            "- Tag and class: 'div.classname'\n"
            "- Text shortcut: 'text:Exact Text' or 'text:Contains Text'\n"
            "- Attribute shortcut: '@attribute=value' (e.g., '@name=example')\n"
            "- Multiple attribute conditions: '@@class=classname@@id=element_id'\n"
            "Use these shortcuts to quickly locate elements based on ID, class, text content, "
            "or specific attributes."
        ),
    )
    by_js: Optional[bool] = Field(
        default = None,
        description=(
            "Whether to use JavaScript to perform the click action"
            "If set to `None`, the tool will decide the best method based on the element state"
            "If set to `True`, the tool will use JavaScript to perform the click action"
            "If set to `False`, a simulated click will be attempted"
        )
    )
    timeout: Optional[float] = Field(
        default = 1.5,
        description= "Timeout in seconds to wait for the elements to be clickbale"
    )

class ClickElementTool(BaseBrowserTool):
    """Tool for clicking an element on the current web page"""
    name: str = "click_element"
    description: str = (
        "Click an element on the current web page identified by the given selector"
    )
    args_schema: Type[BaseModel] = ClickElementToolInput

    def _run(
        self,
        selector: str,
        by_js: Optional[bool] = None,
        timeout: Optional[float] = 1.5,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the tool synchronously"""
        if self.browser is None:
            raise ValueError(f"Browser is not provided to {self.name}")
        tab = get_current_tab(self.browser)
        element: Optional[ChromiumElement] = tab.ele(selector)
        if element is None:
            raise ValueError(f"Element not found with selector: {selector}")
        success = element.click(by_js = by_js, timeout = timeout)
        return "Click action successful!" if success else "Click action failed"