import { renderStatus } from './renderStatus.js';

const fetch_api = async () => {
  const res = await fetch("/api/status");
  const data = await res.json();
  console.log("Room Status via /api/status:", data);
  // renderStatus(data["room_status"]);
}

// Initial fetch
(async () => {
  await fetch_api();
})();

// Fetch every 10 seconds
setInterval(async () => {
  await fetch_api();
}, 10000);
