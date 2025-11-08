import QRCode from "https://cdn.jsdelivr.net/npm/qrcode@1.5.3/+esm";

async function fetchQRCodeToken() {
    try {
        const response = await fetch("/login/qr-token");
        if (!response.ok) {
            throw new Error(`Failed to fetch QR code token (status ${response.status})`);
        }
        const data = await response.json();
        return {
            qr_code_token: data.qr_code_token, 
            user_id: data.user_id
        };
    } catch (error) {
        console.error("Error fetching QR code token:", error);
        return null;
    }
}
    
async function displayQRCode() {
    const qrCodeToken = await fetchQRCodeToken();

    if (qrCodeToken === null) {
        return;
    }

    const canvas = document.getElementById("qrcode");
    QRCode.toCanvas(canvas, JSON.stringify(qrCodeToken), { width: 200 });
}

displayQRCode();