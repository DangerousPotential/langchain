from DrissionPage import Chromium, ChromiumOptions
from typing import Optional, Dict, Any
def create_drission_browser(
    headless: bool = True,
    browser_path: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Chromium:
    """
    Create a DrissionPage Chromium browser instance.

    Args:
        headless: Whether to run the browser in headless mode. Defaults to True.
        browser_path: Path to the Chromium executable.
        options: Additional options for configuring ChromiumOptions.

    Returns:
        Chromium: The DrissionPage Chromium browser instance.
    """
    chromium_options = ChromiumOptions()
    chromium_options.headless = headless
    if browser_path:
        chromium_options.set_browser_path(browser_path)
    
    if options:
        for key, value in options.items():
            setattr(chromium_options, key, value)
    
    return Chromium(chromium_options)

def get_current_tab(browser: Chromium):
    """
    Get the current tab of the DrissionPage browser.

    Args:
        browser: The DrissionPage Chromium browser instance.

    Returns:
        Tab: The current tab of the browser.
    """
    if not browser.latest_tab:
        return browser.new_tab()
    return browser.latest_tab

def close_drission_browser(browser: Chromium):
    """
    Close the DrissionPage Chromium browser.

    Args:
        browser: The DrissionPage Chromium browser instance.
    """
    if browser:
        browser.quit()
