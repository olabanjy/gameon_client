var cartTotalEl = $("#cartTotal");

let updateBtns = $(".update-cart");

let user = $("#currUser").val();

for (let i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener("click", () => {
    let productId = updateBtns[i].dataset.product;
    let action = updateBtns[i].dataset.action;
    if (user === "AnonymousUser") {
      addCookieItem(productId, action);
    } else {
      updateUserOrder(productId, action);
    }
  });
}

function addCookieItem(productId, action) {
  console.log("User is not authenticated", action);

  if (action == "add") {
    if (cart[productId] == undefined) {
      cart[productId] = { quantity: 1 };
    } else {
      cart[productId]["quantity"] += 1;
    }
  }

  if (action == "remove-single") {
    cart[productId]["quantity"] -= 1;
    if (cart[productId]["quantity"] < 1) {
      delete cart[productId];
    }
  }

  if (action == "remove") {
    delete cart[productId];
  }

  console.log("Cart", cart);
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
  $("#cartTotal").load(" #cartTotal");
  currUrl = window.location.href;
  console.log(currUrl);
  if (currUrl.indexOf("/shop/cart/") > -1) {
    location.reload();
  } else {
    $("#btn_atc_" + productId).click();
  }
}

function updateUserOrder(productId, action) {
  console.log("User is authenticated, sending data");
  var url = "/shop/update-item/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(`Data: ${data}`);
      // location.reload();
      $("#cartTotal").load(" #cartTotal");
      currUrl = window.location.href;
      console.log(currUrl);
      if (currUrl.indexOf("/shop/cart/") > -1) {
        location.reload();
      } else {
        $("#btn_atc_" + productId).click();
      }
    });
}
