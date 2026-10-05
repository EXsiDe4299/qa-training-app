async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message = data?.detail || "Request failed";
        throw new Error(message);
    }

    return data;
}

function setSubmitting(form, isSubmitting) {
    const submitButton = form.querySelector('button[type="submit"]');

    if (submitButton) {
        submitButton.disabled = isSubmitting;
    }
}
