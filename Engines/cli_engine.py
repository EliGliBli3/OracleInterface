import os
import sys
from collections.abc import Callable
from lib2to3.fixes.fix_input import context

from logger import *
import Engines.oracle_engine as fscm

class Button:
    def __init__(self, name: str, action: Callable):
        self.name = name
        self.action = action

class Page:
    def __init__(self, name: str, _context: []):
        self.name = name
        self.context = _context

class ButtonPage(Page):
    def __init__(self, name: str, buttons: [Button], _context: []):
        super().__init__(name, _context)
        self.buttons = buttons

class InputPage(Page):
    def __init__(self, name: str, msg: str, action: Callable, _context: []):
        super().__init__(name, _context)
        self.msg = msg
        self.action: Callable = action

curr_page: Page

def go_to_page(page: ButtonPage | InputPage):
    global curr_page

    os.system('cls')
    curr_page = page

    print(f"----- {page.name} -----\n")
    if isinstance(page, ButtonPage):
        for i, button in enumerate(page.buttons):
            print(f"({i}) {button.name}")
        try:
            selection = int(input("Select an action > "))

            button: Button = page.buttons[selection]
            button.action(page.context)
        except Exception as e:
            log(e, LogLevel.WARN)
            go_to_page(page)
    elif isinstance(page, InputPage):
        try:
            _input = input(page.msg + " > ")

            ctx: [] = page.context
            ctx.append(_input)

            page.action(ctx)
        except Exception as e:
            log(e, LogLevel.WARN)
            go_to_page(page)


class Pages:
    def __init__(self):
        self.home = None
        self.get_wo = None

        self.set_pages()

    def set_pages(self):
        self.home = ButtonPage(
            "Home",
            [
                Button(
                    "Get Work Order Details",
                    lambda args: go_to_page(self.get_wo)
                ),
                Button(
                    "Exit",
                    sys.exit
                )
            ],
            _context = []
        )

        self.get_wo = InputPage(
            "Get Work Order Details",
            "Enter Work Order Number",
            Pages.page_get_wo_action,
            _context = []
        )

    def page_get_wo_action(_input: str):
        log(f"Fetching WO-SAU-{_input[0]}")
        wo: fscm.WorkOrder = fscm.get_work_order(_input[0])
        log(f"Found WO-SAU-{_input[0]} ({wo.status})")
        go_to_page(InputPage(
            name=f"WO-SAU-{_input[0]}",
            msg=f"Type: {wo.type} ({wo.status})\n"
                f"Item: {wo.item} (QTY: {wo.quantity})\n"
                f"Description: {wo.description}\n"
                f"Timespan: {wo.start_date} -> {wo.completion_date}"
                + "\n\n",
            action=lambda args: go_to_page(get_home_page()),
            _context=[]
        ))


pages: Pages = Pages()
def get_home_page():
    return pages.home