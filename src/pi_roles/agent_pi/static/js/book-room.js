function updateLocalBookingData(bookingID, accessToken, roomID) {
    let bookings = JSON.parse(localStorage.getItem('bookings')) || {};
    bookings[String(bookingID)] = {"accessToken": accessToken, "roomID": roomID};
    localStorage.setItem('bookings', JSON.stringify(bookings));
}

// Makes a request to book the given room ID
async function fetchBookRoom(roomID, date, startTime, endTime) {
    const url = `/bookings`;
    const body = {
        roomID: roomID,
        date: date,
        startTime: startTime,
        endTime: endTime
    };
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });

    if (response.status !== 201) {
        const errorMessage = await response.text();
        throw new Error(errorMessage);
    }

    const data = await response.json();
    return data;
}

// Fetches available rooms for the given date and time range
async function fetchAvailableRooms(date, startTime, endTime) {
    const url = `/rooms/available?date=${encodeURIComponent(date)}&startTime=${encodeURIComponent(startTime)}&endTime=${encodeURIComponent(endTime)}`;

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

// Returns true if startTime is before endTime
function isStartBeforeEnd(startTime, endTime) {
  if (!startTime) {
    return true;
  }
  if (!endTime) {
    return true
  }

  const [startHour, startMinute] = startTime.split(":").map(Number);
  const [endHour, endMinute] = endTime.split(":").map(Number);

  // Convert both to minutes since midnight
  const startTotal = startHour * 60 + startMinute;
  const endTotal = endHour * 60 + endMinute;

  return startTotal < endTotal;
}

// Books the given room ID
async function bookRoom(roomID) {
    const date = document.getElementById('booking-date').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    if (date === "" || startTime === "" || endTime === "") {
        alert("Please fill in all fields.");
        return;
    }

    console.log("Booking room " + roomID);
    
    var data = null;
    try {
        data = await fetchBookRoom(roomID, date, startTime, endTime);
    } catch (error) {
        console.error(error);
        if (error.message == "room unavailable at given time") {
            alert("The selected room is no longer available for the chosen time. Please select a different room or time.");
            return;
        }
        alert("Failed to book room. Please try again later.");
        return;
    }

    updateLocalBookingData(data.bookingID, data.accessToken, roomID);

    alert("Room " + roomID + " sucessfully booked!");
    
    // Remove the booked room from the table
    const row = document.getElementById('room-' + roomID);
    if (row) {
        row.remove();
    }
}

// Displays the given rooms in the available rooms table.
function displayAvailableRooms(rooms) {
    console.log(rooms)
    const table = document.getElementById('available-rooms-table');
    const tableBody = document.getElementById('rooms-table-body');
    const noRoomsMsg = document.getElementById('no-rooms-available');
    const availableRoomsText = document.getElementById('available-rooms-text');
    
    tableBody.innerHTML = '';
    noRoomsMsg.style.display = 'none';
    table.style.display = 'none';
    availableRoomsText.style.display = 'block';

    if (rooms.length === 0) {
        noRoomsMsg.style.display = 'block';
        return;
    }

    table.style.display = 'table';
    rooms.forEach(room => {
        const row = document.createElement('tr');
        row.id = 'room-' + room.id;

        // Create the room name cell
        const roomCell = document.createElement('td');
        roomCell.textContent = room.room_name;
        row.appendChild(roomCell);

        const locationCell = document.createElement('td');
        locationCell.textContent = room.location;
        row.appendChild(locationCell);

        // Capacity cell
        const capacityCell = document.createElement('td');
        capacityCell.textContent = room.capacity;
        row.appendChild(capacityCell);

        // Create the action cell with a "Book" button
        const actionCell = document.createElement('td');
        const button = document.createElement('button');
        button.className = 'primary';
        button.style.width = '100%';
        button.textContent = 'Book';
        button.onclick = () => bookRoom(room.id);
        actionCell.appendChild(button);
        row.appendChild(actionCell);

        // Add the row to the table body
        tableBody.appendChild(row);
    });
}

// Searches for available rooms based on the selected date and time.
async function searchAvailableRooms() {
    const date = document.getElementById('booking-date').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    if (date === "" || startTime === "" || endTime === "") {
        alert("Please fill in all fields.");
        return;
    }

    console.log("Searching for avaiable rooms on " + date + " from " + startTime + " to " + endTime);
    
    var rooms = null;

    try {
        rooms = await fetchAvailableRooms(date, startTime, endTime);
    } catch (error) {
        alert("Failed to find available rooms. Please try again later.");
        console.error(error);
        return;
    }

    displayAvailableRooms(rooms);
}

const today = new Date().toISOString().split("T")[0];
document.getElementById('booking-date').min = today

const startTimeInput = document.getElementById('start-time');
const endTimeInput = document.getElementById('end-time');

var lastAcceptedStartTime = ""
var lastAcceptedEndTime = ""

startTimeInput.onchange = () => {
    endTimeInput.disabled = false;
    const startTime = startTimeInput.value;
    const endTime = document.getElementById('end-time').value;

    if (!isStartBeforeEnd(startTime, endTime)) {
        alert("Start time must be before End time.");
        startTimeInput.value = lastAcceptedStartTime;
        return
    }
    lastAcceptedStartTime = startTime;
}

endTimeInput.onchange = () => {
    const startTime = document.getElementById('start-time').value;
    const endTime = endTimeInput.value;
    if (!isStartBeforeEnd(startTime, endTime)) {
        alert("End time must be after Start time.");
        endTimeInput.value = lastAcceptedEndTime;
        return
    }
    lastAcceptedEndTime = endTime;
}