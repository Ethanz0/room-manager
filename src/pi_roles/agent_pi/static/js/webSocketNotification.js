import io from 'https://cdn.socket.io/4.7.2/socket.io.esm.min.js';

export const socket = io();

socket.on('admin_announcement', data => {
  console.log('New admin announcement:', data);
  const notificationsDiv = document.getElementById('notifications');
  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-info alert-dismissible fade show';
  alertDiv.setAttribute('role', 'alert');
  const title = data.title || '';
  const type = (data.type || '').toString().toLowerCase();
  const typeClassMap = {
    // Priority
    urgent: 'bg-danger text-white',
    fault: 'bg-danger text-white',
    warning: 'bg-warning text-dark',

    // Category
    information: 'bg-secondary',
    general: 'bg-info text-dark',
    room: 'bg-primary text-white',
    user: 'bg-success text-white',
  };
  const badgeClass = typeClassMap[type] || 'bg-secondary';

  alertDiv.innerHTML = `
    <div class="d-flex justify-content-between align-items-start">
      <div>
        ${title ? `<div><strong>${title}</strong></div>` : ''}
        <div>${data.message || ''}</div>
      </div>
      ${data.type ? `<span class="badge ${badgeClass} ms-2 text-uppercase">${data.type}</span>` : ''}
    </div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  notificationsDiv.appendChild(alertDiv);
});