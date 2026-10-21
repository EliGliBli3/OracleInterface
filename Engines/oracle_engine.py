import playwright
from playwright.sync_api import sync_playwright, Playwright

import Oracle.web
import utils
import Oracle.web as o_web
import Oracle.interface as o_api
import Oracle.nav as nav
from Oracle.interface import new_work_order
from Oracle.web import WorkOrder

from main import PROFILE_DIR, AUTH_STATE, ORACLE_HOST, ORACLE_TEST_HOST
from logger import *

engine: o_api.Engine = None

def block_unneeded_resources(route):
    if route.request.resource_type in {"image", "font"}:
        route.abort()
    else:
        route.continue_()

def get_label(page, label_text, return_none: bool = False):
    label = page.locator("label").get_by_text(
        label_text, exact=True
    ).first

    def return_na():
        return None if return_none else "N/A"

    if label.count() == 0:
        return return_na()

    row = label.locator("xpath=ancestor::tr[1]")
    # Generically 2 cells: (0) Label, (1) Value
    cells = row.locator(":scope > td")

    value_cell = cells.nth(1)
    inputs = value_cell.locator("input:not([type='hidden'])")

    result = None

    # Some values have multiple inputs (e.g. Quantity has qty + UoM)
    if inputs.count() > 0:
        # Dumps playwright locator list ('inputs') into a value array
        values = [
            inputs.nth(i).input_value().strip()
            for i in range(inputs.count())
        ]
        # Remove null values
        values = [value for value in values if value]

        # Would only return 'false' if *every* value was null, and was culled in the previous operation.
        if values and len(values) > 0:
            result = " ".join(values)

    if not result:
        result = value_cell.inner_text().strip()

    return return_na() if utils.is_null_or_whitespace(result) else result

def validate_api():
    if engine is None:
        err_break("No engine was initialized. Call start_engine() before using the api.")
    if engine.pages is None:
        log("Engine pages were unexpectedly invalidated.", LogLevel.WARN)
        log("Revalidating engine page collection...", LogLevel.PENDING)
        engine.pages = []
    if len(engine.pages) == 0:
        log("Revalidating main page...", LogLevel.PENDING)
        engine.pages.append(engine.context.new_page())


def prompt_login(test_environment: bool):
    login_url = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"
    if test_environment:
        log("\n!!!!!\nPROGRAM IS LAUNCHING IN THE ORACLE TEST ENVIRONMENT.\nCHANGES WILL NOT BE PUSHED TO PRODUCTION.\n!!!!!", LogLevel.WARN)
        main.test_environment = True
        login_url = f"{ORACLE_TEST_HOST}/fscmUI/faces/FuseWelcome"

    log("Prompting user login...", LogLevel.PENDING)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 720}
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(login_url)

        if test_environment:
            okta_button = page.get_by_role("img", name="Okta")
            okta_button.click()

        # Wait for user to finish authentication.
        page.wait_for_url("**/fscmUI/faces/*", timeout=120000)

        if (ORACLE_TEST_HOST if test_environment else ORACLE_HOST) not in page.url:
            err_break(f"Oracle is not loaded. Current URL: {page.url}")

        context.storage_state(path=str(AUTH_STATE))
        log("User login complete.", LogLevel.SUCCESS)

        context.close()

def start_engine():
    global engine

    log("Starting browser engine...", LogLevel.PENDING)
    if not AUTH_STATE.exists():
        err_break("run_login() was not fully executed before engine start.")

    pw: Playwright = sync_playwright().start()
    log("Playwright engine started.")
    browser = pw.chromium.launch(headless=False)
    log("Browser launched.")
    context = browser.new_context(
        storage_state=str(AUTH_STATE),
        viewport={"width": int(1920/2), "height": int(1080/2)}
    )
    engine = o_api.Engine(browser, context, pw)
    engine.pages = [engine.context.new_page()]
    log("Engine initialized.", LogLevel.SUCCESS)

def dispose():
    if engine is not None:
        engine.context.close()
        engine.browser.close()
        engine.pw.stop()

def get_work_order(wo_id: str):
    validate_api()

    p: playwright.sync_api.Page
    with nav.new_tab(engine) as p:
        nav.goto_work_order(p, wo_id)

        p.wait_for_load_state("networkidle")

        if p.get_by_text("Type", exact=True).count() == 0:
            def attempt_expand_details():

                if p.get_by_role("button", name="Collapse Details",exact=True).count() > 0:
                    print("Found evidence of expansion... moving forward")
                    return True
                try:
                    # Expand details so that they can be read
                    p.get_by_role("button", name="Expand Details").click()

                    return True
                except Exception as e:
                    print(e)
                    return False

            timeout_attempts = 5
            passed = False

            for _ in range(timeout_attempts):
                if attempt_expand_details():
                    passed = True
                    break
            if not passed:
                raise TimeoutError(f"Could not expand details (Timed out after {timeout_attempts} attempts.)")

        _type = get_label(p, "Type", return_none=True)
        item = get_label(p, "Item")
        status = p.get_by_role('combobox', name="Status").input_value()
        description = p.get_by_role('textbox', name="Description").input_value()
        qty = get_label(p, "Quantity").replace("EA", "").strip()
        start_date = get_label(p, "Start Date")
        end_date = get_label(p, "Completion Date")

        _timeout = datetime.now()
        while _type is None:
            if (datetime.now() - _timeout).total_seconds() > 5:
                err_break(f"Timeout! Couldn't fetch type for WO-SAU-{wo_id}. Maybe the details pane didn't expand?")

            _type = get_label(p, "Type", return_none=True)

        # TODO: FIX WORK ORDER CONSTRUCTION TO MATCH NEW STRUCTURE
        return True #o_web.WorkOrder(wo_id, _type, item, int(qty), WorkOrder.Status.get(status), description, start_date, end_date)

def get_quality_issue(nc_num: str):
    validate_api()

    nav.goto_quality_issue(engine, nc_num)

def create_work_order(work_order: WorkOrder|None):
    validate_api()

    """
    1. Create Work Order (manage work orders)
    2. Go to Work Order separately
    3. Fill in details as necessary
    4. DO NOT RELEASE (Await user confirmation)
    """

    new_work_order(engine, WorkOrder.BaseInformation(
        _id="WO-SAU-TEST123",
        _quantity=5,
        _part="03-33-1565-003",
        _type=WorkOrder.Type.REWORK
    ))

def open_new():
    return nav.new_tab(engine)