import os
from app.config import Configuration
from PIL import Image, ImageEnhance
import asyncio

conf = Configuration()


def list_images():
    """
    Returns the list of available images in the configured image folder.

    This function filters and retrieves all image filenames with a `.JPEG` extension
    from the image folder specified in the configuration.

    Returns
    -------
    list of str
        A list of image filenames with the `.JPEG` extension.
    """
    img_names = filter(
        lambda x: x.endswith(".JPEG"), os.listdir(conf.image_folder_path)
    )
    return list(img_names)


def scale_values(value: int) -> float:
    """
    Scales a given integer value from the range [-100, 100] to the range [0, 2].

    This function is used to transform values obtained from the form on the editor page,
    ensuring they match the valid range for Pillow's enhance functions.

    Parameters
    ----------
    value : int
        The integer value to scale, ranging from -100 to 100.

    Returns
    -------
    float
        The scaled value within the range [0, 2].
    """
    return (value + 100) / 100


def edit_image(original_image_path: str,
               color_value: int,
               brightness_value: int,
               contrast_value: int,
               sharpness_value: int,
               edited_image_path: str) -> None:
    """
    Applies image enhancements based on user-selected values and saves the edited image.

    This function modifies the original image using Pillow's enhancement functions
    for color, brightness, contrast, and sharpness, based on scaled values obtained
    from a form input. The edited image is saved at the specified path.

    Parameters
    ----------
    original_image_path : str
        The file path of the original image.
    color_value : int
        The color enhancement factor, ranging from -100 to 100.
    brightness_value : int
        The brightness enhancement factor, ranging from -100 to 100.
    contrast_value : int
        The contrast enhancement factor, ranging from -100 to 100.
    sharpness_value : int
        The sharpness enhancement factor, ranging from -100 to 100.
    edited_image_path : str, optional
        The file path where the edited image will be saved (default is
        "app/static/imagenet_subset/edited.jpeg").

    Returns
    -------
    None
        The function modifies and saves the edited image but does not return a value.
    """
    original_image = Image.open(original_image_path)
    edited_image = original_image.copy()

    if edited_image.mode != "RGB":
        edited_image = edited_image.convert("RGB")

    edited_image = ImageEnhance.Color(edited_image).enhance(scale_values(color_value))
    edited_image = ImageEnhance.Brightness(edited_image).enhance(scale_values(brightness_value))
    edited_image = ImageEnhance.Contrast(edited_image).enhance(scale_values(contrast_value))
    edited_image = ImageEnhance.Sharpness(edited_image).enhance(scale_values(sharpness_value))

    edited_image.save(edited_image_path, format="JPEG")


async def remove_file_after_time(file_path: str) -> None:
    """
        Deletes a specified file after a delay of 2 minutes.

        This function waits for 10 seconds before checking if the file
        exists at the given path. If the file is found, it is removed from
        the filesystem.

        Parameters
        ----------
        file_path : str
            The absolute or relative path of the file to be deleted.

        Notes
        -----
        - This function is typically used as a background task in FastAPI.
        - If the file is already deleted before this function executes, no action is taken.
        - The delay is implemented using `asyncio.sleep(10)`, which blocks execution within this function.

        """
    await  asyncio.sleep(10)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} deleted")


def get_filename(image_path: str, filename: str) -> str:
    """
    Generates a unique filename by appending a counter if a file with the same name already exists.

    Parameters
    ----------
    image_path : str
        The directory where the file will be stored.
    filename : str
        The original filename.

    Returns
    -------
    str
        A unique filename with an incremented counter if necessary.
    """
    name, ext = os.path.splitext(filename)
    file_counter = 1
    unique_name = f"{name}{ext}"

    while os.path.exists(os.path.join(image_path, unique_name)):
        unique_name = f"{name}_{file_counter}{ext}"
        file_counter += 1

    return unique_name
