````markdown
# Real-Time Face Compression Demo

A Flask-based web application that captures live webcam frames, detects faces, compresses frames with JPEG/WebP at variable quality, computes PSNR/SSIM metrics, and visualizes everything in real time.

---

## Features

- **Live Face Detection** using OpenCV Haar cascades  
- **On-the-fly Compression** to JPEG and WebP  
- **Quality Metrics**: PSNR & SSIM calculation per frame  
- **Interactive Dashboard**: adjust compression quality, preview algorithm steps, view charts of PSNR/SSIM, frame sizes, and PSNR difference  
- **Single-file Flask App** for easy deployment  

---

## Prerequisites

- Python 3.7+  
- Webcam or video capture device  
- pip packages:  
  ```bash
  pip install flask opencv-python-headless numpy scikit-image chart.js
````

---

## Installation & Run

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/face-compression-demo.git
   cd face-compression-demo
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**

   ```bash
   python real_time_face_compression_flask.py
   ```

4. **Open in browser**
   Visit [http://localhost:5000](http://localhost:5000) to see the landing page, then click **Proceed to Demo**.

---

## Project Structure

```
real_time_face_compression_flask.py   # Single-file Flask application
requirements.txt                     # pip dependencies
README.md                             # This documentation
```

---

## Architecture Overview

1. **Landing Page** (`/`)

   * Introduces PSNR & SSIM
   * Describes each algorithm step’s purpose
   * “Proceed to Demo” button

2. **Demo Page** (`/demo`)

   * Live video (`/video_feed`) with face rectangles
   * Latest face ROI stream (`/face_feed`)
   * Algorithm step preview (`/step_image?step=…`)
   * Quality slider (`/set_quality`)
   * Metrics JSON (`/metrics`) for charts

3. **Background Thread**

   * Continuously grabs frames
   * Detects faces & stores latest ROI
   * Encodes to JPEG/WebP, computes PSNR/SSIM, sizes, timestamps

---

## UML Diagrams

### 1. Development Flow

```mermaid
flowchart TD
  CloneRepo --> InstallDeps[Install Dependencies]
  InstallDeps --> OpenEditor[Open Code in Editor]
  OpenEditor --> MakeChanges[Implement Features / Templates]
  MakeChanges --> RunLocally[Run `python real_time_face_compression_flask.py`]
  RunLocally --> TestFeature[Test & Debug]
  TestFeature --> Commit[Commit Changes]
  Commit --> Push[Push to GitHub]
  Push --> CI[CI/CD Pipeline (optional)]
```

### 2. System Flow

```mermaid
flowchart LR
    Browser --> LandingPage[/ GET / \]
    LandingPage --> DemoPage[/ GET /demo \]
    DemoPage -->|GET /video_feed| VideoRoute[/video_feed\]
    VideoRoute --> Capture[Capture Frame]
    Capture --> Detect[Face Detection]
    Detect --> Annotate[Draw Rectangle]
    Annotate --> Encode[Encode JPEG/WebP]
    Encode --> VideoRoute

    DemoPage -->|GET /face_feed| FaceRoute[/face_feed\]
    FaceRoute --> ROI[Return Latest Face ROI]
    ROI --> FaceRoute

    DemoPage -->|GET /metrics| MetricsRoute[/metrics\]
    MetricsRoute --> Compute[Compute PSNR & SSIM]
    Compute --> MetricsRoute

    DemoPage -->|GET /step_image| StepRoute[/step_image\]
    StepRoute --> Process[process_step()]
    Process --> StepRoute
```

---

## Further Reading

* **PSNR & SSIM** fundamentals:

  * Wang, Z., Bovik, A.C., Sheikh, H.R., Simoncelli, E.P. “Image Quality Assessment: From Error Visibility to Structural Similarity.” *IEEE Trans. on Image Processing*, 2004.
* **OpenCV Haar Cascades**:

  * [https://docs.opencv.org/4.x/db/d28/tutorial\_cascade\_classifier.html](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
