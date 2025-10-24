from abc import ABC, abstractmethod
import json

class BaseAnalyzer(ABC):
    def __init__(self):
        self.name = None

    @abstractmethod
    def validation_params(self, params):
        pass

    @abstractmethod
    def analyzer(self, **kwargs):
        pass

    def is_support_models(self, model_type, model_name):
        json.load(open('model_mapping_config.json'))