import base64
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
from multiprocessing import cpu_count
import os
import sys
import threading
time = __import__("time")
webbrowser = __import__("webbrowser")
import cv2
import numpy as np


# ==========================================
# 🎨 COLOR PALETTE & CONFIG
# ==========================================
class Colors:

  RESET = "\033[0m"
  BOLD = "\033[1m"
  RED = "\033[91m"
  GREEN = "\033[92m"
  YELLOW = "\033[93m"
  BLUE = "\033[94m"
  MAGENTA = "\033[95m"
  CYAN = "\033[96m"
  WHITE = "\033[97m"

  B_RED = "\033[1;91m"
  B_GREEN = "\033[1;92m"
  B_YELLOW = "\033[1;93m"
  B_BLUE = "\033[1;94m"
  B_CYAN = "\033[1;96m"
  B_MAGENTA = "\033[1;95m"
  B_WHITE = "\033[1;97m"


DATA_FILE = "face_data.json"
PORT = 8080
server_instance = None
is_server_running = False

# MobileNet-SSD VOC Classes
CLASSES = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]

LABEL_MAP = {
    "person": "HUMAN / PERSON",
    "car": "CAR / VEHICLE",
    "motorbike": "BIKE / MOTORCYCLE",
    "bus": "BUS / HEAVY VEHICLE",
    "bicycle": "BICYCLE",
    "bird": "BIRD / POULTRY",
    "cat": "CAT",
    "dog": "DOG",
    "cow": "COW / CATTLE",
    "train": "TRAIN",
    "aeroplane": "AEROPLANE",
}

# Models
PROTOTXT = "MobileNetSSD_deploy.prototxt"
MODEL = "MobileNetSSD_deploy.caffemodel"

dnn_net = None
try:
  if os.path.exists(PROTOTXT) and os.path.exists(MODEL):
    dnn_net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
except Exception:
  dnn_net = None

# Tracked Objects Cache for Centroid Tracking
previous_objects = {}  # {id: (cx, cy)}
next_object_id = 1


# ==========================================
# 🌐 FRONTEND WEB HUD UI (MOTION TRACKING)
# ==========================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Vision HUD System v11 - Motion Tracker</title>
    <style>
        body {
            background-color: #030712;
            color: #00f0ff;
            font-family: 'Courier New', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 10px;
            box-sizing: border-box;
        }
        h1 { color: #00ff66; text-shadow: 0 0 15px #00ff66; text-align: center; font-size: 15px; margin-bottom: 6px; }
        .speed-bar {
            background: #0d1527;
            border: 1px solid #00f0ff;
            color: #ffbb00;
            padding: 6px 14px;
            font-size: 11px;
            border-radius: 20px;
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(0,240,255,0.3);
            font-weight: bold;
        }
        .camera-box {
            position: relative;
            border: 2px solid #00f0ff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
            width: 100%;
            max-width: 420px;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        /* Fixed Night Mode Filter Style */
        .camera-box.night-mode video {
            filter: brightness(1.6) contrast(1.3) sepia(1) hue-rotate(70deg);
        }
        video { width: 100%; height: auto; display: block; object-fit: cover; transition: filter 0.3s ease; }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        .controls {
            margin-top: 15px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            width: 100%;
            max-width: 420px;
        }
        button {
            background: #0f172a;
            color: #00f0ff;
            border: 1px solid #00f0ff;
            padding: 10px;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
        }
        .btn-active { background: #00ff66 !important; color: #000 !important; }
        .btn-flash { background: #ffbb00 !important; color: #000 !important; }
        #status { margin-top: 10px; color: #ffcc00; font-size: 11px; text-align: center; }
    </style>
</head>
<body>

    <h1>[ CYBER VISION HUD v11 - OBJECT LOCK & MOTION TRACKING ]</h1>
    <div class="speed-bar" id="speedMeter">⚡ Target Lock System: Ready | FPS: 0</div>

    <div class="camera-box" id="camContainer">
        <video id="webcam" autoplay playsinline muted></video>
        <canvas id="overlay"></canvas>
    </div>

    <div class="controls">
        <button id="btnFront" onclick="switchCamera('user')">📷 Front Cam</button>
        <button id="btnBack" onclick="switchCamera('environment')" class="btn-active">📸 Back Cam</button>
        <button id="btnFlash" onclick="toggleFlash()">🔦 Torch: OFF</button>
        <button id="btnNight" onclick="toggleNightMode()">🌙 Night Filter</button>
    </div>

    <div id="status">Connecting to Motion Tracking Engine...</div>

    <script>
        let video = document.getElementById('webcam');
        let canvas = document.getElementById('overlay');
        let ctx = canvas.getContext('2d');
        let currentFacingMode = 'environment';
        let currentStream = null;
        let isFlashOn = false;
        let isNight = false;
        let lastFrameTime = Date.now();
        let isProcessing = false;

        async function startCamera(facingMode) {
            if (currentStream) {
                currentStream.getTracks().forEach(track => track.stop());
                currentStream = null;
            }

            // Fixed Constraints for seamless Front/Back switching
            let constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            try {
                currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                video.srcObject = currentStream;
                document.getElementById('status').innerText = "Target Locking & Motion Tracking Active";
                document.getElementById('status').style.color = "#00ff66";
            } catch (err) {
                // Fallback if ideal resolution fails
                try {
                    currentStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: facingMode } });
                    video.srcObject = currentStream;
                    document.getElementById('status').innerText = "Target Locking Active (Fallback Mode)";
                    document.getElementById('status').style.color = "#00ff66";
                } catch (e) {
                    document.getElementById('status').innerText = "Camera Access Error!";
                    document.getElementById('status').style.color = "#ff3333";
                }
            }
        }

        function switchCamera(mode) {
            currentFacingMode = mode;
            isFlashOn = false;
            document.getElementById('btnFlash').innerText = "🔦 Torch: OFF";
            document.getElementById('btnFlash').classList.remove('btn-flash');
            document.getElementById('btnFront').classList.toggle('btn-active', mode === 'user');
            document.getElementById('btnBack').classList.toggle('btn-active', mode === 'environment');
            startCamera(mode);
        }

        async function toggleFlash() {
            if (!currentStream) return;
            const track = currentStream.getVideoTracks()[0];
            const capabilities = track.getCapabilities ? track.getCapabilities() : {};
            if (capabilities.torch) {
                isFlashOn = !isFlashOn;
                await track.applyConstraints({ advanced: [{ torch: isFlashOn }] });
                document.getElementById('btnFlash').innerText = isFlashOn ? "🔦 Torch: ON" : "🔦 Torch: OFF";
                document.getElementById('btnFlash').classList.toggle('btn-flash', isFlashOn);
            } else {
                alert("Torch not supported on this lens or active camera!");
            }
        }

        function toggleNightMode() {
            isNight = !isNight;
            document.getElementById('camContainer').classList.toggle('night-mode', isNight);
            document.getElementById('btnNight').classList.toggle('btn-active', isNight);
        }

        function captureAndProcess() {
            if (video.readyState === 4 && !isProcessing) {
                isProcessing = true;

                let processWidth = 480;
                let processHeight = 360;

                let tempCanvas = document.createElement('canvas');
                tempCanvas.width = processWidth;
                tempCanvas.height = processHeight;
                let tempCtx = tempCanvas.getContext('2d');
                tempCtx.drawImage(video, 0, 0, processWidth, processHeight);

                let base64Image = tempCanvas.toDataURL('image/jpeg', 0.6);
                let startTime = Date.now();

                fetch('/api/process_opencv', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: base64Image,
                        camera_mode: currentFacingMode === 'user' ? 'Front Cam' : 'Back Cam',
                        torch_status: isFlashOn ? 'ON' : 'OFF'
                    })
                })
                .then(res => res.json())
                .then(data => {
                    isProcessing = false;
                    let duration = Date.now() - startTime;
                    let fps = Math.round(1000 / (Date.now() - lastFrameTime));
                    lastFrameTime = Date.now();

                    document.getElementById('speedMeter').innerText = `⚡ Tracking Latency: ${duration} ms | FPS: ${fps}`;

                    canvas.width = video.clientWidth;
                    canvas.height = video.clientHeight;
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    let scaleX = canvas.width / processWidth;
                    let scaleY = canvas.height / processHeight;

                    if (data.detections && data.detections.length > 0) {
                        data.detections.forEach(item => {
                            if (item.w > 0) {
                                drawMotionHUD(item.x * scaleX, item.y * scaleY, item.w * scaleX, item.h * scaleY, item.label, item.confidence, item.range, item.track_id);
                            }
                        });
                    }
                })
                .catch(() => { isProcessing = false; });
            }
        }

        function drawMotionHUD(x, y, w, h, label, conf, range, trackId) {
            // Main Adaptive Box
            ctx.strokeStyle = '#00ff66';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, w, h);

            // Crosshair Centroid (Motion Tracker Lock)
            let cx = x + w / 2;
            let cy = y + h / 2;
            ctx.strokeStyle = '#ff0055';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
            ctx.moveTo(cx - 10, cy); ctx.lineTo(cx + 10, cy);
            ctx.moveTo(cx, cy - 10); ctx.lineTo(cx, cy + 10);
            ctx.stroke();

            // Lock Edges HUD
            let len = Math.min(w, h) * 0.20;
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 3;

            ctx.beginPath();
            ctx.moveTo(x, y + len); ctx.lineTo(x, y); ctx.lineTo(x + len, y);
            ctx.moveTo(x + w - len, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + len);
            ctx.moveTo(x, y + h - len); ctx.lineTo(x, y + h); ctx.lineTo(x + len, y + h);
            ctx.moveTo(x + w - len, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - len);
            ctx.stroke();

            // Labels
            ctx.fillStyle = '#00ff66';
            ctx.font = 'bold 11px Courier New';
            let mainText = `[ ID:#${trackId} | ${label.toUpperCase()} ${conf} ]`;
            let subText = `[ LOCKED | ${range} ]`;

            ctx.fillText(mainText, x, y - 18 > 15 ? y - 18 : y + 15);
            ctx.fillStyle = '#ffbb00';
            ctx.fillText(subText, x, y - 5 > 28 ? y - 5 : y + 28);
        }

        setInterval(captureAndProcess, 90);
        window.onload = () => startCamera('environment');
    </script>
</body>
</html>
"""


# ==========================================
# ⚙️ BACKEND SERVER ENGINE (CENTROID TRACKER)
# ==========================================
class RequestHandler(BaseHTTPRequestHandler):

  def log_message(self, format, *args):
    return

  def do_GET(self):
    if self.path == "/":
      self.send_response(200)
      self.send_header("Content-type", "text/html; charset=utf-8")
      self.end_headers()
      self.wfile.write(HTML_PAGE.encode("utf-8"))
    else:
      self.send_response(404)
      self.end_headers()

  def do_POST(self):
    if self.path == "/api/process_opencv":
      start_proc_time = time.time()
      content_length = int(self.headers["Content-Length"])
      post_data = self.rfile.read(content_length)
      data = json.loads(post_data.decode("utf-8"))

      processed_payload = process_frame_with_ai(
          data.get("image"),
          data.get("camera_mode"),
          data.get("torch_status"),
          start_proc_time,
      )
      save_face_log(processed_payload)

      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps(processed_payload).encode("utf-8"))


def calculate_distance_range(box_area, frame_area):
  ratio = box_area / frame_area
  if ratio > 0.20:
    return "SHORT-RANGE"
  elif ratio > 0.04:
    return "MID-RANGE"
  else:
    return "LONG-RANGE"


def track_and_assign_id(cx, cy):
  global previous_objects, next_object_id
  assigned_id = None
  min_dist = 60  # Tracking Distance Threshold (px)

  for obj_id, (pcx, pcy) in previous_objects.items():
    dist = math.hypot(cx - pcx, cy - pcy)
    if dist < min_dist:
      assigned_id = obj_id
      min_dist = dist
      break

  if assigned_id is None:
    assigned_id = next_object_id
    next_object_id += 1

  return assigned_id


def process_frame_with_ai(base64_str, cam_mode, torch_status, start_proc_time):
  global previous_objects
  try:
    header, encoded = base64_str.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    (h, w) = frame.shape[:2]
    frame_area = float(h * w)
    detections_list = []
    current_frame_objects = {}

    if dnn_net is not None:
      blob = cv2.dnn.blobFromImage(
          cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5
      )
      dnn_net.setInput(blob)
      detections = dnn_net.forward()

      for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.25:
          idx = int(detections[0, 0, i, 1])
          raw_label = CLASSES[idx] if idx < len(CLASSES) else "object"
          display_label = LABEL_MAP.get(raw_label, raw_label)

          # Auto-Sized Coordinates
          box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
          (startX, startY, endX, endY) = box.astype("int")

          # Bound constraints
          startX, startY = max(0, startX), max(0, startY)
          endX, endY = min(w, endX), min(h, endY)

          bw = endX - startX
          bh = endY - startY
          box_area = float(bw * bh)

          if bw > 10 and bh > 10:
            # Centroid calculation for motion tracking
            cx = int(startX + bw / 2)
            cy = int(startY + bh / 2)

            track_id = track_and_assign_id(cx, cy)
            current_frame_objects[track_id] = (cx, cy)

            range_status = calculate_distance_range(box_area, frame_area)

            detections_list.append({
                "x": int(startX),
                "y": int(startY),
                "w": int(bw),
                "h": int(bh),
                "label": display_label,
                "confidence": f"{int(confidence * 100)}%",
                "range": range_status,
                "track_id": track_id,
            })

    previous_objects = current_frame_objects
    proc_latency = round((time.time() - start_proc_time) * 1000, 2)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "MobileNet-SSD Motion Tracker AI",
        "speed_meter": {
            "processing_time": f"{proc_latency} ms",
            "fps_estimate": (
                round(1000 / proc_latency, 1) if proc_latency > 0 else 30.0
            ),
        },
        "hardware_state": {"camera_mode": cam_mode, "torch": torch_status},
        "detection_metrics": {
            "total_detected": len(detections_list),
            "has_target": len(detections_list) > 0,
        },
        "detections": (
            detections_list
            if detections_list
            else [{
                "x": 0,
                "y": 0,
                "w": 0,
                "h": 0,
                "label": "none",
                "confidence": "0%",
                "range": "N/A",
                "track_id": 0,
            }]
        ),
    }
  except Exception as e:
    return {"error": str(e)}


def save_face_log(entry):
  logs = []
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
    except:
      logs = []

  entry["log_id"] = len(logs) + 1
  logs.append(entry)
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(logs, f, indent=4, ensure_ascii=False)


# ==========================================
# 🚀 LAUNCHER & MENU
# ==========================================
def launch_browser_immediately():
  url = f"http://localhost:{PORT}"
  print(
      f"\n{Colors.B_CYAN}[🚀] Opening Browser on localhost:{PORT}...{Colors.RESET}"
  )
  time.sleep(0.5)
  exit_code = os.system(f"termux-open-url {url}")
  if exit_code != 0:
    webbrowser.open(url)


def start_server():
  global server_instance, is_server_running
  if is_server_running:
    print(f"\n{Colors.B_YELLOW}[!] Server is ALREADY RUNNING!{Colors.RESET}")
    launch_browser_immediately()
    return

  try:
    server_instance = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    threading.Thread(target=server_instance.serve_forever, daemon=True).start()
    is_server_running = True
    print(
        f"\n{Colors.B_GREEN}[✓] Motion Tracking Engine Server Launched!{Colors.RESET}"
    )
    launch_browser_immediately()
  except Exception as e:
    print(f"\n{Colors.B_RED}[!] Error: {e}{Colors.RESET}")


def stop_server():
  global server_instance, is_server_running
  if not is_server_running:
    print(f"\n{Colors.B_YELLOW}[!] Server is not running!{Colors.RESET}")
    return
  if server_instance:
    server_instance.shutdown()
    server_instance.server_close()
    is_server_running = False
    print(f"\n{Colors.B_RED}[✓] Server Stopped!{Colors.RESET}")


def clear_screen():
  os.system("cls" if os.name == "nt" else "clear")


def print_banner():
  C = Colors
  server_status = (
      f"{C.B_GREEN}[ RUNNING ]{C.RESET}"
      if is_server_running
      else f"{C.B_RED}[ STOPPED ]{C.RESET}"
  )
  banner = f"""
{C.B_CYAN}╔═════════════════════════════════════════════════════════════╗{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ██████╗ ███████╗████████╗███████╗ ██████╗████████╗     {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝     {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ██║  ██║█████╗     ██║   █████╗  ██║        ██║        {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║        {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║        {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_GREEN}     ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝        {C.B_CYAN}║{C.RESET}
{C.B_CYAN}╠═════════════════════════════════════════════════════════════╣{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_YELLOW}[+] Status         :{C.RESET} {server_status:<43}       {C.B_CYAN}║{C.RESET}
{C.B_CYAN}║{C.RESET} {C.B_YELLOW}[+] Mode           :{C.RESET} {C.B_GREEN}Auto-Sized Object Lock & Motion Tracker{C.RESET}{C.B_CYAN}║{C.RESET}
{C.B_CYAN}╚═════════════════════════════════════════════════════════════╝{C.RESET}
"""
  print(banner)


def show_menu():
  print_banner()
  C = Colors
  print(
      f" {C.B_YELLOW}[1]{C.RESET} {C.B_WHITE}Start Server & Launch HUD"
      f" (v11 Motion Tracker){C.RESET}"
  )
  print(f" {C.B_YELLOW}[2]{C.RESET} {C.B_WHITE}Stop Background Server{C.RESET}")
  print(
      f" {C.B_YELLOW}[3]{C.RESET} {C.B_GREEN}⚡ LIVE REAL-TIME JSON"
      f" STREAM{C.RESET}"
  )
  print(
      f" {C.B_YELLOW}[4]{C.RESET} {C.B_CYAN}View Structured Box Log{C.RESET}"
  )
  print(f" {C.B_YELLOW}[5]{C.RESET} {C.B_CYAN}View Raw JSON Vault{C.RESET}")
  print(f" {C.B_YELLOW}[6]{C.RESET} {C.B_RED}Clear Vault{C.RESET}")
  print(f" {C.B_YELLOW}[7]{C.RESET} {C.B_MAGENTA}Exit{C.RESET}\n")


def main():
  clear_screen()
  while True:
    show_menu()
    choice = (
        input(f"{Colors.B_YELLOW}Select Option (1-7) ► {Colors.RESET}").strip()
    )
    if choice == "1":
      start_server()
    elif choice == "2":
      stop_server()
    elif choice == "3":
      os.system("clear")
      print(
          f"{Colors.B_GREEN}[*] Real-Time Stream (Ctrl+C to exit)...{Colors.RESET}"
      )
      try:
        while True:
          if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
              logs = json.load(f)
              if logs:
                print(
                    f"{Colors.GREEN}{json.dumps(logs[-1], indent=2, ensure_ascii=False)}{Colors.RESET}"
                )
          time.sleep(1)
      except KeyboardInterrupt:
        pass
    elif choice == "4":
      if os.path.exists(DATA_FILE):
        try:
          with open(DATA_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
          if logs:
            for item in logs[-5:]:
              print(f"{Colors.GREEN}╔══════════════════════════════════════════╗{Colors.RESET}")
              print(f"║ Timestamp   : {item.get('timestamp', 'N/A'):<27} ║")
              print(f"║ Engine      : {item.get('engine', 'N/A'):<27} ║")
              total_det = item.get('detection_metrics', {}).get('total_detected', 0)
              print(f"║ Total Found : {str(total_det):<27} ║")
              print(f"{Colors.GREEN}╚══════════════════════════════════════════╝{Colors.RESET}\n")
          else:
            print(f"{Colors.B_YELLOW}[!] Vault is empty.{Colors.RESET}")
        except Exception as e:
          print(f"{Colors.B_RED}[!] Error reading vault: {e}{Colors.RESET}")
      else:
        print(f"{Colors.B_RED}[!] Vault Empty.{Colors.RESET}")
    elif choice == "5":
      if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
          print(f"{Colors.GREEN}{json.dumps(json.load(f), indent=2)}{Colors.RESET}")
      else:
        print(f"{Colors.B_RED}[!] Vault Empty.{Colors.RESET}")
    elif choice == "6":
      if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        print(f"\n{Colors.B_RED}[✓] Cleared!{Colors.RESET}")
    elif choice == "7":
      if is_server_running:
        stop_server()
      sys.exit()
    input(
        f"\n{Colors.B_CYAN}Press [{Colors.B_YELLOW}Enter{Colors.B_CYAN}] to"
        f" continue...{Colors.RESET}"
    )
    clear_screen()


if __name__ == "__main__":
  main()
