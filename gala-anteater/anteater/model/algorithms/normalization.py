import os

import joblib
from sklearn.preprocessing import StandardScaler

from anteater.utils.common import get_file_path
from anteater.utils.settings import ModelSettings

from anteater.utils.log import Log

log = Log().get_logger()


class Normalization:
    def __init__(self):
        settings = ModelSettings()
        props = settings.norm_properties
        self.model_path = get_file_path(props["file_name"])
        self.model = self.load_model()

    def load_model(self):
        """Loads model"""
        if not os.path.isfile(self.model_path):
            log.warning("Normalization model was not found! Please run model training in advance!")
            return StandardScaler()

        return joblib.load(self.model_path)

    def save(self):
        joblib.dump(self.model, self.model_path)

    def fit_transform(self, x):
        x_norm = self.model.fit_transform(x)
        self.save()

        return x_norm

    def transform(self, x):
        x_norm = self.model.transform(x)
        return x_norm

