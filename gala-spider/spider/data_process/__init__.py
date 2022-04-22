from .processor import DataProcessor
from .prometheus_processor import PrometheusProcessor


class DataProcessorFactory:
    @staticmethod
    def get_instance(data_source: str) -> DataProcessor:
        if data_source == 'prometheus':
            return PrometheusProcessor()
        else:
            return None
