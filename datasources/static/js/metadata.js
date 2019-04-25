"use strict";

let metadataUrl = null;
let ratingUrl = null;


/**
 * Set the root URL at which the data source may be accessed in the PEDASI API.
 *
 * @param url PEDASI API data source URL
 */
function setMetadataUrl(url) {
    "use strict";
    metadataUrl = url;
}

function setRatingUrl(url) {
    "use strict";
    ratingUrl = url;
}


function getCookie(name) {
    "use strict";
    const re = new RegExp("(^| )" + name + "=([^;]+)");
    const match = document.cookie.match(re);
    if (match) {
        return match[2];
    }
}

function updateMetadata(metadataIdField, valueField) {
    "use strict";

    fetch(
        metadataUrl,
        {
            method: "POST",
            body: JSON.stringify({
                field: metadataIdField.value,
                value: valueField.value
            }),
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }

    ).then(function (response) {
        if (response.status !== 200) {
            throw new Error("Request failed")
        }

        valueField.dataset.currentValue = valueField.value;

        return response.json()

    }).then(function (response) {
        console.log(response);
    });
}

function deleteMetadata(metadataIdField, valueField) {
    "use strict";

    fetch(
        metadataUrl,
        {
            method: "DELETE",
            body: JSON.stringify({
                field: metadataIdField.value,
                value: valueField.dataset.currentValue
            }),
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }

    ).then(function (response) {
        if (response.status !== 200) {
            throw new Error("Request failed");
        }

        valueField.dataset.currentValue = "";

        return response.json();

    }).catch(
        error => console.log(error)
    )
}

function submitMetadataForm(event) {
    "use strict";

    const metdataIdField = event.target.getElementsByClassName("fieldMetadataId")[0];
    const valueField = event.target.getElementsByClassName("fieldMetadataValue")[0];

    if (valueField.value) {
        updateMetadata(metdataIdField, valueField);
    } else {
        deleteMetadata(metdataIdField, valueField);
    }

    updateLevelBadge();
}

function updateLevelBadge() {
    "use strict";

    fetch(ratingUrl).then(
        response => response.json()

    ).then(function (data) {
        const levelBadge = document.getElementById("qualityLevelBadge");

        while (levelBadge.hasChildNodes()) {
            levelBadge.removeChild(levelBadge.lastChild);
        }

        for (let i = 0; i < data.quality; i++) {
            const star = document.createElement("i");
            star.classList.add("fas", "fa-star");
            levelBadge.appendChild(star);
        }
    });
}
