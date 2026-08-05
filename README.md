# 🎯 Cyber Vision HUD System v11 - Redmi Edition

## 📝 বিবরণ (Description)
**Cyber Vision HUD v11** হলো একটি অ্যাডভান্সড রিয়েল-টাইম মোশন ট্র্যাকিং ও অবজেক্ট ডিটেকশন সিস্টেম, যা বিশেষ করে **Redmi 13C** সহ অ্যান্ড্রয়েড টার্মাক্স (Termux) এবং OpenCV এনভায়রনমেন্টে সহজে রান করার জন্য অপ্টিমাইজ করা হয়েছে। এটি ফোনের ক্যামেরা ব্যবহার করে স্বয়ংক্রিয়ভাবে অবজেক্ট শনাক্ত করে, সাইজ অনুযায়ী বাউন্ডিং বক্স অ্যাডজাস্ট করে এবং মোশন ট্র্যাক করে টার্গেট লক করে রাখে।

---

## ⚙️ এটি কী কী ইনপুট/ডেটা প্রসেস করতে পারে? (Supported Types)
* **লাইভ ক্যামেরা স্ট্রিম:** ফ্রন্ট ও ব্যাক ক্যামেরা (`user` / `environment`) থেকে আসা ভিডিও ফ্রেম।
* **ইমেজ ফরম্যাট:** Base64 এনকোডেড JPEG/PNG ইমেজ ডেটা।
* **অবজেক্ট ক্যাটাগরি (VOC Classes):** মানুষ (Human/Person), গাড়ি (Car), বাইক (Motorcycle), পোষা প্রাণী (Cat/Dog), বাস, ট্রেন এবং আরও বেশ কিছু অবজেক্ট।
* **আউটপুট ডেটা ফরম্যাট:** রিয়েল-টাইম JSON লগ এবং সেন্ট্রয়েড মোশন কোঅর্ডিনেট।

---

## 🛠️ টুলটির মূল কাজ কী? (Core Features & Functionality)
1. **Adaptive Box Sizing:** অবজেক্টের দূরত্ব ও সাইজ ছোট/বড় হলে বক্সটি স্বয়ংক্রিয়ভাবে নিজের আকার পরিবর্তন করে নেয়।
2. **Object Locking & Centroid Motion Tracking:** ক্যামেরা সরলে বা অবজেক্ট নড়াচড়া করলেও সেন্ট্রয়েড ট্র্যাকিংয়ের মাধ্যমে নির্দিষ্ট অবজেক্টে বক্সটি লক (`ID:#1`) হয়ে থাকে।
3. **Range Distance Calculation:** অবজেক্টের সাইজ ফিল্টারিং করে `SHORT-RANGE`, `MID-RANGE`, এবং `LONG-RANGE` ক্যালকুলেট করা।
4. **Hardware Control:** ওয়েব ইন্টারফেস থেকে সরাসরি ব্যাক ক্যামেরার ফ্ল্যাশলাইট (Torch) ও নাইট মোড ফিল্টার অন/অফ করার সুবিধা।
5. **Real-time JSON Logger:** প্রতি ফ্রেমে অবজেক্ট লকিং ডেটা Vault-এ সেভ করা ও লাইভ স্ট্রিম দেখা।

---

## 🎛️ টুলটির মোডসমূহ (System Modes & CLI Options)
টার্মিনাল চালুর পর মেনু ইন্টারফেসে নিচের মোডগুলো পাওয়া যায়:

1. **Start Server & Launch HUD (`Option 1`):** 
   * ব্যাকগ্রাউন্ডে পাইথন সার্ভার চালুর মাধ্যমে ব্রাউজারে সাইবার HUD ট্র্যাকিং মোড চালু করে।
2. **Stop Background Server (`Option 2`):** 
   * ব্যাকগ্রাউন্ডে রান হতে থাকা সার্ভার ও ক্যামেরা ফিড বন্ধ করে।
3. **Live Real-Time JSON Stream (`Option 3`):** 
   * ক্যামেরা দ্বারা ট্র্যাকিং ডেটা রিয়েল-টাইমে টার্মিনালে JSON আকারে লাইভ স্ট্রিম দেখায়।
4. **Structured Box Log & Vault Viewer (`Option 4 & 5`):** 
   * পূর্বে সেভ হওয়া ট্র্যাকিং ও ফেস লগের হিস্ট্রি ব্রাউজ করে।
5. **Clear Vault (`Option 6`):** 
   * পূর্বের সমস্ত ট্র্যাকিং ডেটা মুছে ফেলে এনভায়রনমেন্ট ফাঁকা করে।

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
# Termux Packages
pkg update && pkg upgrade -y
pkg install python opencv-python clang -y

# Python Pip Libraries
pip install numpy
```
​Note: You will need the MobileNet-SSD model files (MobileNetSSD_deploy.prototxt and MobileNetSSD_deploy.caffemodel) in the same directory for the AI detection engine to run.
## 📦 Installation & Setup
1. Clone or copy the project script into your working directory.
2. Ensure the model files are present.
3. Run the script:
4. python your_script_name.py

## 🕹️ Menu Options
- [1] Start Server & Launch HUD: Launches the local HTTP server on port 8080 and automatically opens the browser interface.
- [2] Stop Background Server: Shuts down the active web server.
- [3] LIVE REAL-TIME JSON STREAM: Streams live detection JSON logs directly in your terminal.
- [4] View Structured Box Log: Displays recent logs nicely formatted inside terminal box frames.
- [5] View Raw JSON Vault: Dumps the entire contents of face_data.json.
- [6] Clear Vault: Deletes the local log database.
- [7] Exit: Safely stops the server and exits the program.
​
## 📱 Termux / Android Support
​If you are running this on an Android device via Termux, ensure you have granted storage permissions and have installed Python and OpenCV properly to leverage local camera streams and termux-open-url.
