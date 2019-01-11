"use strict";

let metadataUrl = null;


/**
 * Set the root URL at which the data source may be accessed in the PEDASI API.
 *
 * @param url PEDASI API data source URL
 */
function setMetadataUrl(url) {
    "use strict";
    metadataUrl = url;
}


function getCookie(name) {
    const re = new RegExp("(^| )" + name + "=([^;]+)");
    const match = document.cookie.match(re);
    if (match) {
        return match[2];
    }
}


function tableAppendRow(table, values, id=null) {
    const row = table.insertRow(-1);
    if (id !== null) {
        row.id = id;
    }

    for (const value of values) {
        const cell = row.insertCell(-1);
        const text = document.createTextNode(value);
        cell.appendChild(text);
    }

    return row;
}


function postMetadata() {
    fetch(
        metadataUrl,
        {
            method: "POST",
            body: JSON.stringify({
                field: document.getElementById("id_field").value,
                value: document.getElementById("id_value").value
            }),
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }
    ).then(
        response => response.json()
    ).then(
        function (response) {
            if (response.status === "success") {
                const table = document.getElementById("tableMetadata");
                const field = response.data.field;
                const value = response.data.value;

                const row = tableAppendRow(
                    table,
                    [field, value],
                    "metadata-row-" + response.data.field_short + "-" + value
                );

                const buttonCell = row.insertCell(-1);
                const button = document.createElement("button");

                button.id = "btn-" + field + "-" + value;
                button.classList.add("btn", "btn-sm", "btn-danger", "float-right");
                button.addEventListener(
                    "click",
                    function () {
                        const f = response.data.field_short;
                        const v = value;
                        deleteMetadata(f, v);
                    }
                );
                button.textContent = "Delete";
                buttonCell.appendChild(button);
                row.appendChild(buttonCell);
            }
        }
    ).catch(
        function (e) {
            console.log(e);
        }
    )
}

function deleteMetadata(field, value) {
    fetch(
        metadataUrl,
        {
            method: "DELETE",
            body: JSON.stringify({
                field: field,
                value: value
            }),
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }
    ).then(
        response => response.json()
    ).then(function (response) {
        if (response.status === "success") {
            const row = document.getElementById("metadata-row-" + field + "-" + value);
            row.parentNode.removeChild(row);
        }

    })
}
