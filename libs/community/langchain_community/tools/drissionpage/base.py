from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Dict, Type

from langchain_core.tools import BaseTool
from langchain_core.utils import guard_import
from pydantic import model_validator

if TYPE_CHECKING:
    from DrissionPage import Chromium, ChromiumOptions
else:
    try:
        from DrissionPage import Chromium, ChromiumOptions
    except ImportError:
        Chromium = None
        ChromiumOptions = None

def lazy_import_drissionpage() -> Type[Chromium]:
    """
    Lazy import DrissionPage Chromium class.
    """
    if Chromium is None or ChromiumOptions is None:
        raise ImportError("DrissionPage is not installed.")
    return guard_import(module_name="DrissionPage").Chromium

class BaseBrowserTool(BaseTool):  # type: ignore[override]
    """Base class for browser tools using DrissionPage's Chromium interface."""

    browser: Optional[Chromium] = None
    browser_options: Dict[str, Any] = {}

    @model_validator(mode="before")
    @classmethod
    def validate_browser_options(cls, values: dict) -> Any:
        """Validator to ensure a Chromium instance is created or provided."""
        lazy_import_drissionpage()
        browser = values.get("browser")
        browser_options = values.get("browser_options", {})

        if browser is None:
            options = ChromiumOptions()
            options.headless = browser_options.get("headless", True)
            if "browser_path" in browser_options:
                options.set_browser_path(browser_options["browser_path"])
            values["browser"] = Chromium(options)
        elif not isinstance(browser, Chromium):
            raise ValueError("browser must be a Chromium instance.")
        
        return values

    @classmethod
    def from_browser(
        cls,
        name: str = 'Drission Tool',
        description: str = 'A tool for interacting with Drission browser',
        browser: Optional[Chromium] = None,
        browser_options: Optional[Dict[str, Any]] = None,
    ) -> BaseBrowserTool:
        """Instantiate the tool with required name and description."""
        lazy_import_drissionpage()
        return cls(
            name= name,
            description=description,
            browser=browser,
            browser_options=browser_options or {}
        )

    def get_current_tab(self):
        """Get the current tab of the browser."""
        if self.browser is None:
            raise ValueError("Browser is not initialized.")
        return self.browser.latest_tab

    def close_browser(self):
        """Close the browser."""
        if self.browser:
            self.browser.quit()
            self.browser = None

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Synchronous execution method to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the _run method.")
