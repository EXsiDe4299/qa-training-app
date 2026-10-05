const form = document.getElementById("login-form");
const errorElement = document.getElementById("error");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorElement.textContent = "";
    setSubmitting(form, true);

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        await apiRequest("/api/v1/auth/login", {
            method: "POST",
            body: JSON.stringify({ username, password }),
        });

        window.location.href = "/requests";
    } catch (error) {
        errorElement.textContent = error.message;
        setSubmitting(form, false);
    }
});
