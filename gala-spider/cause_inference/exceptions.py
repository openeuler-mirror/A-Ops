class InferenceException(Exception):
    pass


class DBException(InferenceException):
    pass


class DataParseException(InferenceException):
    pass
