import playwright.sync_api
from playwright.sync_api import Playwright, Page

o_web = None
nav = None

class Engine:
    def __init__(self,
                 browser: playwright.sync_api.Browser,
                 context: playwright.sync_api.BrowserContext,
                 pw: Playwright
     ):
        import Oracle.web as o_web
        import Oracle.nav as nav

        self.browser: playwright.sync_api.Browser = browser
        self.context: playwright.sync_api.BrowserContext = context
        self.pw: Playwright = pw
        self.pages: list[playwright.sync_api.Page] = []


def new_work_order(engine: Engine):#, info: o_web.WorkOrder.BaseInformation):
    page: Page = nav.goto_manage_work_orders(engine)

    page.get_by_role("presentation", name="Create", exact=True).click()