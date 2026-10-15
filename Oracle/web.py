from enum import Enum

class DeeplinkObjType(Enum):
    WIE_WORK_ORDER = "WIE_WORK_ORDER"
    QUALITY_ISSUES = "ISSUES"

class DeeplinkAction(Enum):
    EDIT = "EDIT"
    VIEW = "VIEW"

class WorkOrder:
    class Status(Enum):
        CANCELED = 0
        CLOSED = 1
        COMPLETE_NO_CHARGE = 2
        COMPLETED = 3
        COMPLETED_AND_REVIEWED = 4
        RELEASED = 5
        UNRELEASED = 6
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
                 order_description: str="",
                 priority: int = 0,
                 item_description: str = "",
                 start_date: int = 0,
                 completion_date: int = 0,
                 ):
        order_name: str = number
        order_type: WorkOrder.Type = _type
        item: str = item
        item_description: str = item_description
        quantity: int = quantity
        order_status: WorkOrder.Status = status
        start_date: int = start_date
        completion_date: int = completion_date
        order_description: str = order_description
        order_priority: int = priority
