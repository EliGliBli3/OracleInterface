from __future__ import annotations

from datetime import datetime
from enum import Enum

class Date:
    def __init__(self, _datetime: datetime):
        self.value = _datetime.strftime("%m:%d:%y %-I:%M %p")

class OrgCode(Enum):
    SAUK_RAPIDS = "231SAU"

class DeeplinkObjType(Enum):
    WIE_WORK_ORDER = "WIE_WORK_ORDER"
    QUALITY_ISSUES = "ISSUES"

class DeeplinkAction(Enum):
    EDIT = "EDIT"
    VIEW = "VIEW"
    NONE = "NONE"


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
        STANDARD = "Standard"
        REWORK = "Rework"
        NONSTANDARD = "Nonstandard"
        TRANSFORM = "Transform"

    class BaseInformation:
        def __init__(self, _id: str, _type: WorkOrder.Type, _part: str, _quantity: int):
            self.work_order_id: str = _id
            self.work_order_type: WorkOrder.Type = _type
            self.part: str = _part
            self.quantity: int = _quantity

    class GeneralInformation:
        def __init__(self):
            self.status: WorkOrder.Status
            self.description: str
            self.priority: int
            self.start_date: Date
            self.end_date: Date

    class Item:
        def __init__(self):
            self.name: str
            self.fixed: bool
            self.quantity: float

    class Resource:
        def __init__(self):
            self.name: str
            self.fixed: bool
            self.usage_rate: float

    class Operation:
        class SupplierDetails:
            def __init__(self):
                self.part: str
                self.supplier: str
                self.generate_shipment: bool
                self.lead_time: int # in hours

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