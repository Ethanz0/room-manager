import { socket } from './webSocketNotification.js';
import { renderStatus, renderUpcomingBookings, renderTemperature, renderHumidity, renderPressure } from './renderStatus.js';

socket.on('status_update', data => {
  console.log('New status:', data);
  // Update your DOM here
  if (data["room_status"] || data["room_status"] === null) {
    renderStatus(data["room_status"]);
  }
  if (data["temperature"]) {
    renderTemperature(data["temperature"]);
  }

  if (data["humidity"]) {
    renderHumidity(data["humidity"]);
  }

  if (data["pressure"]) {
    renderPressure(data["pressure"]);
  }

  if (data["upcoming_bookings"]) {
    renderUpcomingBookings(data["upcoming_bookings"]);
  }
}); { }
