from asyncio import timeout
from pathlib import Path

import playwright
from playwright.sync_api import sync_playwright, Playwright

import utils
import Oracle.web as o_web
import Oracle.interface as o_api

AUTH_STATE = Path("./oracle_auth_state.json")
PROFILE_DIR = "./oracle_cookies"
ORACLE_HOST = "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
LOGIN_URL = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"

engine: o_api.Engine = None

def get_deeplink(org_code: str, _type: o_web.DeeplinkObjType, action: o_web.DeeplinkAction, params: dict):
    url = (
        f"{ORACLE_HOST}/fscmUI/faces/deeplink"
        f"?objType={_type.value}&action={action.value}"
        f"&objKey=organizationCode={org_code}"
    )
    for param in params:
        url += f";{param}={params.get(param)}"

    return url

def block_unneeded_resources(route):
    if route.request.resource_type in {"image", "font"}:
        route.abort()
    else:
        route.continue_()

def get_field(page, label_text):
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
        raise RuntimeError("No engine was initialized. Call start_engine() before using the api.")
    if engine.page is None:
        print("Engine page was unexpectedly invalidated. Revalidating...")
        engine.page = engine.context.new_page()


def prompt_login():
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
            raise RuntimeError(
                f"Oracle is not loaded. Current URL: {page.url}"
            )

        context.storage_state(path=str(AUTH_STATE))
        print("Saved playwright authentication state.")

        context.close()

def start_engine():
    global engine

    if not AUTH_STATE.exists():
        raise RuntimeError("run_login() was not fully executed before engine start.")

    pw: Playwright = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=str(AUTH_STATE),
        viewport={"width": 720, "height": 450}
    )
    engine = o_api.Engine(browser, context, pw)

    engine.page = engine.context.new_page()

def dispose():
    if engine is not None:
        engine.context.close()
        engine.browser.close()
        engine.pw.stop()

def get_work_order(wo_id: str):
    validate_api()

    with engine.page as p:
        target_url = get_deeplink(
            "231SAU",
            o_web.DeeplinkObjType.WIE_WORK_ORDER,
            o_web.DeeplinkAction.EDIT,
            {
                "workOrderNumber": f"WO-SAU-{wo_id}"
            }
        )

        print(f"\nPulling Work Order data from WO-SAU-{wo_id} : {target_url}")
        p.goto(
            target_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        if p.get_by_text("Type", exact=True).count() == 0:
            def attempt_expand_details():
                try:
                    # Expand details so that they can be read
                    p.get_by_role("button", name="Expand Details").click()


                    playwright.sync_api.expect(p.get_by_text("Type", exact=True)).to_be_visible(timeout=500)
                    return True
                except Exception:
                    return False

            timeout_attempts = 5
            passed = False

            for _ in range(timeout_attempts):
                if attempt_expand_details():
                    passed = True
                    break
            if not passed:
                raise TimeoutError(f"Could not expand details (Timed out after {timeout_attempts} attempts.)")


        _type = get_field(p, "Type")
        item = get_field(p, "Item")
        priority = get_field(p, "Priority")
        item_desc = get_field(p, "Item Description")
        qty = get_field(p, "Quantity").replace("EA", "").strip()
        status = get_field(p, "Status")

        print(f"WO-SAU-{wo_id}:"
              f"\n\tTYPE: {_type}"
              f"\n\tITEM: {item}"
              f"\n\tITEM DESCRIPTION: {item_desc}"
              f"\n\tQUANTITY: {qty}"
              f"\n\tSTATUS: {status}"
              f"\n\tPRIORITY: {priority}"
          )
