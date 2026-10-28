import copy
import re
from selectors import SelectSelector

import playwright.sync_api
from playwright.sync_api import Playwright, Page

import logger
import utils
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
    def get_work_order_page(work_order: WO | str, engine: Engine | None = None):
        oracle_engine.validate_api()
        if engine is None:
            engine = oracle_engine.engine
        assert engine is not None

        _id: str = work_order.base_information.work_order_id if isinstance(work_order, WO) else (
                    "WO-SAU-" + work_order.replace("WO-SAU-", ""))

        return nav.get_saved_page(
            _id,
            lambda: nav.goto_work_order(nav.new_tab(engine), _id)
        )

    class BaseInformation:
        @staticmethod
        def set_quantity(work_order: WO, value: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            if work_order.general_information.status != WO.Status.UNRELEASED:
                log(f"Cannot change quantity when work order is {work_order.general_information.status.value}",
                    LogLevel.WARN)
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
                def set_lead_time(work_order: WO, value: float | int):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

            class Item:
                @staticmethod
                def set_is_fixed(work_order: WO, op: int, item: WO.Item | str, value: bool):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

                @staticmethod
                def set_quantity(work_order: WO, op: int, item: WO.Item | str, value: int):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

            class Resource:
                @staticmethod
                def set_is_fixed(work_order: WO, op: int, resource: WO.Resource | str, value: bool):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

                @staticmethod
                def set_usage_rate(work_order: WO, op: int, resource: WO.Resource | str, value: float):
                    p: Page = WorkOrderInterface.get_work_order_page(work_order)
                    log("This feature is not supported yet.", LogLevel.WARN)

            @staticmethod
            def set_name(work_order: WO | str, op: int, value: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order, None)
                log("This feature is not supported yet.", LogLevel.WARN)

                # p.wait_for_load_state("networkidle")
                #
                # p.get_by_role("link", name="Operations", exact=False).click()
                #
                # p.wait_for_timeout(1000)
                # playwright.sync_api.expect(p.get_by_text("Operation Yield", exact=True)).to_be_visible()

            @staticmethod
            def set_work_instruction(work_order: WO, op: int, value: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                log("This feature is not supported yet.", LogLevel.WARN)

            @staticmethod
            def add_item(work_order: WO, op: int, value: WO.Item):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                log("This feature is not supported yet.", LogLevel.WARN)

            @staticmethod
            def remove_item(work_order: WO, op: int, value: WO.Item | str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                log("This feature is not supported yet.", LogLevel.WARN)

            @staticmethod
            def add_resource(work_order: WO, op: int, value: WO.Resource):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                log("This feature is not supported yet.", LogLevel.WARN)

            @staticmethod
            def remove_resource(work_order: WO, op: int, resource_name: str):
                p: Page = WorkOrderInterface.get_work_order_page(work_order)
                log("This feature is not supported yet.", LogLevel.WARN)

        @staticmethod
        def add_operations(work_order: WO, values: list[WO.Operation]):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            if work_order.general_information.status != WO.Status.UNRELEASED:
                released_msg = \
                    f"Adding operations on released work orders is not yet supported." \
                        if work_order.general_information.status == WO.Status.RELEASED else \
                        f"Cannot add operations when work order is {work_order.general_information.status.value}."

                log(released_msg, LogLevel.WARN)
                return

            p.wait_for_load_state("networkidle")
            op_link = p.get_by_role("link", name="Operations", exact=False)
            op_link.click()
            playwright.sync_api.expect(op_link).to_have_class(re.compile(r"p_AFSelected"))

            p.get_by_role("img", name="Add Operations", exact=True).click()
            popup = p.locator('.AFPopupSelector')

            current_op = popup.locator('[class*="p_AFSelected"]')
            for i, value in enumerate(values):
                if i > 0:
                    popup.get_by_role("img", name="Add", exact=True).click()
                    (playwright.sync_api.expect(
                        current_op.get_by_role("combobox", name="Work Center", exact=True))
                     .to_have_value(""))

                if value.op != -1:
                    seq_textbox = current_op.get_by_role('textbox', name="Sequence", exact=True)
                    seq_textbox.click()
                    seq_textbox.fill(str(value.op))

                #TODO [Operation Type]

                # Code (str) OR Name/WorkCenter ((str, str))
                has_code = isinstance(value.code, str)
                if has_code:
                    code_textbox = current_op.get_by_role("combobox", name="Code", exact=True)
                    code_textbox.click()
                    code_textbox.fill(value.code)
                    code_textbox.press("Tab")
                else:
                    name_textbox = current_op.get_by_role("textbox", name="Name", exact=True)
                    name_textbox.click()
                    name_textbox.fill(value.code[0])

                    current_op.get_by_role("img", name="Work Center", exact=True).click()
                    p.get_by_role("link", name="Search...", exact=True).click()

                    search_popup = p.locator(".AFPopupSelector[id*='workCenter']")

                    search_popup.get_by_role("button", name="Advanced", exact=True).click()

                    p.wait_for_load_state("networkidle")

                    code_dropdown = search_popup.get_by_role("combobox", name="Code Operator", exact=True)
                    code_dropdown.select_option("Equals")

                    code_textbox = search_popup.get_by_role("textbox", name="Code", exact=True)
                    code_textbox.click()
                    code_textbox.fill(value.code[1])

                    search_popup.get_by_role("button", name="Search", exact=True).click()
                    search_popup.get_by_role("cell", name=value.code[1], exact=True).click()

                    search_popup.get_by_role("button", name="OK", exact=True).click()

                if not utils.is_null_or_whitespace(value.work_instruction):
                    current_op.get_by_role("img", name="Manage Attachments", exact=True).click()
                    # 'popup' now returns two elements

                    attachments_popup = popup.locator('[id*="attachments"]')

                    type_combobox = attachments_popup.get_by_role("combobox", name="Type", exact=True)
                    type_combobox.select_option("Text")

                    category_combobox = attachments_popup.get_by_role("combobox", name="Category", exact=True)
                    category_combobox.select_option("Work Instruction")

                    instruction_textbox = attachments_popup.get_by_role("textbox", name="File Name or URL", exact=True)
                    instruction_textbox.click()
                    instruction_textbox.fill(value.work_instruction)

                    title_textbox = attachments_popup.get_by_role("textbox", name="Title", exact=True)
                    title_textbox.click()
                    title_textbox.fill("Disposition")

                    attachments_popup.get_by_role("button", name="OK", exact=True).click()

                (playwright.sync_api.expect(
                    current_op.get_by_role("combobox", name="Work Center", exact=True))
                 .to_have_value(re.compile(r".+")))

            p.wait_for_load_state("networkidle")
            popup.get_by_role("button", name="OK", description="OK", exact=True).click()

        @staticmethod
        def remove_operation(work_order: WO, op_num: int):
            p: Page = WorkOrderInterface.get_work_order_page(work_order)
            if work_order.general_information.status != WO.Status.UNRELEASED:
                released_msg = \
                    f"Removing operations on released work orders is not yet supported." \
                        if work_order.general_information.status == WO.Status.RELEASED else \
                        f"Cannot remove operations when work order is {work_order.general_information.status.value}."

                log(released_msg, LogLevel.WARN)
                return

            p.wait_for_load_state("networkidle")
            op_link = p.get_by_role("link", name="Operations", exact=False)
            op_link.click()
            playwright.sync_api.expect(op_link).to_have_class(re.compile(r"p_AFSelected"))

            op_loc = p.locator('div[data-afrrk]')
            matched_op = None

            for i in range(op_loc.count()):
                i_op = op_loc.nth(i)
                title = i_op.get_attribute('title')

                if not title:
                    continue

                op_text = i_op.get_by_text(title).get_by_text(str(op_num))
                if op_text.count() != 0:
                    matched_op = i_op
                    break

            if not matched_op:
                log(f"Could not find operation #{op_num}!", LogLevel.WARN)
                return
            log(f"Found operation #{op_num} ({matched_op.get_attribute('title')})!")

            matched_op.click()
            p.get_by_role("img", name="Remove", exact=True).click()
            p.get_by_role("button", name="Yes", exact=True).click()

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


QI = o_web.QualityIssue


class QualityIssueInterface:

    @staticmethod
    def approve_issue(issue_id: int):
        oracle_engine.validate_api(); assert oracle_engine.engine is not None

        #TODO:
        #   - EDGE CASE: ISSUE APPROVED BUT STUCK IN APPROVAL
        #   - "SAVE AND CLOSE" INSTEAD OF CLOSING TAB
        #   - HOLD ISSUES THAT HAVE INDETERMINATE DATA

        p: Page = nav.goto_quality_issue(oracle_engine.engine, str(issue_id))

        log(f"Approving NC{issue_id}", LogLevel.PENDING)

        playwright.sync_api.expect(p.get_by_role("heading", name="General Information", exact=True)).to_be_visible()

        status = oracle_engine.get_label(p, "Status", True)
        if status is None:
            err_break("NC status returned NONE.")

        if status != "Approval":
            log("Cannot approve a quality issue unless it is in approval!", LogLevel.WARN)
            return

        p.get_by_role("button", name="Approve", exact=True).click()
        popup = p.locator('.AFPopupSelector')

        disposition = p.get_by_role("combobox", name="Disposition", exact=True).get_attribute('title')

        approval_message = "Miscellaneous Non-Conformance Issue Approval."
        match disposition:
            case "Dispose As Scrap":
                approval_message = "Scrapped."
            case "Rework to Specification":
                approval_message = "Rework Paperwork Complete."
            case "Use As Is":
                approval_message = "UAI per Engineering"
        approval_message += f"\n{logger.LOG_NAME}"

        approval_comment_textbox = popup.get_by_role("textbox", name="Comments", exact=True)
        approval_comment_textbox.click()
        approval_comment_textbox.fill(approval_message)

        popup.get_by_role("button", name="Approve", exact=True).click()
        #popup.get_by_role("button", name="Cancel", exact=True).click() # FOR TESTING

        issue_tab = p.locator('[class*="p_AFSelected"][id*="MainAreaTab"]')
        issue_tab.get_by_role("img", name="Close Tab", exact=True).click()

        log(f"Approved NC{issue_id}! ({disposition})", LogLevel.SUCCESS)


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

        # Populates the quantity
        quantity_textbox = popup.get_by_role("textbox", name="Quantity", exact=True)
        quantity_textbox.click()
        quantity_textbox.fill(str(_info.quantity))

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

        # Waits for all fields to settle
        page.wait_for_load_state("networkidle")

        # Creates the work order and returns to the Manage Work Orders screen.
        popup.get_by_role("button", name="Save and Close", exact=True).click()

        return True

    return sequence()
