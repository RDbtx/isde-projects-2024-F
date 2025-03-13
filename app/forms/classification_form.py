from fastapi import Request, UploadFile
from typing import Optional


class EditedImageForm:
    """
    A form handler for collecting and validating image editing parameters.

    This class is used to collect all parameters submitted through the `editor_select.html`
    form and pass them to the backend for processing and image editing.

    Attributes
    ----------
    request : Request
        The HTTP request containing form data.
    errors : list
        A list of validation error messages.
    model_id : str
        The selected model identifier.
    image_id : str
        The selected image identifier.
    color_value : int
        The color adjustment value (-100 to 100).
    brightness_value : int
        The brightness adjustment value (-100 to 100).
    contrast_value : int
        The contrast adjustment value (-100 to 100).
    sharpness_value : int
        The sharpness adjustment value (-100 to 100).
    """

    def __init__(self, request: Request) -> None:
        """
        Initializes a new instance of the EditedImageForm class.

        This constructor sets up attributes to handle the classification form request.

        Parameters
        ----------
        request : Request
            The HTTP request containing form data.
        """
        self.request: Request = request
        self.errors: list = []
        self.model_id: str = ""
        self.image_id: str = ""
        self.color_value: int = 0
        self.brightness_value: int = 0
        self.contrast_value: int = 0
        self.sharpness_value: int = 0

    async def load_data(self):
        """
        Loads and processes form data from the HTTP request.

        This asynchronous method extracts form values from the request and assigns them
        to corresponding instance variables, including model ID, image ID, color, brightness,
        contrast, and sharpness.
        """
        form = await self.request.form()
        self.model_id = form.get("model_id")
        self.image_id = form.get("image_id")

        self.color_value = int(form.get("color_value", 0))
        self.brightness_value = int(form.get("brightness_value", 0))
        self.contrast_value = int(form.get("contrast_value", 0))
        self.sharpness_value = int(form.get("sharpness_value", 0))

    def is_valid(self) -> bool:
        """
        Validates the form data.

        This method checks if the required fields are present and correctly formatted.
        If any required field is missing or invalid, an error message is added to the
        `errors` list.

        Returns
        -------
        bool
            `True` if `image_id` and `model_id` are valid, otherwise `False`.
        """
        if not self.image_id or not isinstance(self.image_id, str):
            self.errors.append("A valid image ID is required.")
        if not self.model_id or not isinstance(self.model_id, str):
            self.errors.append("A valid model ID is required.")
        return not bool(self.errors)


class UploadedImageForm:
    """
    A form handler for processing uploaded image files and associated metadata.

    This class collects and validates the uploaded file, model ID, and additional image
    editing parameters submitted through the `classification_upload.html` and `editor_select.html` forms.

    Attributes
    ----------
    request : Request
        The HTTP request containing form data.
    file : Optional[UploadFile]
        The uploaded image file.
    errors : list
        A list of validation error messages.
    model_id : str
        The selected model identifier.
    image_id : str
        The assigned image identifier.
    color_value : int
        The color adjustment value (-100 to 100).
    brightness_value : int
        The brightness adjustment value (-100 to 100).
    contrast_value : int
        The contrast adjustment value (-100 to 100).
    sharpness_value : int
        The sharpness adjustment value (-100 to 100).
    """

    def __init__(self, file: Optional[UploadFile], request: Request) -> None:
        """
        Initializes a new instance of the UploadedImageForm class.

        Parameters
        ----------
        file : Optional[UploadFile]
            The uploaded image file.
        request : Request
            The HTTP request containing form data.
        """
        self.request: Request = request
        self.file: Optional[UploadFile] = file
        self.errors: list[str] = []
        self.model_id: str = ""
        self.image_id: str = ""
        self.color_value: int = 0
        self.brightness_value: int = 0
        self.contrast_value: int = 0
        self.sharpness_value: int = 0

    async def load_data(self):
        """
        Loads and processes form data from the HTTP request.

        Extracts form values, ensuring they are valid integers within allowed ranges.
        """
        try:
            form = await self.request.form()
            self.model_id = form.get("model_id", "").strip()

            self.color_value = int(form.get("color_value", 0))
            self.brightness_value = int(form.get("brightness_value", 0))
            self.contrast_value = int(form.get("contrast_value", 0))
            self.sharpness_value = int(form.get("sharpness_value", 0))

        except Exception:
            self.errors.append("An error occurred while processing the form. Please try again.")

    def is_valid(self) -> bool:
        """
        Validates the required fields for the uploaded image form.

        Ensures the uploaded file and model ID are provided.
        If any required field is missing, an error message is added to `errors`.

        Returns
        -------
        bool
            `True` if the form is valid (no errors found), otherwise `False`.
        """
        if not self.file:
            self.errors.append("A valid image file is required.")
        elif not self.is_valid_file_type(self.file.filename):
            self.errors.append("Invalid file type. Allowed types: .jpg, .jpeg, .png.")

        return not bool(self.errors)

    def is_valid_file_type(self, filename: str) -> bool:
        """
        Checks if the uploaded file has a valid image extension.

        Parameters
        ----------
        filename : str
            The filename of the uploaded file.

        Returns
        -------
        bool
            `True` if the file extension is valid, otherwise `False`.
        """
        allowed_extensions = {".jpg", ".jpeg", ".png"}
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
