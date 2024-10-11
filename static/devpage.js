getForm = document.getElementById("getForm");
getItem = document.getElementById("getItem");
result = document.getElementById("result");
resultFrame = document.getElementById("resultIFrame");

getForm.addEventListener("submit", (event) => {
    event.preventDefault();
    fetch("/api/item/" + getForm.name.value + "/get", {
        method: "GET",
    })
    .then((response) => {
        if (response.status === 200) {
            resultFrame.src = '/tpl/itemview/'+ getForm.name.value;
            return response.json();
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
});

getAllForm = document.getElementById("getAllForm");
getAllForm.addEventListener("submit", (event) => {
    event.preventDefault();
    fetch("/api/item/all", {
        method: "GET",
    })
    .then((response) => {
        if (response.status === 200) {
            return response.json();
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
})

createForm = document.getElementById("createForm");
createItem = document.getElementById("createItem");
createForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (createForm.name.value === "") {
        result.innerHTML = "Error: name cannot be empty";
        return;
    }
    fetch("/api/item/" + createForm.name.value + "/create", {
        method: "PUT"
    })
    .then((response) => {
        if (response.status === 200 || response.status === 201) {
            return response;
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
});

updateForm = document.getElementById("updateForm");
updateItem = document.getElementById("updateItem");
updateForm.addEventListener("submit", (event) => {
    event.preventDefault();
    value = updateForm.value.value
    if (updateForm.name.value === "" || value === "") {
        result.innerHTML = "Error: name and value cannot be empty";
        return;
    }
    fetch("/api/item/" + updateForm.name.value + "/update", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: value,
    })
    .then((response) => {
        if (response.status === 204) {
            return "Success (no content)";
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
});

deleteForm = document.getElementById("deleteForm");
deleteItem = document.getElementById("deleteItem");
deleteForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (deleteForm.name.value === "") {
        result.innerHTML = "Error: name cannot be empty";
        return;
    }
    fetch("/api/item/" + deleteForm.name.value + "/delete", {
        method: "DELETE",
    })
    .then((response) => {
        if (response.status === 204) {
            return "Success (no content)";
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
})

uploadForm = document.getElementById("uploadForm");
uploadImage = document.getElementById("uploadImage");
uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (uploadForm.name.value === "") {
        result.innerHTML = "Error: name cannot be empty";
        return;
    }
    formData = new FormData(uploadForm);
    formData.append("upload", uploadForm.upload.files[0]);
    fetch("/api/item/" + uploadForm.name.value + "/image", {
        method: "PUT",
        body: formData,
    })
    .then((response) => {
        if (response.status === 201) {
            return response.json();
        } else {
            return {
                error: "Error",
                status: response.status,
            };
        }
    })
    .then((data) => {
        result.innerHTML = JSON.stringify(data);
    });
})