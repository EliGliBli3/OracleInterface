from datetime import datetime
from enum import Enum
from turtledemo.penrose import start

class Date:
    def __init__(self, _datetime: datetime):
        self.value = _datetime.strftime("%m:%d:%y %-I:%M %p")

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

    class BaseInformation:
        def __init__(self):
            self.work_order_id: str
            self.work_order_type: WorkOrder.Type
            self.part: str
            self.quantity: int

    class GeneralInformation:
        def __init__(self):
            self.status: WorkOrder.Status
            self.description: str
            self.priority: int
            self.start_date: Date
            self.end_date: Date

    class Item:
        def __init__(self):
            pass

    class Resource:
        def __init__(self):
            pass

    class Operation:
        class SupplierDetails:
            def __init__(self):
                self.part: str
                self.supplier: str
                self.generate_shipment: bool
                self.lead_time: int

        def __init__(self):
            self.op: int
            self.code: str | (str, str)  # Code | (Name, WorkCenter)
            self.operation_type: str
            self.work_instruction: str
            self.items: list[WorkOrder.Item]
            self.resources: list[WorkOrder.Resource]
            self.supplier_details: WorkOrder.Operation.SupplierDetails

    def __init__(self, general_information: GeneralInformation, operations: list[Operation]):
        self.base_information: WorkOrder.BaseInformation
        self.general_information: WorkOrder.GeneralInformation = general_information
        self.operations: list[WorkOrder.Operation] = operations
        self.lots = list[str]