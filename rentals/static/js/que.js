let queUpdateBtns = $(".update-que");
// console.log(queUpdateBtns);

console.log(user);

for (let i = 0; i < queUpdateBtns.length; i++) {
  queUpdateBtns[i].addEventListener("click", () => {
    console.log(queUpdateBtns[i]);
    let productId = queUpdateBtns[i].dataset.product;
    let action = queUpdateBtns[i].dataset.action;
    let no_of_days = $(`#no_of_days_${productId}`).val();
    currUrl = window.location.pathname;
    console.log(currUrl);
    if (currUrl == "/") {
      if (!no_of_days) {
        console.log("You need to select number of days!");
        // location.reload();
      } else {
        performUpdate(productId, action, no_of_days);
      }
    } else {
      performUpdate(productId, action, no_of_days);
    }
  });
}

function performUpdate(productId, action, no_of_days = null) {
  if (user !== "AnonymousUser") {
    console.log(productId, action, no_of_days);
    $(`#que_modal_response_${productId}`).html('<div id="que_loader"></div>');
    updateUserQue(productId, action, no_of_days);
  }
}

function updateUserQue(productId, action, no_of_days = null) {
  console.log("User is authenticated, sending data");
  var url = "/update-que/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      action: action,
      no_of_days: no_of_days,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(`Data: ${data}`);
      $("#queTotal").load(" #queTotal");
      currUrl = window.location.pathname;
      console.log(currUrl);
      if (currUrl == "/que/") {
        location.reload();
      } else {
        $(`#que_modal_response_${productId}`).html(
          '<span class="modal__text"> Item has been added to your Rental Cart </span>'
        );
      }
    });
}
