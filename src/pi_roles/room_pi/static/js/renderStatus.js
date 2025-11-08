export function renderStatus(status) {
    const statusMap = {
        'MAINTENANCE': '<span class="maintenance">Maintenance</span>',
        'AVAILABLE': '<span class="available">Available</span>',
        'RESERVED': '<span class="reserved">Reserved</span>',
        'IN_USE': '<span class="in-use">In Use</span>',
        'FAULT': '<span class="fault">Fault</span>',
    };

    const loading_html = `
        <svg viewBox="25 25 50 50">
            <circle r="20" cy="50" cx="50"></circle>
        </svg>
    `

    const container = document.getElementById('room_status');
    if (!container) return;

    container.innerHTML = `
        <div class="status">
            ${statusMap[status] || loading_html}
        </div>
    `;
}

export function renderUpcomingBookings(bookings) {
    const container = document.getElementById('upcoming_bookings_tbody');
    console.log("Bookings is:")
    console.log(bookings)
    if (!container) return;

    container.innerHTML = bookings.map(booking => {
        const now = new Date();
        const start = new Date(booking.start_time);
        const end = new Date(booking.end_time);
        const createdAt = new Date(booking.created_at);

        // Format date and time for readability
        const startDate = start.toLocaleDateString();
        const startTime = start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const endDate = end.toLocaleDateString();
        const endTime = end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const createdAtDate = createdAt.toLocaleDateString();
        const createdAtTime = createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Determine if the booking has already ended
        const nowTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const isPast = endTime < nowTime;

        return `
            <tr class="${isPast ? 'table-secondary text-muted' : ''}">
            <td><span class="fw-bold">${booking.booking_id}</span></td>
            <td>${booking.user_full_name}</td>
            <td>${booking.user_email}</td>
            <td>
                <div class="d-flex flex-column">
                <small>${createdAtDate}</small>
                <small><time datetime="${createdAt.toISOString()}">${createdAtTime}</time></small>
                </div>
            </td>
            <td>
                <div class="d-flex flex-column">
                <small>${startDate}</small>
                <small><time datetime="${start.toISOString()}">${startTime}</time></small>
                </div>
            </td>
            <td>
                <div class="d-flex flex-column">
                <small>${endDate}</small>
                <small><time datetime="${end.toISOString()}">${endTime}</time></small>
                </div>
            </td>
            </tr>
        `;
    }).join('');
}

export function renderTemperature(temperature) {
    const container = document.getElementById('temperature');

    if (!container) return;

    container.innerHTML = `
        ${temperature !== null ? temperature.toFixed(2) + ' °C' : 'N/A'}
    `;
}

export function renderHumidity(humidity) {
    const container = document.getElementById('humidity');

    if (!container) return;

    container.innerHTML = `
        ${humidity !== null ? humidity.toFixed(2) + ' %' : 'N/A'}
    `;
}

export function renderPressure(pressure) {
    const container = document.getElementById('pressure');

    if (!container) return;
    container.innerHTML = `
        ${pressure !== null ? pressure.toFixed(2) + ' hPa' : 'N/A'}
    `;
}