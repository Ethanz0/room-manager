function goToBookRoom() {
    window.location.href = "/book-room";
}

function goToBookedRooms() {
    window.location.href = "/booked-rooms";
}

function goToManageRooms() {
    window.location.href = "/manage-rooms";
}

function logoutUser() {
    fetch("/logout", { method: "POST" })
        .then(response => {
            if (response.ok) {
                window.location.href = "/login";
            } else {
                document.getElementById("msg").textContent = "Logout failed. Try again.";
                document.getElementById("msg").style.color = "red";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            const msg = document.getElementById("msg");
            msg.textContent = "An error occurred while logging out.";
            msg.style.color = "red";
        });
}