"use strict";

const params = new Map();

let datasourceUrl = null;
let selectedDataset = null;


function setDatasourceUrl(url) {
    "use strict";
    datasourceUrl = url;
}


/**
 * Get the base URL to use for requests to PEDASI API.
 *
 * @returns {string} PEDASI API URL
 */
function getBaseURL() {
    "use strict";
    let url = datasourceUrl;

    if (selectedDataset !== null) {
        url += "datasets/" + selectedDataset + "/";
    }

    return url;
}


/**
 * Render request query parameters into table.
 */
function renderParams() {
    "use strict";
    const table = document.getElementById("tableParams");

    /* Clear the table */
    while (table.rows.length > 1) {
        table.deleteRow(-1);
    }

    params.forEach(function (value, key, map) {
        const row = table.insertRow();

        const cellParam = row.insertCell();
        const textParam = document.createTextNode(key);
        cellParam.appendChild(textParam);

        const cellValue = row.insertCell();
        const textValue = document.createTextNode(value);
        cellValue.appendChild(textValue);
    });
}


/**
 * Get the query params as a URL query string.
 *
 * @returns {string} Query param string
 */
function getQueryParamString() {
    "use strict";
    const encodedParams = new URLSearchParams();
    params.forEach(function (value, key, map) {
        encodedParams.set(key, value);
    });

    return encodedParams.toString();
}


/**
 * Display query param string in #queryParamSpan.
 */
function displayParams() {
    "use strict";
    const paramString = getQueryParamString();
    const span = document.getElementById("queryParamSpan");

    span.textContent = paramString;
}


/**
 * Add a query parameter to the API query.
 *
 * @returns {boolean} return false to halt form processing
 */
function addParam() {
    "use strict";
    const param = document.getElementById("inputParam").value;
    const value = document.getElementById("inputValue").value;

    params.set(param, value);

    renderParams();
    displayParams();

    return false;
}


/**
 * Submit the prepared query to the PEDASI API and render the result into the 'results' panel.
 */
function submitQuery() {
    "use strict";
    const results = document.getElementById("queryResults");
    const query = getBaseURL() + "data/?" + getQueryParamString();

    fetch(query).then(function (response) {
        if (response.ok) {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                return response.json();
            } else {
                return response.text();
            }
        }
        throw new Error("Request failed.");
    }).then(function (data) {
        if (typeof data === "string") {
            results.textContent = data;
        } else {
            results.textContent = JSON.stringify(data, null, 4);
        }
    }).catch(function (error) {
        results.textContent = error.toString();
    });
}


/**
 * Query the PEDASI API for data source metadata and render it into the 'metadata' panel.
 */
function populateMetadata() {
    "use strict";

    const table = document.getElementById("metadata");

    /* Clear the table */
    while (table.rows.length > 0) {
        table.deleteRow();
    }

    const url = getBaseURL() + "metadata/";

    fetch(url).then(function (response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error("Metadata request failed.");
    }).then(function (data) {
        if (data.status === "success") {
            data.data.forEach(function (item) {
                const row = table.insertRow();
                const cell = row.insertCell();
                const text = document.createTextNode(JSON.stringify(item));

                cell.appendChild(text);
            });
        }
    }).catch(function (error) {
        const row = table.insertRow();
        const cell = row.insertCell();
        const text = document.createTextNode(error.toString());

        cell.appendChild(text);
    });
}


/**
 * Query the PEDASI API for the list of data sets within the data source and render into the 'datasets' panel.
 */
function populateDatasets() {
    "use strict";

    const url = getBaseURL() + "datasets/";
    const table = document.getElementById("datasets");

    fetch(url).then(function (response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error("Datasets request failed.");
    }).then(function (data) {
        if (data.status === "success") {
            data.data.forEach(function (item) {
                const row = table.insertRow();
                const nameCell = row.insertCell();
                const buttonCell = row.insertCell();

                const nameText = document.createTextNode(item);
                nameCell.appendChild(nameText);

                const button = document.createElement("button");
                button.id = "btn-" + item;
                button.classList.add("btn", "btn-secondary", "btn-dataset");
                button.addEventListener(
                    "click",
                    function () {
                        selectDataset(item);
                    }
                );
                button.textContent = "Select";
                buttonCell.appendChild(button);
            });
        }
    }).catch(function (error) {
        const row = table.insertRow();
        const nameCell = row.insertCell();

        const nameText = document.createTextNode(error.toString());
        nameCell.appendChild(nameText);
    });
}


/**
 * Change the active dataset.
 *
 * @param datasetId Dataset id to select
 */
function selectDataset(datasetId) {
    "use strict";
    selectedDataset = datasetId;
    document.getElementById("selectedDataset").textContent = selectedDataset;

    populateMetadata();

    // Have to use for ... of ... loop since collection is live (updates with changes to DOM)
    for (const button of document.getElementsByClassName("btn-dataset")) {
        button.removeAttribute("disabled");
        button.textContent = "Select";
    }

    const button = document.getElementById("btn-" + selectedDataset);
    button.textContent = "Selected";
    button.setAttribute("disabled", "true");
}


function toggleExpandPanel(obj, panelId) {
    "use strict";
    const panel = document.getElementById(panelId);

    if ("expanded" in panel.dataset) {
        panel.style.height = "30vh";
        obj.textContent = "Expand";
        delete panel.dataset.expanded;
    } else {
        panel.style.height = "100%";
        obj.textContent = "Shrink";
        panel.dataset.expanded = "true";
    }
}
