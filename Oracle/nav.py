from playwright.sync_api import Page
import Oracle.web as web, Oracle.interface as interface, main
from Oracle.web import WorkOrder


def get_deeplink(org_code: str, _type: web.DeeplinkObjType, action: web.DeeplinkAction, params: dict):
    url = (
        f"{main.ORACLE_HOST}/fscmUI/faces/deeplink"
        f"?objType={_type.value}&action={action.value}"
        f"&objKey=organizationCode={org_code}"
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
            "231SAU",
            web.DeeplinkObjType.WIE_WORK_ORDER,
            web.DeeplinkAction.EDIT,
            {
                "workOrderNumber": f"WO-SAU-{job_num}"
            }
        )
        page.goto(
            target_url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        return True
    except Exception:
        return False


def new_tab(engine: interface.Engine):
    page = engine.context.new_page()
    goto_home(page)

    engine.pages.append(page)
    return page