async function loginUser() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const msg = document.getElementById("msg");

    if (!email || !password) {
        msg.textContent = "Please fill out all fields.";
        msg.style.color = "red";
        return;
    }

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.message || `Login failed (status ${response.status})`);
        }

        window.location.href = "/dashboard";

    } catch (error) {
        console.error("Error:", error);
        msg.textContent = error.message || "An error occurred during login.";
        msg.style.color = "red";
    }
}

async function qrCodeLogin() {
    window.location.href = "/qr-code-login"
}