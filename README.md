# Cyber Vision HUD System (v11 - Motion Tracker)

A Python-based real-time object detection, motion tracking, and HUD web interface designed to run locally (including Android/Termux environments via Python, OpenCV, and a local HTTP server).

## 🚀 Features
- **Real-Time Object Detection & Tracking:** Powered by MobileNet-SSD Caffe model and centroid tracking.
- **Web-Based HUD UI:** Clean, futuristic cyber-style interface with live FPS counter, latency display, and bounding box overlays.
- **Hardware Controls:** Switch between Front and Back cameras seamlessly, toggle Torch/Flash, and apply a Night Vision filter.
- **Live Terminal Logging & Vault:** View structured log boxes or stream real-time JSON detection metrics directly in the terminal.

---
## 📸 স্ক্রিনশটসমূহ (Screenshots)
### ১. মূল ব্যানার
![Main Banner](images/demo.jpg)

## 📂 প্রজেক্ট ফাইল স্ট্রাকচার (Project Structure)
```text
cyber-vision-tool/
│
├── cyber_vision_v11.py            # মূল পাইথন ব্যাকএন্ড ও CLI ইঞ্জিন
├── face_data.json                 # প্রসেস করা অবজেক্ট ট্র্যাকিংয়ের লকিং ডেটা
├── MobileNetSSD_deploy.prototxt   # Caffe মডেলের আর্কিটেকচার ফাইল
├── MobileNetSSD_deploy.caffemodel # অবজেক্ট ডিটেকশনের প্রাক-প্রশিক্ষিত মডেল
└── README.md                      # টুলসের ডকুমেন্টেশন ফাইল
```

## 🛠️ Prerequisites & Dependencies

Make sure you have Python installed along with the required libraries:

```bash
pip install opencv-python numpy
```
​Note: You will need the MobileNet-SSD model files (MobileNetSSD_deploy.prototxt and MobileNetSSD_deploy.caffemodel) in the same directory for the AI detection engine to run.
## 📦 Installation & Setup
1. Clone or copy the project script into your working directory.
2. Ensure the model files are present.
3. Run the script:
4. python your_script_name.py

## 🕹️ Menu Options
​[1] Start Server & Launch HUD: Launches the local HTTP server on port 8080 and automatically opens the browser interface.
​[2] Stop Background Server: Shuts down the active web server.
​[3] LIVE REAL-TIME JSON STREAM: Streams live detection JSON logs directly in your terminal.
​[4] View Structured Box Log: Displays recent logs nicely formatted inside terminal box frames.
​[5] View Raw JSON Vault: Dumps the entire contents of face_data.json.
​[6] Clear Vault: Deletes the local log database.
​[7] Exit: Safely stops the server and exits the program.
​
## 📱 Termux / Android Support
​If you are running this on an Android device via Termux, ensure you have granted storage permissions and have installed Python and OpenCV properly to leverage local camera streams and termux-open-url.
