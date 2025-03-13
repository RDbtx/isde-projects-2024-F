"""
This is a simple classification service. It accepts an url of an
image and returns the top-5 classification labels and scores.
"""
import importlib
import json
import logging
import torch
from app.utils import get_filename

from torchvision import transforms
from fastapi import UploadFile

from app.config import Configuration

conf = Configuration()

import os
from PIL import Image


def fetch_image(image_id: str) -> Image.Image:
    """
    Retrieves an image from the edited, upload, or dataset folder.

    This function attempts to fetch an image using the provided image ID.
    - It first checks if an edited version of the image exists in the 'edited' folder.
    - If not found, it looks in the upload folder.
    - If still not found, it retrieves the image from the default dataset folder.

    Parameters
    ----------
    image_id : str
        The filename or identifier of the image to be retrieved.

    Returns
    -------
    Image.Image
        The opened image file as a PIL Image object.
    """

    edited_image_path = os.path.join(conf.edit_folder_path, image_id)
    upload_image_path = os.path.join(conf.upload_folder_path, image_id)
    default_image_path = os.path.join(conf.image_folder_path, image_id)

    if os.path.exists(edited_image_path):
        print(f"Fetching edited image: {edited_image_path}")
        return Image.open(edited_image_path)

    if os.path.exists(upload_image_path):
        print(f"Fetching uploaded image: {upload_image_path}")
        return Image.open(upload_image_path)

    if os.path.exists(default_image_path):
        print(f"Fetching default image: {default_image_path}")
        return Image.open(default_image_path)

    raise FileNotFoundError(f"Image not found in any folder: {image_id}")


def store_uploaded_image(file: UploadFile) -> str:
    """
    Saves an uploaded image to the designated upload folder with a unique filename.

    This function stores the uploaded image file in the upload directory,
    ensuring the filename does not overwrite existing files.

    Parameters
    ----------
    file : UploadFile
        The uploaded file containing the image data.

    Returns
    -------
    str
        The unique filename of the saved image.
    """
    upload_dir = conf.upload_folder_path
    os.makedirs(upload_dir, exist_ok=True)

    filename = get_filename(upload_dir, os.path.basename(file.filename))
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return filename


def get_labels() -> list:
    """
    Retrieves the ImageNet class labels.

    This function loads the ImageNet labels from a JSON file and returns them
    as a list, where each index corresponds to a class label.

    Returns
    -------
    list of str
        A list of ImageNet labels where each index represents a class.
    """
    labels_path = os.path.join(conf.image_folder_path, "imagenet_labels.json")
    with open(labels_path) as f:
        labels = json.load(f)
    return labels


def get_model(model_id: str):
    """
    Loads a pre-trained model from the configuration.

    This function imports a specified model from `torchvision.models`
    using the given model ID. The model is pre-downloaded to prevent
    unnecessary waiting during classification.

    Parameters
    ----------
    model_id : str
        The identifier of the model to be loaded (must be in `conf.models`).

    Returns
    -------
    torch.nn.Module
        The loaded PyTorch model with default pretrained weights.

    Raises
    ------
    ImportError
        If the specified model is not found.
    """
    if model_id in conf.models:
        try:
            module = importlib.import_module("torchvision.models")
            return module.__getattribute__(model_id)(weights="DEFAULT")
        except ImportError:
            logging.error(f"Model {model_id} not found")
    else:
        raise ImportError(f"Model {model_id} not found in configuration.")


def classify_image(model_id: str, img_id: str) -> list:
    """
    Classifies an image using the specified pre-trained model.

    This function feeds the specified image into a pre-trained model and
    returns the top-5 classification results.

    Parameters
    ----------
    model_id : str
        The identifier of the pre-trained model to be used for classification.
    img_id : str
        The identifier (filename) of the image to be classified.

    Returns
    -------
    list of tuple
        A list containing the top-5 classification results, where each item
        is a tuple of (label_name: str, confidence_score: float).
    """
    img = fetch_image(img_id)
    model = get_model(model_id)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Apply transformation
    img = img.convert("RGB")
    preprocessed = transform(img).unsqueeze(0)

    # Get model output
    out = model(preprocessed)
    _, indices = torch.sort(out, descending=True)

    # Convert scores to percentages
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100

    # Retrieve labels
    labels = get_labels()

    # Extract top-5 classification results
    output = [(labels[idx], percentage[idx].item()) for idx in indices[0][:5]]

    img.close()
    return output
