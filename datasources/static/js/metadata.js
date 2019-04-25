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


/**
 * Create a new metadata item or update an existing one.
 *
 * @param event Form event
 */
function submitMetadataForm(event) {
    "use strict";

    const metadataIdField = event.target.getElementsByClassName("fieldMetadataId")[0];
    const metadataValueIdField = event.target.getElementsByClassName("fieldMetadataValueId")[0];
    const valueField = event.target.getElementsByClassName("fieldMetadataValue")[0];

    let url = metadataUrl;
    let method = "POST";

    if (metadataValueIdField && metadataValueIdField.value) {
        url = metadataUrl + metadataValueIdField.value.toString() + "/";
        method = "PUT";
    }

    fetch(
        url,
        {
            method: method,
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
        if (!response.ok) {
            throw new Error("Request failed: " + response.statusText);
        }

        valueField.dataset.currentValue = valueField.value;
        window.location.reload();

    }).catch(function (error) {
        console.log(error);

        if (valueField.dataset.currentValue !== null) {
            valueField.value = valueField.dataset.lastValue;
        }

    });
}

/**
 * Delete an existing metadata item.
 *
 * @param event Form event
 */
function deleteMetadataForm(event) {
    "use strict";

    const metadataIdField = event.target.getElementsByClassName("fieldMetadataValueId")[0];

    fetch(
        metadataUrl + metadataIdField.value.toString() + "/",
        {
            method: "DELETE",
            headers: {
                "Accept": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        }

    ).then(function (response) {
        if (!response.ok) {
            throw new Error("Request failed: " + response.statusText);
        }

        window.location.reload();

    }).catch(function (error) {
        console.log(error);

    });
}

/**
 * Update the star rating display.
 *
 * @param url Url to get quality level for a data source - defaults to global setting 'ratingUrl'
 * @param badgeId Id of badge element to populate with stars - defaults to 'qualityLevelBadge'
 */
function updateLevelBadge(url, badgeId) {
    "use strict";

    if (!url) {
        url = ratingUrl;
    }

    if (!badgeId) {
        badgeId = "qualityLevelBadge";
    }

    fetch(url).then(
        (response) => response.json()

    ).then(function (data) {
        const levelBadge = document.getElementById(badgeId);

        // Clear existing rating
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
