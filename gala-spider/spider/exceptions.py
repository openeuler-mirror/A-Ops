class SpiderException(Exception):
    pass


class StorageException(SpiderException):
    pass


class StorageConnectionException(StorageException):
    pass


class MetadataException(StorageException):
    pass
