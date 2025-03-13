/**
 * Captures the content of an HTML canvas element and allows the user to download it as a JPEG image file.
 *
 * This function retrieves the specified canvas element using its ID, extracts its contents as a JPEG image,
 * and creates a downloadable link. If the canvas element does not exist, an alert is displayed, and the function exits.
 *
 * @param {string} elementID - The ID of the canvas element to download.
 * @throws {Error} If the canvas element is not found, an alert is displayed.
 */
function downloadPLOT(elementID) {
    var canvas = document.getElementById(elementID);
    var immagine = document.getElementById('selectedImage')
    var image_name = immagine.getAttribute('alt')
    if (!canvas) {
        alert("ATTENTION: No plot has been found!");
        return;
    }

    var image = canvas.toDataURL("image/jpeg");
    var imageLink = document.createElement("a");
    imageLink.href = image;
    imageLink.download = `${image_name}_${elementID}_data.jpeg`;
    imageLink.click();
}

/**
 * Downloads classification scores from the 'makeGraph' script element as a JSON file.
 *
 * This function retrieves classification scores stored in the `classification_scores` attribute of
 * the 'makeGraph' script element. If no scores are found, an alert notifies the user, and the function exits.
 * The function formats the retrieved data as JSON and initiates a download as a `.json` file.
 *
 * @param {string} elementID - The identifier used in the downloaded filename.
 * @throws {Error} If no classification scores are available, an alert is displayed.
 */
function downloadClassificationJSON(elementID) {
    var scripts = document.getElementById('makeGraph');
    var classification_scores = scripts.getAttribute('classification_scores');
    var immagine = document.getElementById('selectedImage')
    var image_name = immagine.getAttribute('alt')

    if (!classification_scores) {
        alert("ATTENTION: No graph data available!");
        return;
    }

    var items = JSON.parse(classification_scores);
    var data = {scores: items, date: Date.now()};
    const jsonData = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonData], {type: "application/json"});

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${image_name}_${elementID}_data.json`;
    a.click();
}

/**
 * Downloads histogram data as a JSON file.
 *
 * This function retrieves histogram data from `computeHistogram()`, which analyzes pixel intensities
 * in the red, green, and blue channels. If no histogram data is available, an alert notifies the user.
 * The histogram data is then formatted as JSON and downloaded as a `.json` file.
 *
 * @throws {Error} If no histogram data is available, an alert is displayed.
 */
function downloadHistogramJSON() {
    var immagine = document.getElementById('selectedImage')
    var image_name = immagine.getAttribute('alt')
    const histogramData = computeHistogram();

    if (!histogramData) {
        alert("No histogram data available. Please select an image first.");
        return;
    }

    const jsonContent = JSON.stringify({
        red: histogramData.red,
        green: histogramData.green,
        blue: histogramData.blue
    }, null, 2);

    const blob = new Blob([jsonContent], {type: "application/json"});
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${image_name}_histogram_data.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
