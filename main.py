from playwright.sync_api import sync_playwright, expect
from pathlib import Path

AUTH_STATE = Path("./oracle_auth_state.json")
PROFILE_DIR = "./oracle_cookies"
ORACLE_HOST = "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
LOGIN_URL = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"


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
        raise ValueError(f"Field not found: {label_text}")

    row = label.locator("xpath=ancestor::tr[1]")
    cells = row.locator(":scope > td")

    if cells.count() < 2:
        raise ValueError(f"Unable to find value cell for {label_text}")

    value_cell = cells.nth(1)

    inputs = value_cell.locator("input:not([type='hidden'])")
    if inputs.count() > 0:
        values = [
            inputs.nth(i).input_value().strip()
            for i in range(inputs.count())
        ]
        values = [value for value in values if value]
        if values:
            result = " ".join(values)
        else:
            result = ""
    else:
        result = ""

    if not result:
        result = value_cell.inner_text().strip()

    if label_text == "Quantity":
        unit = value_cell.locator("span.p_AFReadOnly")
        if unit.count() > 0:
            unit_text = unit.last.inner_text().strip()
            if unit_text and unit_text not in result.split():
                result = f"{result} {unit_text}".strip()

    return "" if result is None else result

def run_login():
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

def fetch_wos(wo_ids: [str]):
    if not AUTH_STATE.exists():
        raise RuntimeError("run_login() was not fully executed before attempting to fetch.")

    with (sync_playwright() as p):
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state=str(AUTH_STATE),
            viewport={"width":720,"height":450}
        )

        try:
            page = context.new_page()

            for i, wo_id in enumerate(wo_ids):
                target_url = (
                    f"{ORACLE_HOST}/fscmUI/faces/deeplink"
                    f"?objType=WIE_WORK_ORDER&action=EDIT"
                    f"&objKey=organizationCode=231SAU;"
                    f"workOrderNumber=WO-SAU-{wo_id}"
                )

                print(f"\nPulling Work Order Data ({i+1}/{len(wo_ids)}) {'🟩' * (i+1)}{'⬛'*(len(wo_ids)-(i+1))}")
                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                #page.route("**/*", block_unneeded_resources)

                if page.get_by_text("Type", exact=True).count() == 0:
                    def attempt_expand_details():
                        try:
                            # Expand details so that they can be read
                            page.get_by_role("button", name="Expand Details").click()

                            expect(page.get_by_text("Type", exact=True)).to_be_visible(timeout=500)
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



                _type = get_field(page, "Type")
                item = get_field(page, "Item")
                priority = get_field(page, "Priority")
                item_desc = get_field(page, "Item Description")
                qty = get_field(page, "Quantity")
                status = get_field(page, "Status")

                print(f"WO-SAU-{wo_id}:"
                      f"\n\tTYPE: {_type}"
                      f"\n\tITEM: {item}"
                      f"\n\tITEM DESCRIPTION: {item_desc if item_desc != "" else "N/A"}"
                      f"\n\tQUANTITY: {qty}"
                      f"\n\tSTATUS: {status}"
                      f"\n\tPRIORITY: {priority if priority != "" else "N/A"}"
                  )

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    run_login()

    # Trial fetch
    fetch_wos([
        "125433",
        "112830",
        "119932",
        "121052",
        "133828",
        "130664",
        "147040",
        "142653",
        "139575",
    ])
