from langchain_community.tools.drissionpage.utils import create_drission_browser, close_drission_browser
from langchain_community.agent_toolkits.drissionpage.toolkit import DrissionBrowserToolkit

# Create Browser Instance
browser = create_drission_browser(headless = True)

toolkit = DrissionBrowserToolkit.from_browser(browser = browser)

# Get all Tools
tools = toolkit.get_tools()


print(tools)
