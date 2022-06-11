class InferenceException(Exception):
    pass


class DBException(InferenceException):
    pass


class MetadataException(InferenceException):
    pass


class DataParseException(InferenceException):
    pass
