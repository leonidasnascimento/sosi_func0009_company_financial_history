class StatusProcessing():
    success: bool 
    message: str
    err_stack: str

    def __init__(self, _success: bool, _message: str, _err_stack: str = ""):
        self.success = _success
        self.message = _message
        self.err_stack = _err_stack
        pass
    pass