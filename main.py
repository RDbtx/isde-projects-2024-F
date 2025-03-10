import json
from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import Configuration
from app.forms.classification_form import ClassificationForm, EditedImageForm, UploadedImageForm
from app.ml.classification_utils import classify_image, store_uploaded_image
from app.utils import list_images, edit_image

app = FastAPI()
config = Configuration()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/info")
def info() -> dict[str, list[str]]:
    """Returns a dictionary with the list of models and
    the list of available image files."""
    list_of_images = list_images()
    list_of_models = Configuration.models
    data = {"models": list_of_models, "images": list_of_images}
    return data


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """The home page of the service."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/classifications")
def create_classify(request: Request):
    return templates.TemplateResponse(
        "classification_select.html",
        {"request": request, "images": list_images(), "models": Configuration.models},
    )


@app.post("/classifications")
async def request_classification(request: Request):
    form = ClassificationForm(request)
    await form.load_data()
    image_id = form.image_id
    model_id = form.model_id
    classification_scores = classify_image(model_id=model_id, img_id=image_id)
    return templates.TemplateResponse(
        "classification_output.html",
        {
            "request": request,
            "image_id": image_id,
            "classification_scores": json.dumps(classification_scores),
        },
    )


@app.get("/histogram")
def histogram_get(request: Request):
    """This function is a FastAPI route handler for the histogram calculator.
    It is responsible for rendering and returning the "histogram.html" template,
    as all histogram-related functions are executed client-side."""
    return templates.TemplateResponse(
        "histogram.html",
        {"request": request, "images": list_images()},
    )


@app.get("/editor")
def editor_get(request: Request):
    """The editor_get function handles GET requests to the /editor endpoint and renders
    the editor selection page. It serves an HTML template that provides the user
    interface for selecting images,models, and image editing parameters.
    The template is populated with a list of available images and models
    retrieved from the system configuration."""
    return templates.TemplateResponse(
        "editor_select.html",
        {
            "request": request,
            "images": list_images(),
            "models": Configuration.models
        },
    )


@app.post("/editor", response_class=HTMLResponse)
async def request_edited_classification(request: Request):
    """The request_edited_classification function handles POST requests to the /editor endpoint.
    It collects all parameters from the form on the "editor_select.html" page and passes them
    to the edit_image function to generate the edited image. The edited image is then classified,
    and both the edited image and classification results are returned to the client
    via the "editor_output.html" template."""
    form = EditedImageForm(request)
    await form.load_data()

    if not form.is_valid():
        return {"errors": form.errors}

    print(form.image_id)

    original_image_path = f"app/static/imagenet_subset/{form.image_id}"
    edited_image_path = "app/static/imagenet_subset/edited.jpg"

    color_value = form.color_value
    brightness_value = form.brightness_value
    contrast_value = form.contrast_value
    sharpness_value = form.sharpness_value

    edit_image(
        original_image_path,
        color_value,
        brightness_value,
        contrast_value,
        sharpness_value,
        edited_image_path
    )

    edited_image_id = "edited.jpg"
    classification_scores = classify_image(form.model_id, edited_image_id)

    return templates.TemplateResponse(
        "editor_output.html",
        {
            "request": request,
            "image_id": edited_image_id,
            "classification_scores": json.dumps(classification_scores),
        }
    )


@app.get("/upload")
def upload(request: Request):
    return templates.TemplateResponse(
        "classification_upload.html",
        {
            "request": request,
            "models": Configuration.models
        },
    )

@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), model_id: str = Form(...)):
    print("PROVA DEBUG")
    form = UploadedImageForm(file, model_id)

    if not form.is_valid():
        return {"errors": form.errors}

    # Store the uploads image and classify it
    filename = store_uploaded_image(file)
    classification_scores = classify_image(model_id=model_id, img_id=filename)

    return templates.TemplateResponse(
        "classification_upload_output.html",
        {
            "request": request,
            "image_id": filename,
            "image_path": f"/static/uploads/{filename}",
            "classification_scores": json.dumps(classification_scores),
        },
    )
