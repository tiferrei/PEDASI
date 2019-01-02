let params = new Map();


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
 *
 * @param {string} url PEDASI API data endpoint
 */
function submitQuery(url) {
    "use strict";
    const results = document.getElementById("queryResults");
    const query = url + "?" + getQueryParamString();

    $.getJSON(
        query,
        function (data) {
            results.textContent = JSON.stringify(data, null, 4);
        }
    );
}


/**
 * Query the PEDASI API for data source metadata and render it into the 'metadata' panel.
 *
 * @param {string} url PEDASI API metadata endpoint
 */
function populateMetadata(url) {
    "use strict";
    $.getJSON(
        url,
        function (data) {
            if (data.status === "success") {
                const element = document.getElementById("metadata");

                data.data.forEach(function (item) {
                    const p = document.createElement("p");
                    p.textContent = JSON.stringify(item);
                    element.appendChild(p);
                });
            }
        }
    );
}


/**
 * Query the PEDASI API for the list of data sets within the data source and render into the 'datasets' panel.
 *
 * @param {string} url PEDASI API datasets endpoint
 */
function populateDatasets(url) {
    "use strict";
    $.getJSON(
        url,
        function (data) {
            if (data.status === "success") {
                const table = document.getElementById("datasets");

                data.data.forEach(function (item) {
                    let row = table.insertRow();
                    let cell = row.insertCell();

                    let content = document.createTextNode(item);
                    cell.appendChild(content);
                });
            }
        }
    );
}
