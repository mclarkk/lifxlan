# Custom exceptions

class WorkflowException(Exception):
    def __init__(self, message):
        super(WorkflowException, self).__init__(message)


class InvalidParameterException(Exception):
    def __init__(self, message):
        super(InvalidParameterException, self).__init__(message)
