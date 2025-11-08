// Makes a request to book the given room ID
async function fetchCancelBooking(bookingID) {
    const url = `/bookings/${bookingID}`;

    const response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
}

// Fetches available rooms for the given date and time range
async function fetchBookedRooms() {
    const url = `/bookings`;

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
}

// Retrieves the access token for the given booking ID from local storage
function getBookingData(bookingID) {
    return JSON.parse(localStorage.getItem("bookings"))[bookingID];
}

// Makes a request to check-in to the given booking ID
async function fetchCheckIn(bookingID) {
    const url = `/bookings/${bookingID}/check-in`;
    const accessToken = getBookingData(bookingID).accessToken;
    const roomID = getBookingData(bookingID).roomID;

    const response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            accessToken: accessToken,
            roomID: roomID
        })
    });

    if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(errorMessage);
    }
}

async function checkIn(bookingID) {
    console.log("Checking in to booking " + bookingID);
    try {
        await fetchCheckIn(bookingID);
    } catch (error) {
        console.error(error);
        if (error.message == "not ready for check-in") {
            alert("You can only check in within 15 minutes of your booking start time.");
            return;
        }
        alert("Failed to check in. Please try again later.");
        return;
    }
    document.getElementById('check-in-button-' + bookingID).remove();
    alert("Checked in successfully!");
}

// Cancels the given booking ID
async function cancelBooking(bookingID) {
    console.log("Cancelling booking " + bookingID);

    try {
        await fetchCancelBooking(bookingID);
    } catch (error) {
        alert("Failed to cancel room booking. Please try again later.");
        console.error(error);
        return;
    }

    alert("Booking sucessfully cancelled!");
    
    // Remove the cancelled room from the table
    document.getElementById('booking-' + bookingID).remove();;
}

// Displays the given rooms in the available rooms table.
function displayBookedRooms(rooms) {
    // Get the table body element
    const tableBody = document.getElementById('rooms-table-body');

    // Clear existing rows
    tableBody.innerHTML = '';

    // Populate the table with booked rooms
    rooms.forEach(booking => {
        // Create a new row
        const row = document.createElement('tr');
        row.id = 'booking-' + booking.booking_id;

        // Room location
        const roomCell = document.createElement('td');
        roomCell.textContent = booking.room_name;
        row.appendChild(roomCell);

        // Location
        const locationCell = document.createElement('td');
        locationCell.textContent = booking.location;
        row.appendChild(locationCell);

        // Booking date
        const dateCell = document.createElement('td');
        dateCell.textContent = booking.booking_date;
        row.appendChild(dateCell);

        // Start time
        const startCell = document.createElement('td');
        startCell.textContent = booking.start_time;
        row.appendChild(startCell);

        // End time
        const endCell = document.createElement('td');
        endCell.textContent = booking.end_time;
        row.appendChild(endCell);

        // Action buttons
        const actionCell = document.createElement('td');
        const actionDiv = document.createElement('div');
        actionDiv.className = 'action-buttons';

        // Checkin button
        if (booking.checked_in == false) {
            const checkInButton = document.createElement('button');
            checkInButton.className = 'primary';
            checkInButton.id = 'check-in-button-' + booking.booking_id;
            checkInButton.textContent = 'Check In';
            checkInButton.onclick = () => checkIn(booking.booking_id);
            actionDiv.appendChild(checkInButton);
        }

        actionCell.appendChild(actionDiv);

        // Cancel button
        const cancelButton = document.createElement('button');
        cancelButton.className = 'danger';
        cancelButton.textContent = 'Cancel';
        cancelButton.onclick = () => cancelBooking(booking.booking_id);

        actionDiv.appendChild(cancelButton);
        row.appendChild(actionCell);

        // Append the row to the table
        tableBody.appendChild(row);
    });
}

async function init() {
    var rooms = null;
    try {
        rooms = await fetchBookedRooms();
    } catch (error) {
        alert("Failed to get booked rooms. Please try again later.");
        console.error(error);
        return;
    }
    displayBookedRooms(rooms);
}

init();