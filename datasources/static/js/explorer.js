"use strict";

const params = new Map();

let datasourceUrl = null;
let selectedDataset = null;


/**
 * Set the root URL at which the data source may be accessed in the PEDASI API.
 *
 * @param url PEDASI API data source URL
 */
function setDatasourceUrl(url) {
    "use strict";
    datasourceUrl = url;
}


/**
 * Append a row of text cells to a table.
 *
 * @param table Table to which row should be appended
 * @param values Iterable of strings to append as new cells
 */
function tableAppendRow(table, values) {
    "use strict";
    const row = table.insertRow(-1);

    for (const value of values) {
        const cell = row.insertCell(-1);
        const text = document.createTextNode(value);
        cell.appendChild(text);
    }

    return row;
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
        tableAppendRow(table, [key, value]);
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
        encodedParams.set(key.trim(), value.trim());
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
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        } else {
            return response.text();
        }
    }).then(function (data) {
        if (typeof data === "string") {
            results.textContent = data;
        } else {
            results.textContent = JSON.stringify(data, null, 4);
        }
    });
}


/**
 * Query the PEDASI API for data source internal metadata and render it into the 'metadataInternal' panel.
 */
function populateMetadataInternal() {
    "use strict";

    const table = document.getElementById("metadataInternal");

    const url = getBaseURL();

    fetch(url).then(function (response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error("Internal metadata request failed.");
    }).then(function (data) {
        data.metadata_items.forEach(function (item) {
            tableAppendRow(table, [item.field.name, item.value]);
        });
    }).catch(function (e) {
        tableAppendRow(table, e.toString());
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
        table.deleteRow(-1);
    }

    const url = getBaseURL() + "metadata/";

    fetch(url).then(
        response => response.json()
    ).then(function (data) {
        if (data.status === "success") {
            try{
                data.data.forEach(function (item) {
                    tableAppendRow(table, [JSON.stringify(item, null, 4)]);
                });
            } catch (e) {
                for (const key in data.data) {
                    tableAppendRow(table, [
                        key,
                        JSON.stringify(data.data[key], null, 4)
                    ]);
                }
            }
        } else if (data.message) {
            tableAppendRow(table, [data.message]);
        }
    }).catch(function (e) {
        tableAppendRow(table, [e.toString()]);
    });
}


/**
 * Query the PEDASI API for the list of data sets within the data source and render into the 'datasets' panel.
 */
function populateDatasets() {
    "use strict";
    function rowAppendButton (row, item) {
        const buttonCell = row.insertCell(-1);
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
        row.appendChild(buttonCell);
    }

    const url = getBaseURL() + "datasets/";
    const table = document.getElementById("datasets");

    fetch(url).then(
        response => response.json()
    ).then(function (data) {
        if (data.status === "success") {
            const row = tableAppendRow(table, ["Root"]);
            rowAppendButton(row, null);

            data.data.forEach(function (item) {
                const row = tableAppendRow(table, [item]);
                rowAppendButton(row, item)
            });
        } else if (data.message) {
            tableAppendRow(table, [data.message]);
        }
    }).catch(function (e) {
        tableAppendRow(table, [e.toString()]);
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
    document.getElementById("selectedDataset").textContent = selectedDataset === null ? "None" : selectedDataset;

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


function toggleExpandPanel(e) {
    "use strict";
    const button = e.target;
    const panel = document.querySelector(button.dataset.target);

    if (panel === null) {
        // Happens in MS Edge when a span receives the click event before the button it belongs to
        return;
    }

    const iconPlus = button.querySelector(".toggle-icon-plus");
    const iconMinus = button.querySelector(".toggle-icon-minus");

    if ("expanded" in panel.dataset) {
        panel.style.height = "30vh";
        iconPlus.style.display = "inline";
        iconMinus.style.display = "none";
        delete panel.dataset.expanded;
    } else {
        panel.style.height = "100%";
        iconPlus.style.display = "none";
        iconMinus.style.display = "inline";
        panel.dataset.expanded = "true";
    }
}
