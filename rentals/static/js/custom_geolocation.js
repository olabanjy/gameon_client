function handlePermission() {
  navigator.permissions.query({ name: "geolocation" }).then((result) => {
    if (result.state === "granted") {
      report(result.state);
    } else if (result.state === "prompt") {
      report(result.state);
    } else if (result.state === "denied") {
      report(result.state);
    }
    result.addEventListener("change", () => {
      report(result.state);
    });
  });
}

function report(state) {
  console.log(`Permission ${state}`);
  if (state === "denied") {
    console.log("sorry you need location services to access the website");
    window.localStorage.removeItem("loc");
    $("#trigger_location_not_enabled").click();
  } else if (state === "granted") {
    $("#trigger_close_location_not_enabled").click();
    getLocation();
  } else if (state === "prompt") {
    first_time_load = true;
    getLocation();
  }
}

function refreshHomepage() {
  currentPositionLoc = JSON.parse(window.localStorage.getItem("loc"));
  let currentURL = window.location;
  if (currentURL.pathname === "/") {
    if (!window.location.href.includes("?")) {
      window.location.replace(
        window.location.href.split("?")[0] +
          `?loclong=${currentPositionLoc.loclong}&loclat=${currentPositionLoc.loclat}`
      );
    }
  } else if (currentURL.pathname === "/shop/") {
    if (!window.location.href.includes("?")) {
      window.location.replace(
        window.location.href.split("?")[0] +
          `?loclong=${currentPositionLoc.loclong}&loclat=${currentPositionLoc.loclat}`
      );
    }
  }
}

function fetchRegion(position) {
  //  check current city

  fetch(
    `https://maps.googleapis.com/maps/api/geocode/json?latlng=${position.latitude},${position.longitude}&key=AIzaSyAUBoCQ9qfFHOOVqGF7Q0XrhpGl1x6cDHw`
  )
    .then((res) => res.json())
    .then((response) => {
      var addressComp = response.results[0].address_components;
      for (var i = 0; i < addressComp.length; i++) {
        if (addressComp[i].types[0] == "administrative_area_level_1") {
          let region = addressComp[i].short_name;
          if (region === "LA") {
            window.location.replace("/not-available/");
          }
          break;
        }
      }
    });
}

function handleError(error) {
  console.log(error);
  $("#trigger_location_not_enabled").click();
}

function handleSuccess(pos) {
  const position = pos.coords;

  fetchRegion(position);

  let loc = {
    loclong: position.longitude,
    loclat: position.latitude,
  };
  window.localStorage.setItem("loc", JSON.stringify(loc));
  // refresh homepage here
  console.log("refreshing homepage now");
  refreshHomepage();
}

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
      maximumAge: 0,
    });
  } else {
    console.log("location service not enabled");
    $("#trigger_location_not_enabled").click();
  }
}

$(document).ready(function () {
  "use strict";
  handlePermission();
});
