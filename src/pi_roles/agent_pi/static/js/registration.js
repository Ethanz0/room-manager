function registerUser() {
    const firstname = document.getElementById("firstname").value.trim();
    const lastname = document.getElementById("lastname").value.trim();
    const role = document.getElementById("role").value;
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const msg = document.getElementById("msg");

    if (!firstname || !lastname || !role || !email || !password) {
        msg.textContent = "Please fill out all fields.";
        msg.style.color = "red";
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        msg.textContent = "Please enter a valid email address.";
        msg.style.color = "red";
        return;
    }


    fetch("/registration", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firstname, lastname, role, email, password })
    })
        .then(async (response) => {
            const data = await response.json();

            if (!response.ok) {
                msg.textContent = data.message || "Registration failed.";
                msg.style.color = "red";
                return;
            }

            msg.textContent = data.message || "Registration successful!";
            msg.style.color = "green";

            setTimeout(() => {
                window.location.href = "/login";
            }, 1500);
        })
        .catch((err) => {
            console.error("Error:", err);
            msg.style.color = "red";
            msg.textContent = "An error occurred during registration.";
        });
}