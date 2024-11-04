from __future__ import annotations

import json
from typing import TYPE_CHECKING, List, Optional, Sequence, Type, Any

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.utils import (
    get_current_tab,
)

if TYPE_CHECKING:
    from DrissionPage import ChromiumElement


class GetElementsToolInput(BaseModel):
    """Input schema for GetElementsTool."""

    selector: str = Field(
        ...,
        description=(
            "CSS selector or DrissionPage syntactic sugar for locating elements. "
            "Supported formats include:\n"
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
    attributes: List[str] = Field(
        default_factory=lambda: ["text"],
        description=(
            "List of attributes to retrieve for each element. "
            "Supported attributes include 'text', 'html', 'inner_html', 'tag', 'attrs', "
            "and any specific attribute like 'id', 'class', etc."
        ),
    )
    preview_attributes: bool = Field(
        default=False,
        description="If set to True, display all available attributes for each element instead of specific ones."
    )


def _get_elements(
    tab: Any, selector: str, attributes: Sequence[str], preview_attributes: bool = False
) -> List[dict]:
    """Retrieve elements matching the given CSS selector and extract specified attributes."""
    elements = tab.eles(f'{selector}')
    results = []
    for element in elements:
        result = {}
        
        # If preview_attributes is True, show all attributes
        if preview_attributes:
            result = element.attrs    
        else:
            for attribute in attributes:
                if attribute == "text":
                    val: Optional[str] = element.text
                elif attribute == "html":
                    val = element.html
                elif attribute == "inner_html":
                    val = element.inner_html
                elif attribute == "tag":
                    val = element.tag
                elif attribute == "attrs":
                    val = element.attrs
                else:
                    val = element.attr(attribute)
                
                # Only add non-empty and non-null attributes
                if val is not None and (isinstance(val, str) and val.strip() != "" or isinstance(val, dict) and val):
                    result[attribute] = val

        if result:
            results.append(result)
    return results


class GetElementsTool(BaseBrowserTool):  # type: ignore[override]
    """Tool for retrieving elements in the current web page matching a CSS selector."""

    name: str = "get_elements"
    description: str = (
        "Retrieve elements in the current web page matching the given CSS selector and extract specified attributes. "
        "Set 'preview_attributes' to True to view all available attributes for each element before selecting specific ones."
    )
    args_schema: Type[BaseModel] = GetElementsToolInput

    def _run(
        self,
        selector: str,
        attributes: Sequence[str] = ["text"],
        preview_attributes: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool synchronously."""
        if self.browser is None:
            raise ValueError(f"Browser not provided to {self.name}")
        tab = get_current_tab(self.browser)
        # Ensure navigation to the desired webpage before using this tool
        results = _get_elements(tab, selector, attributes, preview_attributes)
        return json.dumps(results, ensure_ascii=False)
