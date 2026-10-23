import copy

import playwright.sync_api
from playwright.sync_api import Playwright, Page

from Engines import oracle_engine
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

WO = o_web.WorkOrder
class WorkOrderInterface:
    @staticmethod
    def get_work_order_page(work_order: WO|str, engine: Engine|None):
        oracle_engine.validate_api()
        if engine is None:
            engine = oracle_engine.engine
        assert engine is not None

        _id: str = work_order.base_information.work_order_id if isinstance(work_order, WO) else ("WO-SAU-" + work_order.replace("WO-SAU-", ""))

        return nav.get_saved_page(
            _id,
            lambda: nav.goto_work_order(nav.new_tab(engine), _id)
        )


    class BaseInformation:
        @staticmethod
        def set_quantity(work_order: WO, value: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            if work_order.general_information.status != WO.Status.UNRELEASED:
                log(f"Cannot change quantity when work order is {work_order.general_information.status.value}", LogLevel.WARN)
                return

            p.get_by_role("link", name="General Information", exact=True).click()
            quantity_texbox = p.get_by_role("textbox", name="Quantity", exact=True)
            quantity_texbox.click()
            quantity_texbox.fill(str(value))
            work_order.base_information.quantity = value

    class GeneralInformation:
        @staticmethod
        def set_status(work_order: WO, value: WO.Status):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            log("Setting a work order's status is not yet supported."
                     "\nWork order status should only be changed by the program if directed by a user, never automatically.",
                LogLevel.WARN)

        @staticmethod
        def set_description(work_order: WO, value: str):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)

            p.get_by_role("link", name="General Information", exact=True).click()
            description_textbox = p.get_by_role("textbox", name="Description", exact=True)
            description_textbox.click()
            description_textbox.fill(value)
            work_order.general_information.description = value


        @staticmethod
        def set_priority(work_order: WO, value: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)

            p.get_by_role("link", name="General Information", exact=True).click()
            priority_textbox = p.get_by_role("textbox", name="Priority", exact=True)
            priority_textbox.click()
            priority_textbox.fill(str(value))
            work_order.general_information.priority = value

        @staticmethod
        def set_start_date(work_order: WO, value: o_web.Date):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)

            p.get_by_role("link", name="General Information", exact=True).click()
            start_date_textbox = p.get_by_role("textbox", name="Start Date", exact=True)
            start_date_textbox.click()
            start_date_textbox.fill(value.value)
            work_order.general_information.start_date = value

        @staticmethod
        def set_end_date(work_order: WO, value: o_web.Date):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)

            p.get_by_role("link", name="General Information", exact=True).click()
            end_date_textbox = p.get_by_role("textbox", name="Completion Date", exact=True)
            end_date_textbox.click()
            end_date_textbox.fill(value.value)
            work_order.general_information.start_date = value

    class Operations:

        class Operation:
            class SupplierDetails:
                @staticmethod
                def set_osp_item(work_order: WO, value: str):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)


                @staticmethod
                def set_supplier(work_order: WO, value: str):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

                @staticmethod
                def set_generate_shipment(work_order: WO, value: bool):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

                @staticmethod
                def set_lead_time(work_order: WO, value: float|int):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

            class Item:
                @staticmethod
                def set_is_fixed(work_order: WO, op: int, item: WO.Item|str, value: bool):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    pass

                @staticmethod
                def set_quantity(work_order: WO, op: int, item: WO.Item|str, value: int):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    pass

            class Resource:
                @staticmethod
                def set_is_fixed(work_order: WO, op: int, resource: WO.Resource|str, value: bool):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    pass

                @staticmethod
                def set_usage_rate(work_order: WO, op: int, resource: WO.Resource|str, value: float):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    pass

            @staticmethod
            def set_name(work_order: WO|str, op: int, value: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order, None)

                p.wait_for_load_state("networkidle")

                p.get_by_role("link", name="Operations", exact=False).click()

                p.wait_for_timeout(1000)
                playwright.sync_api.expect(p.get_by_text("Operation Yield", exact=True)).to_be_visible()

                # Only the operations panel has _afrtotalrows on this page, and the panel is the only class child.
                operations_panel = p.locator('div[_afrtotalrows]')
                log(f"Matched for {operations_panel.count()} panels.")

                log(f"There are {operations_panel.locator("> *").count()} operations.")

            @staticmethod
            def set_work_instruction(work_order: WO, op: int, value: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                pass

            @staticmethod
            def add_item(work_order: WO, op: int, value: WO.Item):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                pass

            @staticmethod
            def remove_item(work_order: WO, op: int, value: WO.Item|str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                pass

            @staticmethod
            def add_resource(work_order: WO, op: int, value: WO.Resource):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                pass

            @staticmethod
            def remove_resource(work_order: WO, op: int, resource_name: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                pass


        @staticmethod
        def add_operation(work_order: WO, value: WO.Operation):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            pass

        @staticmethod
        def remove_operation(work_order: WO, op: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            pass

    class Lots:
        @staticmethod
        def set_lot(work_order: WO, lot: str, quantity: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            # !!! Update description after all changes !!!

            """
            if lot not exists:
                if quantity == 0:
                    # Not a change, don't update description.
                    return

                # Add lot with quantity
                    Return
            """

            if quantity == 0:
                # Remove
                return

            """
            (IF LOT EXISTS & QUANTITY > 0)
            
            # Fetch lot and change quantity
            
            """



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
