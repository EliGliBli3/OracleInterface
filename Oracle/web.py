from __future__ import annotations

from datetime import datetime
from enum import Enum
from utils import *
import re

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

    class OperationType(Enum):
        IN_HOUSE = "In-house"
        SUPPLIER = "Supplier"

    class BaseInformation:
        def __init__(self, _id: str, _type: WorkOrder.Type, _part: str, _quantity: int):
            self.work_order_id: str = "WO-SAU-" + _id.replace("WO-SAU-", "")
            self.work_order_type: WorkOrder.Type = _type
            self.part: str = _part
            self.quantity: int = _quantity

    class GeneralInformation:
        def __init__(self, status: WorkOrder.Status, description: str, priority: int, start_date: Date|None, end_date: Date|None):
            self.status: WorkOrder.Status = status
            self.description: str = description
            self.priority: int = priority
            self.start_date: Date = start_date
            self.end_date: Date = end_date

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

        def __init__(self,
                     code: str | (str, str,),
                     op: int = -1,
                     operation_type: WorkOrder.OperationType|None = None,
                     work_instruction: str = "",
                     items=None,
                     resources=None,
                     supplier_details = None

        ):
            if items is None:
                items = []
            if resources is None:
                resources = []
            if operation_type is None:
                operation_type = WorkOrder.OperationType.IN_HOUSE

            self.op: int = op
            self.code: str | (str, str) = code  # Code | (Name, WorkCenter)
            self.operation_type: WorkOrder.OperationType = operation_type
            self.work_instruction: str = work_instruction
            self.items: list[WorkOrder.Item] = items
            self.resources: list[WorkOrder.Resource] = resources
            self.supplier_details: WorkOrder.Operation.SupplierDetails = supplier_details

    def __init__(self, base_information: WorkOrder.BaseInformation|None = None, general_information: GeneralInformation|None = None, operations: list[Operation]|None = None):
        self.base_information: WorkOrder.BaseInformation = base_information
        self.general_information: WorkOrder.GeneralInformation = general_information
        self.operations: list[WorkOrder.Operation] = operations
        self.lots: dict[str, int]

class QualityIssue:
    class Status(Enum):
        DRAFT = "Draft"
        OPEN = "Open"
        SCHEDULED = "Scheduled"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        APPROVAL = "Approval"
        INTERIM_APPROVAL = "Interim Approval"
        DEFINITION = "Definition"

    def __init__(self, issue_id: int|str):
        self.issue_id: int = try_or(
            lambda: int(re.sub(
                pattern="nc",
                repl="",
                string=str(issue_id),
                flags=re.IGNORECASE
            )), default=-1) \
            if isinstance(issue_id, str) \
            else issue_id