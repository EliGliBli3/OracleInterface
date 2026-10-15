from playwright.sync_api import sync_playwright, expect
from pathlib import Path

AUTH_STATE = Path("./oracle_auth_state.json")
PROFILE_DIR = "./oracle_cookies"
ORACLE_HOST = "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
LOGIN_URL = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"


def get_field(page, label_text):

    # Exact label text match (avoids matching with fields with similar values)
    label = page.locator("label").get_by_text(
        label_text, exact=True
    )

    if label.count() == 0:
        raise ValueError(f"Field not found: {label_text}")

    # All Work Order fields follow this pattern (<tr> { label, value })
    row = label.first.locator("xpath=ancestor::tr[1]")
    cells = row.locator(":scope > td")

    if cells.count() < 2:
        raise ValueError(f"Unable to find value cell for {label_text}")

    return cells.nth(1).inner_text().strip()

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
            viewport={"width":1440,"height":900}
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

                print(f"Pulling Work Order Data ({i}/{len(wo_ids)})")
                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                if page.get_by_text("Type", exact=True).count() == 0:
                    # Expand details so that they can be read
                    page.get_by_role("button", name="Expand Details").click()

                    expect(page.get_by_text("Type", exact=True)).to_be_visible()

                print(f"\nWO-SAU-{wo_id}:"
                      f"\n\tTYPE: {get_field(page, "Type")}"
                      f"\n\tITEM: {get_field(page, "Item")}"
                      f"\n\tITEM DESCRIPTION: {get_field(page, "Item Description")}"
                      f"\n\tQUANTITY: {get_field(page, "Quantity")}"
                      f"\n\tSTATUS: {get_field(page, "Status")}"
                      f"\n\tPRIORITY: {get_field(page, "Priority")}"
                  )

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    run_login()

    # Trial fetch
    fetch_wos(["125433", "112830", "119932", "121052"])
