import jsQR from "https://cdn.skypack.dev/jsqr";

async function postQRCodeLogin(userID, token) {
    const url = `/qrcode-login`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userID, token })
    });

    if (response.status !== 200) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
}

async function qrCodeLogin(userID, token) {
    try {
        await postQRCodeLogin(userID, token)
        console.log("QR Code login sucessful!")
        return true;
    } catch (error) {
        console.log("Failed to QR Code login: " + error)
    }
    return false;
}

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

async function startScanner() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
    });
    video.srcObject = stream;
    await video.play();
    await requestAnimationFrame(scanFrame);
  } catch (err) {
    console.error("Camera access denied:", err);
    alert("Camera access is denied. QR code login unavailable.")
  }
}

async function attemptQRCodeLogin(code) {
  const rawCodeData = code
  console.log("QR Code:", rawCodeData);

  var codeData = null
  try {
    codeData = JSON.parse(rawCodeData)
  } catch(error) {
    console.log("Failed to decode JSON data: " + codeData)
    return false
  }
  const userID = codeData.user_id
  const token = codeData.qr_code_token

  if (userID == undefined) {
    return false
  }
  if (token == undefined) {
    return false
  }

  const success = await qrCodeLogin(userID, token)
  if (!success) {
    alert("Login failed. Please try again later.")
    return false
  }
  return true
}

async function scanFrame() {
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);
    if (code) {
      const rawCodeData = code.data
      console.log("QR Code:", rawCodeData);

      const success = await attemptQRCodeLogin(rawCodeData)
      if (success) {
        window.location.href = "/dashboard";
        return
      }
    }
  }
  await requestAnimationFrame(scanFrame);
}

startScanner();