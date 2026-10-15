from enum import Enum

class DeeplinkObjType(Enum):
    WIE_WORK_ORDER = "WIE_WORK_ORDER"
    QUALITY_ISSUES = "ISSUES"

class DeeplinkAction(Enum):
    EDIT = "EDIT"
    VIEW = "VIEW"

