function callAPI(endpoint) {
  const token = document.getElementById("token").value;
  const url = window.location.origin + endpoint;

  fetch(url, {
    headers: {
      "Authorization": token
    }
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("response").innerText = JSON.stringify(data, null, 2);
    })
    .catch((err) => {
      document.getElementById("response").innerText = "Error: " + err;
    });
}
