import copy

import playwright.sync_api
from playwright.sync_api import Playwright, Page

from logger import *

lazy import Oracle.web as o_web
lazy import Oracle.nav as nav


class Engine:
    def __init__(self,
                 browser: playwright.sync_api.Browser,
                 context: playwright.sync_api.BrowserContext,
                 pw: Playwright
                 ):
        self.browser: playwright.sync_api.Browser = browser
        self.context: playwright.sync_api.BrowserContext = context
        self.pw: Playwright = pw
        self.pages: list[playwright.sync_api.Page] = []


def new_work_order(engine: Engine, _info: o_web.WorkOrder.BaseInformation):
    # Navigates to the manage work orders page
    page: Page = nav.goto_manage_work_orders(engine)

    # Extensively commented to allow for patching if the UI changes
    def sequence():
        nonlocal page

        # There are two "Create" images. The "last" one (second one) is the dropdown arrow
        page.get_by_role("img", name="Create", exact=True).last.click()
        page.get_by_text(f"Create {_info.work_order_type.value} Work Order", exact=True).click()

        # Scopes to the popup window to avoid selecting locators on the Manage Work Orders page
        popup = page.locator("#__af_Z_window")

        # Expands the additional details to allow for manual work-order input
        popup.get_by_text("Show More", exact=True).click()

        # Populates the work order field
        work_order_textbox = popup.get_by_role("textbox", name="Work Order", exact=True)
        work_order_textbox.click()
        work_order_textbox.fill(_info.work_order_id)

        # Enters the item search menu
        item_search_combobox = popup.get_by_role("img", name="Search: Item", exact=True)
        item_search_combobox.click()

        # Populates the search field
        # The 'keyword' field allows for exact-match searches
        item_keyword_textbox = popup.get_by_role("textbox", name="Keyword", exact=True)
        item_keyword_textbox.click()
        item_keyword_textbox.fill(f"\"{_info.part}\" within itemcode")

        # Presses the search button on the 'search item' popup
        popup.get_by_role("button", name="Search", exact=True).click()
        # Locates the "cell" (item) that pops up. With exact match (keyword), there should only be one
        item_cell = popup.get_by_role("cell", name=_info.part, exact=True)

        try:
            # Tries to select the item (fails if there are 0 matches)
            item_cell.first.click()
            # Confirms the item
            popup.get_by_role("button", name="OK", exact=True).click()
        except Exception as e:
            log(f"P/N {_info.part} could not be found. Are you sure it was typed correctly?\nException: {e}",
                LogLevel.WARN)
            return False

        # Waiting is necessary, since the popup refreshes some time after confirming an item and ...
        # ... will discard any changes made between confirmation and refreshing
        page.wait_for_load_state("networkidle")

        # Populates the supply subinventory with rework by default
        # If orders need to grab from a different subinventory, this can be added
        # Alternatively, this tool should not be used in that case
        supply_subinventory_combobox = popup.get_by_role("combobox", name="Supply Subinventory", exact=True)
        supply_subinventory_combobox.click()
        supply_subinventory_combobox.fill("REWORK")

        # Populates the quantity
        quantity_textbox = popup.get_by_role("textbox", name="Quantity", exact=True)
        quantity_textbox.click()
        quantity_textbox.fill(str(_info.quantity))

        # Waits for all fields to settle
        page.wait_for_load_state("networkidle")

        # Creates the work order and returns to the Manage Work Orders screen.
        popup.get_by_role("button", name="Save and Close", exact=True).click()

        return True
    return sequence()
