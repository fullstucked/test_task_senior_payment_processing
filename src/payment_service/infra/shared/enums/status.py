from enum import Enum


class TaskStatus(str, Enum):
    PENDING = 'pending'
    OK = 'success'
    FAIL = 'failed'
    IN_PROCESS = 'InProcess'
