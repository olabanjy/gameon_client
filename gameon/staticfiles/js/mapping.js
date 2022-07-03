//This div will display Google map
const mapArea = document.getElementById("map");

//This button will set everything into motion when clicked
const actionBtn = document.getElementById("showMeBtn");

//This will display all the available addresses returned by Google's Geocode Api
const locationsAvailable = document.getElementById("locationList");

//Let's bring in our API_KEY
const __KEY = "AIzaSyAUBoCQ9qfFHOOVqGF7Q0XrhpGl1x6cDHw";

//Let's declare our Gmap and Gmarker variables that will hold the Map and Marker Objects later on
let Gmap;
let Gmarker;

//Now we listen for a click event on our button
actionBtn.addEventListener("click", (e) => {
  // hide the button
  actionBtn.innerHTML = "Get My Location";
  // get the user's position
  getLocation();
});

getLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      displayLocation,
      showError,
      options
    );
  } else {
    window.alert("Sorry, your browser does not support this feature...");
  }
};

// displayLocation
displayLocation = (position) => {
  const lat = position.coords.latitude;
  const lng = position.coords.longitude;

  const latlng = { lat, lng };
  console.log(latlng);

  showMap(latlng, lat, lng);
  createMarker(latlng);
  mapArea.style.display = "block";
  getGeolocation(lat, lng);
};

// Recreates the map
showMap = (latlng, lat, lng) => {
  let mapOptions = {
    center: latlng,
    zoom: 17,
  };

  Gmap = new google.maps.Map(mapArea, mapOptions);
  Gmap.addListener("drag", function () {
    Gmarker.setPosition(this.getCenter());
  });

  Gmap.addListener("dragend", function () {
    Gmarker.setPosition(this.getCenter()); // set marker position to map center
  });

  Gmap.addListener("idle", function () {
    Gmarker.setPosition(this.getCenter()); // set marker position to map center

    if (
      Gmarker.getPosition().lat() !== lat ||
      Gmarker.getPosition().lng() !== lng
    ) {
      setTimeout(() => {
        // console.log("I have to get new geocode here!")
        updatePosition(this.getCenter().lat(), this.getCenter().lng()); // update position display
      }, 2000);
    }
  });
};

// Creates marker on the screen
createMarker = (latlng) => {
  let markerOptions = {
    position: latlng,
    map: Gmap,
    animation: google.maps.Animation.BOUNCE,
    clickable: true,
    // draggable: true
  };
  Gmarker = new google.maps.Marker(markerOptions);
};

// updatePosition on
updatePosition = (lat, lng) => {
  getGeolocation(lat, lng);
};

// Displays the different error messages
showError = (error) => {
  mapArea.style.display = "block";
  switch (error.code) {
    case error.PERMISSION_DENIED:
      mapArea.innerHTML = "You denied the request for your location.";
      break;
    case error.POSITION_UNAVAILABLE:
      mapArea.innerHTML = "Your Location information is unavailable.";
      break;
    case error.TIMEOUT:
      mapArea.innerHTML = "Your request timed out. Please try again";
      break;
    case error.UNKNOWN_ERROR:
      mapArea.innerHTML =
        "An unknown error occurred please try again after some time.";
      break;
  }
};

const options = {
  enableHighAccuracy: true,
};

getGeolocation = (lat, lng) => {
  const latlng = lat + "," + lng;

  fetch(
    `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latlng}&key=${__KEY}`
  )
    .then((res) => res.json())
    .then((data) => populateCard(data.results));
};

function removeAddressCards() {
  if (locationsAvailable.hasChildNodes()) {
    while (locationsAvailable.firstChild) {
      locationsAvailable.removeChild(locationsAvailable.firstChild);
    }
  }
}

populateCard = (geoResults) => {
  console.log("results are", geoResults);
  console.log("first results is", geoResults[0]);
  // check if a the container has a child node to force re-render of dom
  removeAddressCards();

  const firstAddress = geoResults[0];
  console.log($("#shipping_address_iddd"));
  $(".hideable_shipping_form")
    .find("input[name^='shipping_address']")
    .val(`${firstAddress.formatted_address}`);
  $(".hideable_shipping_form")
    .find("input[name^='shipping_address']")
    .attr("placeholder", `${firstAddress.formatted_address}`);

  $(".hideable_shipping_form")
    .find("input[name^='shipping_address']")
    .attr("disabled", true);

  console.log(firstAddress.geometry.location.lat);
  console.log(firstAddress.geometry.location.lng);
  $(".hideable_shipping_form")
    .find("input[name^='shipping_long']")
    .val(`${firstAddress.geometry.location.lng}`);

  $(".hideable_shipping_form")
    .find("input[name^='shipping_lat']")
    .val(`${firstAddress.geometry.location.lat}`);

  firstAddress.address_components.map((component) => {
    const types = component.types;

    if (types.includes("administrative_area_level_1")) {
      $(".hideable_shipping_form")
        .find("input[name^='shipping_state']")
        .val(`${component.long_name}`);
      $(".hideable_shipping_form")
        .find("input[name^='shipping_state']")
        .attr("placeholder", `${component.long_name}`);

      $(".hideable_shipping_form")
        .find("input[name^='shipping_state']")
        .attr("disabled", true);
    }

    if (types.includes("administrative_area_level_2")) {
      $(".hideable_shipping_form")
        .find("input[name^='shipping_city']")
        .val(`${component.long_name}`);
      $(".hideable_shipping_form")
        .find("input[name^='shipping_city']")
        .attr("placeholder", `${component.long_name}`);

      $(".hideable_shipping_form")
        .find("input[name^='shipping_city']")
        .attr("disabled", true);
    }
  });

  //   geoResults.map((geoResult) => {
  //     // first create the input div container
  //     const addressCard = document.createElement("div");
  //     addressCard.setAttribute("style", "color: whitesmoke !important;");

  //     // then create the input and label elements
  //     const input = document.createElement("input");
  //     const label = document.createElement("label");

  //     // then add materialize classes to the div and input
  //     addressCard.classList.add("card");
  //     input.classList.add("with-gap");

  //     // add attributes to them
  //     label.setAttribute("for", geoResult.place_id);
  //     label.setAttribute("class", "form__label");
  //     label.innerHTML = geoResult.formatted_address;

  //     input.setAttribute("name", "address");
  //     input.setAttribute("type", "checkbox");
  //     input.setAttribute("value", geoResult.formatted_address);
  //     input.setAttribute("id", geoResult.place_id);

  //     // input.addEventListener('click', e => console.log(123));
  //     input.addEventListener("click", () => inputClicked(geoResult));
  //     // finalResult = input.value;
  //     finalResult = geoResult.formatted_address;

  //     addressCard.appendChild(input);
  //     addressCard.appendChild(label);

  //     // console.log(geoResult.formatted_address)

  //     return locationsAvailable.appendChild(addressCard);
  //   });
};

// inputClicked = (result) => {
//   result.address_components.map((component) => {
//     const types = component.types;

//     if (types.includes("postal_code")) {
//       $("postal_code").value = component.long_name;
//     }

//     if (types.includes("locality")) {
//       $("locality").value = component.long_name;
//     }

//     if (types.includes("administrative_area_level_2")) {
//       $("city").value = component.long_name;
//     }

//     if (types.includes("administrative_area_level_1")) {
//       $("state").value = component.long_name;
//     }

//     if (types.includes("point_of_interest")) {
//       $("landmark").value = component.long_name;
//     }
//   });

//   $("address").value = result.formatted_address;

//   // to avoid labels overlapping prefilled contents
//   M.updateTextFields();
//   removeAddressCards();
// };
