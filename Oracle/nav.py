from typing import Callable

from playwright.sync_api import Page, expect
import Oracle.web as web, Oracle.interface as interface, main
from Oracle.interface import Engine
from Oracle.web import OrgCode
import re

from logger import *


# Standard dictionary keys
class SavedPageType(Enum):
    QUALITY_ISSUES_SEARCH = "quality_issues"
    MANAGE_WORK_ORDERS = "manage_work_orders"

saved_pages: dict[str, Page] = {}

def get_saved_page(_type: SavedPageType|str, navigate: Callable):

    str_type = _type.value if isinstance(_type, SavedPageType) else _type

    keys = saved_pages.keys()
    if keys is not None and str_type in keys:
        return saved_pages.get(str_type)

    log(f"No tab found for {str_type}. Navigating...", LogLevel.PENDING)

    p: Page = navigate()
    saved_pages[str_type] = p
    log(f"Saved new page for type {str_type}!", LogLevel.SUCCESS)

    return p


def get_deeplink(org_code: OrgCode | str, _type: web.DeeplinkObjType, action: web.DeeplinkAction, params: dict):
    org_code_str = org_code.value if isinstance(org_code, OrgCode) else org_code
    url = (
        f"{main.ORACLE_TEST_HOST if main.test_environment else main.ORACLE_HOST}/fscmUI/faces/deeplink"
        f"?objType={_type.value}&action={action.value}" +
        (f"&objKey=organizationCode={org_code_str}" if action != web.DeeplinkAction.NONE else "")
    )
    for param in params:
        url += f";{param}={params.get(param)}"

    return url

def goto_home(page: Page):
    try:
        page.goto(
            main.LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=30000
        )

        return True
    except Exception:
        return False

def goto_work_order(page: Page, job_num: str):
    try:
        target_url = get_deeplink(
            OrgCode.SAUK_RAPIDS,
            web.DeeplinkObjType.WIE_WORK_ORDER,
            web.DeeplinkAction.EDIT,
            {
                "workOrderNumber": "WO-SAU-" + job_num.replace("WO-SAU-", "")
            }
        )
        log(f"Going to {target_url}...")
        page.goto(
            target_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        return page
    except Exception:
        return None

def goto_quality_issues(engine: Engine):
    page_type = SavedPageType.QUALITY_ISSUES_SEARCH
    def navigate():
        p: Page = new_tab(engine)

        try:
            target_url = get_deeplink(
                OrgCode.SAUK_RAPIDS,
                web.DeeplinkObjType.QUALITY_ISSUES,
                web.DeeplinkAction.NONE,
                {

                }
            )
            p.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            search_textbox = p.get_by_role("combobox", name="Search", exact=True)
            search_button = p.get_by_role("button", name="Search", exact=True)

            # Searches a character that is not found in any NC numbers.
            # Throughout several trials, this consistently loaded the 'search' tab the fastest.
            search_textbox.click()
            search_textbox.fill("!")

            # Waits for the page to stop making requests
            # (Search doesn't work if metric panels are loading)
            p.wait_for_load_state("networkidle")
            search_button.click()

            return p
        except Exception as e:
            err_break(f"Error navigating to quality issues landing page!\n{e}")

    p: Page|None = get_saved_page(page_type, navigate); assert p is not None
    return p

def goto_quality_issue(engine: Engine, nc_num: str):
    page: Page = goto_quality_issues(engine)

    search_tab = page.get_by_role("link", name="Search", exact=True)
    search_tab.click()

    search_bar_fast = page.get_by_placeholder("Search For", exact=True)
    search_bar_fast.click()

    search_bar_fast.fill(nc_num)
    search_bar_fast.press("Enter", delay=100)

    try:
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("link", name=re.compile(r"^NC")).first).to_be_visible(timeout=30000) # Waits for an NC to be visible
        nc_link = page.get_by_role("link", name=f"NC{nc_num}", exact=True)

        if nc_link.count() == 0:
            nc_link = page.get_by_role("link", name=f"NC").first

        nc_link.click()
        expect(page.get_by_role("link", name="Actions", exact=True)).to_be_visible(timeout=30000)
    except Exception as e:
        log(f"Could not find any NCs for input {nc_num}\n{e}", LogLevel.WARN)

    assert page is not None; return page

def goto_manage_work_orders(engine: Engine):
    page_type = SavedPageType.MANAGE_WORK_ORDERS

    def navigate():
        p: Page = new_tab(engine)

        try:
            target_url = get_deeplink(
                OrgCode.SAUK_RAPIDS,
                web.DeeplinkObjType.WIE_WORK_ORDER,
                web.DeeplinkAction.EDIT,
                {
                    "workOrderNumber": "WO-SAU-"
                }
            )
            log(target_url)
            p.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            p.get_by_role("img", name="Close Tab", exact=True).click()
            p.get_by_role("img", name="Tasks", exact=True).click()
            p.get_by_role("link", name="Manage Work Orders", exact=True).click()

            return p
        except Exception as e:
            err_break(f"Error navigating to manage work orders landing page!\n{e}")

    return get_saved_page(page_type, navigate)

def new_tab(engine: interface.Engine):
    page = engine.context.new_page()
    goto_home(page)

    engine.pages.append(page)
    return page