# Real-Time Face Compression

This repository contains a Flask-based real-time face detection and image compression demo, showcasing JPEG and WebP compression quality metrics (PSNR & SSIM) in live video feeds.

---

## Features

* **Real-time Face Detection:** Uses OpenCV Haar cascades to detect and display faces.
* **Compression Formats:** Compare JPEG vs. WebP at user-controlled quality levels.
* **Quality Metrics:** Compute PSNR (Peak Signal-to-Noise Ratio) and SSIM (Structural Similarity Index) for objective and perceptual quality measurements.
* **Live Charts:** Dynamic rendering of PSNR, SSIM, file size (KB), and PSNR difference over time.
* **Interactive UI:** Slider for quality control, step-by-step algorithm preview, and responsive design.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/face-compression-demo.git
cd face-compression-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**

* Python 3.7+
* Flask
* OpenCV-Python
* scikit-image

---

## Usage

```bash
python real_time_face_compression_flask.py
```

Open your browser at `http://localhost:5000/` to view the landing page. Click **Proceed to Demo** to start the real-time demo.

---

## Architecture Overview

The application consists of a single Flask file (`real_time_face_compression_flask.py`) with the following components:

1. **Landing Page:** Introduces PSNR & SSIM and outlines pipeline steps.
2. **Demo Page:** Streams live video, detected faces, algorithm steps, and charts.
3. **Background Thread:** Continuously captures frames, computes compression/decompression, metrics, and buffers results.
4. **Flask Routes:** Serve landing page, demo page, video/face feeds, metrics JSON, and step images.

```mermaid
classDiagram
    class FlaskApp {
        +cap: VideoCapture
        +cascade: CascadeClassifier
        +quality: int
        +start_time: float
        +jpeg_psnr_vals: list
        +webp_ssim_vals: list
        +times: list
        +last_face: ndarray
        +lock: threading.Lock
        +compute_psnr(a,b)
        +process_step(frame,step)
        +bg()
    }
    class Routes {
        +index()
        +demo()
        +video_feed()
        +face_feed()
        +set_quality()
        +metrics()
        +step_image()
    }
    FlaskApp --> Routes
```

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant S as Flask Server
    participant C as Background Thread

    U->>B: Request landing page (/)
    B->>S: GET /
    S-->>B: render landing HTML
    U->>B: Click Proceed
    B->>S: GET /demo
    S-->>B: render demo HTML
    B->>S: GET /video_feed (multipart)
    S-->>B: JPEG frames stream
    C->>C: compute PSNR, SSIM, sizes
    B->>S: GET /metrics
    S-->>B: JSON metrics
    B->>S: GET /step_image?step=X
    S-->>B: single JPEG frame
```

---

## File Structure

```
face-compression-demo/
├── real_time_face_compression_flask.py  # Main application
├── requirements.txt                    # Dependencies
└── README.md                           # This documentation
```

---

## UML Diagrams

### Development Flow

```mermaid
graph TD
    A[Clone Repository] --> B[Create Virtual Env]
    B --> C[Install Dependencies]
    C --> D[Implement Features]
    D --> E[Write/Update Tests]
    E --> F[Run Application]
    F --> G[Debug & Refine]
    G --> H[Commit & Push]
```

### System Flow

````mermaid
flowchart LR
    subgraph Client [Browser]
        U[User] -->|Click Proceed| DemoPage[Demo Page]
        DemoPage -->|Stream| VideoFeed
        DemoPage -->|Stream| FaceFeed
        DemoPage -->|Poll every 1s| Metrics[Metrics Endpoint]
        DemoPage -->|Request| StepImage[Step Image Endpoint]
    end

    subgraph Server [Flask App]
        VideoFeed -->|Generate JPEG| Camera[Webcam]
        FaceFeed -->|Crop Face ROI| Camera
        Metrics -->|Return JSON| Logger[bg Thread]
        StepImage -->|Process Frame| Processor[process_step()]
    end

    Camera --> Logger
    Processor -->|Returns| StepImage
    Logger --> Metrics
```mermaid
flowchart LR
    subgraph Client [Browser]
        U[User] -->|Click "Proceed"| DemoPage[Demo Page]
        DemoPage -->|Stream| VideoFeed
        DemoPage -->|Stream| FaceFeed
        DemoPage -->|Poll every 1s| Metrics[Metrics Endpoint]
        DemoPage -->|Request| StepImage[Step Image Endpoint]
    end

    subgraph Server [Flask App]
        VideoFeed -->|Generate JPEG| Camera[Webcam]
        FaceFeed -->|Crop Face ROI| Camera
        Metrics -->|Return JSON| Logger[bg Thread]
        StepImage -->|Process Frame| Processor[process_step()]
    end

    Camera --> Logger
    Processor -->|Returns| StepImage
    Logger --> Metrics
````

---

## License

MIT License. See [LICENSE](LICENSE) for details.
