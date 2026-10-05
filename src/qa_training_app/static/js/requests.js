const requestsElement = document.getElementById("requests");
const form = document.getElementById("request-form");
const errorElement = document.getElementById("error");
const usernameElement = document.getElementById("current-username");
const logoutButton = document.getElementById("logout-button");

let currentUser = null;

async function loadCurrentUser() {
    try {
        currentUser = await apiRequest("/api/v1/auth/me");
        usernameElement.textContent = currentUser.username;
    } catch {
        window.location.href = "/login";
    }
}

function renderEmptyState() {
    requestsElement.innerHTML = `
        <p class="empty-state" data-testid="empty-state">Заявок пока нет.</p>
    `;
}

function renderRequest(request) {
    const element = document.createElement("article");
    const isOwner = request.author_id === currentUser.id;

    element.className = "request";
    element.setAttribute("data-testid", "request-card");
    element.setAttribute("data-request-id", String(request.id));

    element.innerHTML = `
        <h3 class="request-title" data-testid="request-title">${escapeHtml(request.title)}</h3>
        <p class="request-description" data-testid="request-description">${escapeHtml(request.description)}</p>
        <div class="request-meta" data-testid="request-author">
            Автор: ${escapeHtml(request.author_username)}
        </div>
        ${
            isOwner
                ? `
                    <div class="request-actions">
                        <button
                            type="button"
                            class="danger delete-button"
                            data-testid="delete-request-button"
                            data-id="${request.id}"
                        >
                            Удалить
                        </button>
                    </div>
                `
                : ""
        }
    `;

    return element;
}

async function loadRequests() {
    try {
        const requests = await apiRequest("/api/v1/requests");

        requestsElement.innerHTML = "";

        if (requests.length === 0) {
            renderEmptyState();
            return;
        }

        for (const request of requests) {
            requestsElement.appendChild(renderRequest(request));
        }
    } catch (error) {
        if (error.message === "Not authenticated") {
            window.location.href = "/login";
            return;
        }

        errorElement.textContent = error.message;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorElement.textContent = "";
    setSubmitting(form, true);

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;

    try {
        await apiRequest("/api/v1/requests", {
            method: "POST",
            body: JSON.stringify({ title, description }),
        });

        form.reset();
        await loadRequests();
    } catch (error) {
        errorElement.textContent = error.message;
    } finally {
        setSubmitting(form, false);
    }
});

requestsElement.addEventListener("click", async (event) => {
    const button = event.target.closest(".delete-button");

    if (!button) {
        return;
    }

    try {
        await apiRequest(`/api/v1/requests/${button.dataset.id}`, {
            method: "DELETE",
        });

        await loadRequests();
    } catch (error) {
        errorElement.textContent = error.message;
    }
});

logoutButton.addEventListener("click", async () => {
    try {
        await apiRequest("/api/v1/auth/logout", {
            method: "POST",
        });

        window.location.href = "/login";
    } catch (error) {
        errorElement.textContent = error.message;
    }
});

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}

async function init() {
    await loadCurrentUser();

    if (currentUser) {
        await loadRequests();
    }
}

init();
