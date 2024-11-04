from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Type, List, Union

from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field

from langchain_community.tools.drissionpage.base import BaseBrowserTool
from langchain_community.tools.drissionpage.utils import get_current_tab
from DrissionPage._units.listener import DataPacket
if TYPE_CHECKING:
    from DrissionPage._units.listener import DataPacket


class ListenNetworkToolInput(BaseModel):
    """Input Schema for ListenNetwork Tool"""
    url_pattern: str = Field(
        ...,
        description=(
            "URL pattern to listen for in network requests. "
            "Supports exact matches or substrings to match multiple URLs."
        )
    )
    page_url: str = Field(
        ...,
        description="URL of the page to navigate to before listening to network packets."
    )
    timeout: Optional[float] = Field(
        default=10.0,
        description="Maximum time in seconds to wait for matching network requests."
    )
    count: int = Field(
        default=1,
        description="Number of network packets to capture."
    )


class ListenNetworkTool(BaseBrowserTool):
    """Tool to navigate to a page and listen to network packets matching a specific URL pattern."""

    name: str = "listen_network"
    description: str = (
        "Navigates to a specified page, listens to network packets matching a specific URL pattern, "
        "and captures their details."
    )
    args_schema: Type[BaseModel] = ListenNetworkToolInput

    def _run(
        self,
        url_pattern: str,
        page_url: str,
        timeout: Optional[float] = 10.0,
        count: int = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the tool synchronously."""
        if self.browser is None:
            raise ValueError(f"Browser not provided to {self.name}")
        
        tab = get_current_tab(self.browser)
        
        # Navigate to the specified page URL
        tab.get(page_url)
        
        # Start listening for network packets matching the given URL pattern
        tab.listen.start(url_pattern)
        
        # Wait for the specified number of matching packets
        packets = tab.listen.wait(count=count, timeout=timeout)
        
        # If a single packet is returned, wrap it in a list for consistent processing
        if isinstance(packets, DataPacket):
            packets = [packets]
        
        if not packets:
            return json.dumps({'error': f'No matching network packets found within {timeout} seconds'})
        
        # Process and store information for each captured packet
        packets_info = []
        for packet in packets:
            packet_info = {
                "tab_id": packet.tab_id,
                "frameId": packet.frameId,
                "target": packet.target,
                "url": packet.url,
                "method": packet.method,
                "is_failed": packet.is_failed,
                "resourceType": packet.resourceType,
                "request": {
                    "url": packet.request.url,
                    "method": packet.request.method,
                    "params": packet.request.params,
                    "headers": packet.request.headers,
                    "cookies": packet.request.cookies,
                    "postData": packet.request.postData,
                },
                "response": {
                    "url": packet.response.url if packet.response else None,
                    "headers": packet.response.headers if packet.response else None,
                    "body": packet.response.body if packet.response else None,
                    "raw_body": packet.response.raw_body if packet.response else None,
                    "status": packet.response.status if packet.response else None,
                    "statusText": packet.response.statusText if packet.response else None,
                },
            }
            
            # Optionally wait for extra information if available
            if hasattr(packet, 'wait_extra_info'):
                packet.wait_extra_info(timeout=timeout)
            
            packets_info.append(packet_info)
        
        return json.dumps(packets_info, ensure_ascii=False, default=str)
