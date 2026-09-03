const API_URL = "http://localhost:5000/api/documents";


async function loadDocuments() {
    try {
        const response = await fetch(API_URL);
        const documents = await response.json();

        const container = document.getElementById("documents");

        container.innerHTML = "";

        if (documents.length === 0) {
            container.innerHTML = "<p>No documents found.</p>";
            return;
        }

        documents.forEach(doc => {
            const div = document.createElement("div");

            div.className = "document";

            div.innerHTML = `
                <h3>${doc.name}</h3>
                <p><strong>Category:</strong> ${doc.category || ""}</p>
                <p>${doc.description || ""}</p>
                <p><strong>File:</strong> ${doc.file_name || "No file"}</p>
                <button
                    class="delete-button"
                    onclick="deleteDocument(${doc.id})">
                    Delete
                </button>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        console.error("Failed to load documents:", error);
    }
}


async function addDocument() {

    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    const description = document.getElementById("description").value;
    const file = document.getElementById("file").files[0];

    if (!name) {
        alert("Please enter a document name.");
        return;
    }

    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();

    formData.append("name", name);
    formData.append("category", category);
    formData.append("description", description);
    formData.append("file", file);

    try {

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        if (response.ok) {

            document.getElementById("name").value = "";
            document.getElementById("category").value = "";
            document.getElementById("description").value = "";
            document.getElementById("file").value = "";

            loadDocuments();

        } else {
            const error = await response.json();
            alert(error.error || "Failed to add document.");
        }

    } catch (error) {
        console.error("Failed to add document:", error);
        alert("Failed to connect to the server.");
    }
}


async function deleteDocument(id) {

    const response = await fetch(`${API_URL}/${id}`, {
        method: "DELETE"
    });

    if (response.ok) {
        loadDocuments();
    } else {
        alert("Failed to delete document.");
    }
}


loadDocuments();