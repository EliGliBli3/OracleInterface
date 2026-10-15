from playwright.sync_api import sync_playwright
from pathlib import Path

AUTH_STATE = Path("./oracle_auth_state.json")
PROFILE_DIR = "./oracle_cookies"
ORACLE_HOST = "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
LOGIN_URL = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"


def block_unneeded_resources(route):
    if route.request.resource_type in {"image", "stylesheet", "font"}:
        route.abort()
    else:
        route.continue_()

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

def fetch_wo(wo_id):
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

            # OPTIMIZATION: Blocks images, fonts, etc. downloads (BROKEN: 'list' has no attribute 'route')
            # ENABLE WHEN WORKFLOW IS CONFIRMED TO WORK
            # page.route("**/*", block_unneeded_resources)

            target_url = (
                f"{ORACLE_HOST}/fscmUI/faces/deeplink"
                f"?objType=WIE_WORK_ORDER&action=EDIT"
                f"&objKey=organizationCode=231SAU;"
                f"workOrderNumber=WO-SAU-{wo_id}"
            )

            print("Navigating to deeplink...")
            page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            msg = page.get_by_role("textbox", name="Description").text_content()
            print(msg)

            #page.pause()

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    run_login()

    # Trial fetch
    fetch_wo("3643")
