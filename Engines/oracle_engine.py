import playwright
from playwright.sync_api import sync_playwright, Playwright

import Oracle.web
import utils
import Oracle.web as o_web
import Oracle.interface as o_api
import Oracle.nav as nav
from Oracle.web import WorkOrder

from main import ORACLE_HOST, PROFILE_DIR, AUTH_STATE, LOGIN_URL
from logger import *

engine: o_api.Engine = None

def block_unneeded_resources(route):
    if route.request.resource_type in {"image", "font"}:
        route.abort()
    else:
        route.continue_()

def get_label(page, label_text):
    label = page.locator("label").get_by_text(
        label_text, exact=True
    ).first

    if label.count() == 0:
        return "N/A"

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

    return "N/A" if utils.is_null_or_whitespace(result) else result

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


def prompt_login():
    log("Prompting user login...", LogLevel.PENDING)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 720}
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(LOGIN_URL)

        # Wait for user to finish authentication.
        page.wait_for_url("**/fscmUI/faces/*", timeout=120000)

        if ORACLE_HOST not in page.url:
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
        viewport={"width": 720, "height": 450}
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

        _type = get_label(p, "Type")
        item = get_label(p, "Item")
        status = p.get_by_role('combobox', name="Status").input_value()
        description = get_label(p, "Description")
        qty = get_label(p, "Quantity").replace("EA", "").strip()
        start_date = get_label(p, "Start Date")
        end_date = get_label(p, "Completion Date")

        print(f"Fetching {status}"
              f"\n\tSample: CANCELED = {WorkOrder.Status.get("Canceled")}")
        return o_web.WorkOrder(wo_id, _type, item, int(qty), WorkOrder.Status.get(status), description, start_date, end_date)


def open_new():
    return nav.new_tab(engine)