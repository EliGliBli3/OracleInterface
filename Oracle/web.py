from enum import Enum
from turtledemo.penrose import start


class DeeplinkObjType(Enum):
    WIE_WORK_ORDER = "WIE_WORK_ORDER"
    QUALITY_ISSUES = "ISSUES"

class DeeplinkAction(Enum):
    EDIT = "EDIT"
    VIEW = "VIEW"

class WorkOrder:
    class Status(Enum):
        CANCELED = "Canceled"
        CLOSED = "Closed"
        COMPLETE_NO_CHARGE = "Complete No-Charge"
        COMPLETED = "Completed"
        COMPLETED_AND_REVIEWED = "Completed and Reviewed"
        RELEASED = "Released"
        UNRELEASED = "Unreleased"
        NONE = "N/A"

        def get(web_status: str):
            return [s.name for s in list(WorkOrder.Status) if s.value == web_status][0]

    class Type(Enum):
        STANDARD = 0
        REWORK = 1
        NONSTANDARD = 2
        TRANSFORM = 3


    def __init__(self,
                 number: str,
                 _type: Type,
                 item: str,
                 quantity: int,
                 status: Status,
                 description: str,
                 start_date: str,
                 completion_date: str
                 ):
        self.number = number
        self.type = _type
        self.item = item
        self.quantity = quantity
        self.status = status
        self.description = description
        self.start_date = start_date
        self.completion_date = completion_date