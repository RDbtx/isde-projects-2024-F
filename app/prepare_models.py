import importlib
import logging

from config import Configuration

conf = Configuration()


def prepare_models():
    """
    Pre-downloads the models specified in the configuration object.

    This function iterates over the models specified in the configuration and downloads them
    using the `torchvision.models` module. The models are downloaded with their default weights
    to avoid unnecessary delays during inference. After downloading, the function releases memory
    by deleting the model from memory.

    Raises
    ------
    ImportError
        If the specified model is not found in the `torchvision.models` module.
    """
    for model_name in conf.models:
        try:
            module = importlib.import_module("torchvision.models")
            # download model
            _ = module.__getattribute__(model_name)(weights="DEFAULT")
            del _  # free up memory
        except ImportError:
            logging.error("Model {} not found".format(model_name))


if __name__ == "__main__":
    prepare_models()
