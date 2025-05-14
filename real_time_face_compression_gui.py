from flask import Flask, Response, render_template_string, request, jsonify, redirect, url_for
import cv2
import numpy as np
import threading
import time
from skimage.metrics import structural_similarity as compare_ssim

app = Flask(__name__)

# 1. Video Capture Setup
cap = cv2.VideoCapture(0)
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 2. Global State
quality = 50
jpeg_psnr_vals, webp_psnr_vals = [], []
jpeg_ssim_vals, webp_ssim_vals = [], []
jpeg_size_vals, webp_size_vals = [], []
times = []
start_time = time.time()
last_face = None
lock = threading.Lock()

# 3. Landing Page Template with Enhanced Styling
LANDING_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About PSNR & SSIM</title>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Roboto', sans-serif;
      background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }
    .container {
      background: #ffffff;
      padding: 40px;
      max-width: 800px;
      width: 90%;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      text-align: left;
    }
    h1 {
      font-size: 2.5rem;
      margin-bottom: 10px;
      color: #102a43;
    }
    h2 {
      font-size: 1.5rem;
      margin-top: 30px;
      color: #243b53;
    }
    p {
      font-size: 1rem;
      line-height: 1.6;
      color: #334e68;
      margin-bottom: 20px;
    }
    ul {
      list-style: disc inside;
      margin-left: 20px;
    }
    li {
      margin-bottom: 10px;
    }
    .btn {
      display: inline-block;
      margin-top: 30px;
      padding: 15px 30px;
      font-size: 1rem;
      font-weight: 700;
      color: #fff;
      background-color: #006c8c;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      text-decoration: none;
    }
    .btn:hover {
      background-color: #005066;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Understanding PSNR & SSIM</h1>
    <p><strong>PSNR</strong> (Peak Signal-to-Noise Ratio) quantifies the peak error between a compressed image and the original. Defined as:</p>
    <p style="text-align:center;"><code>PSNR = 20 * log10(MAX_I) - 10 * log10(MSE)</code></p>
    <p>where <em>MSE</em> is the mean squared error. A higher PSNR indicates less difference from the original image.</p>
    <p><strong>SSIM</strong> (Structural Similarity Index) models perceived image quality through luminance, contrast, and structural comparison. SSIM values range from -1 to 1, with 1 indicating identical images.</p>

    <h2>Algorithm Pipeline & Significance</h2>
    <ul>
      <li><strong>Frame Capture:</strong> Grab live frames from your webcam for real-time analysis.</li>
      <li><strong>Face Detection:</strong> Apply Haar cascades to pinpoint face regions, reducing extra processing.</li>
      <li><strong>Grayscale Conversion:</strong> Simplify to luminance data; key for accurate SSIM computation.</li>
      <li><strong>Compression:</strong> Encode to JPEG/WebP at adjustable quality to observe artifacts.</li>
      <li><strong>Decompression:</strong> Decode back the compressed images to compare with originals.</li>
      <li><strong>Metrics Computation:</strong> Calculate PSNR & SSIM for both formats to evaluate objective vs perceptual quality.</li>
      <li><strong>Visualization:</strong> Dynamic charts reveal how quality and file size evolve over time.</li>
    </ul>

    <a href="{{ url_for('demo') }}" class="btn">Proceed to Demo</a>
  </div>
</body>
</html>
"""

# 4. Demo Page Template
DEMO_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Real-Time Face & Compression Demo</title>
  <style>
    body{font-family:Arial, sans-serif; margin:0;padding:0;background:#fafafa;}
    header{background:#333;color:#fff;padding:10px;text-align:center;}
    #controls{margin:20px;text-align:center;}
    #main{display:flex;flex-wrap:wrap;justify-content:center;padding:10px;}
    .stream,.step,.charts{margin:10px;background:#fff;padding:10px;border-radius:6px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}
    img{border:1px solid #ccc;border-radius:4px;}
    .chart-container{width:400px;height:300px;margin:10px;display:inline-block;}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <header><h1>Real-Time Face & Compression Demo</h1></header>
  <div id="controls">
    Compression Quality: <span id="qval">{{ quality }}</span>%
    <input type="range" id="quality" min="10" max="100" value="{{ quality }}"/>
  </div>
  <div id="main">
    <div class="stream">
      <h3>Live Detection & Encoding</h3>
      <img id="video" src="{{ url_for('video_feed') }}" width="480"/>
    </div>
    <div class="stream">
      <h3>Detected Face ROI</h3>
      <img id="face" src="{{ url_for('face_feed') }}" width="200"/>
    </div>
    <div class="step">
      <h3>Algorithm Step Preview</h3>
      <select id="stepSelect">
        <option value="5.1">Capture Frame</option>
        <option value="5.2">Face Detection</option>
        <option value="5.2g">Grayscale</option>
        <option value="5.3">Compression</option>
        <option value="5.4">Metrics Overlay</option>
        <option value="5.6">Composite View</option>
      </select>
      <div id="stepDesc"></div>
      <img id="stepImg" src="{{ url_for('step_image', step='5.1') }}" width="480"/>
    </div>
    <div class="charts">
      <h3>PSNR & SSIM over Time</h3>
      <div class="chart-container"><canvas id="psnrChart"></canvas></div>
      <div class="chart-container"><canvas id="ssimChart"></canvas></div>
      <h3>Frame Sizes (KB)</h3>
      <div class="chart-container"><canvas id="sizeChart"></canvas></div>
      <h3>PSNR Difference (JPEG–WebP)</h3>
      <div class="chart-container"><canvas id="diffChart"></canvas></div>
    </div>
  </div>
  <script>
    const slider = document.getElementById('quality'), qval = document.getElementById('qval');
    slider.oninput = () => {
      qval.textContent = slider.value;
      fetch('{{ url_for('set_quality') }}', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({quality:slider.value}) });
    };
    const info = {'5.1':'Raw frame capture.','5.2':'Face detection overlay.','5.2g':'Grayscale output.','5.3':'JPEG compression.','5.4':'PSNR & SSIM overlay.','5.6':'Side-by-side composite.'};
    const sel=document.getElementById('stepSelect'), desc=document.getElementById('stepDesc'), img=document.getElementById('stepImg');
    function upd(){const s=sel.value;desc.innerText=info[s];img.src='{{ url_for('step_image') }}?step='+s+'&_='+Date.now();}
    sel.onchange=upd; upd();
    function makeChart(id,yLabel,labels){return new Chart(document.getElementById(id).getContext('2d'),{type:'line',data:{labels:[],datasets:labels.map(l=>({label:l,data:[],fill:false}))},options:{animation:false,scales:{x:{title:{display:true,text:'Time (s)'}},y:{title:{display:true,text:yLabel}}}}});}
    const psnrChart=makeChart('psnrChart','PSNR (dB)',['JPEG','WebP']), ssimChart=makeChart('ssimChart','SSIM',['JPEG','WebP']), sizeChart=makeChart('sizeChart','Size (KB)',['JPEG','WebP']), diffChart=new Chart(document.getElementById('diffChart').getContext('2d'),{type:'line',data:{labels:[],datasets:[{label:'ΔPSNR',data:[],fill:false}]},options:{animation:false,scales:{x:{title:{display:true,text:'Time (s)'}},y:{title:{display:true,text:'ΔPSNR (dB)'}}}}});
    setInterval(()=>{fetch('{{ url_for('metrics') }}').then(r=>r.json()).then(d=>{[['jpeg_psnr','webp_psnr',psnrChart],['jpeg_ssim','webp_ssim',ssimChart],['jpeg_size','webp_size',sizeChart]].forEach(([a,b,ch])=>{ch.data.labels=d.times;ch.data.datasets[0].data=d[a].map(v=>a.includes('size')?v/1024:v);ch.data.datasets[1].data=d[b].map(v=>b.includes('size')?v/1024:v);ch.update();});const diff=d.jpeg_psnr.map((v,i)=>v-d.webp_psnr[i]);diffChart.data.labels=d.times;diffChart.data.datasets[0].data=diff;diffChart.update();});},1000);
  </script>
</body>
</html>
"""

# 5. Helpers
def compute_psnr(a, b):
    mse = np.mean((a.astype(np.float64)-b.astype(np.float64))**2)
    return 100.0 if mse==0 or not np.isfinite(mse) else 20*np.log10(255.0/np.sqrt(mse))

def process_step(frame, step):
    img = frame.copy()
    if step=='5.2':
        small=cv2.resize(img,(img.shape[1]//4,img.shape[0]//4));gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        for x,y,w,h in cascade.detectMultiScale(gray,1.3,5):
            cv2.rectangle(img,(x*4,y*4),(x*4+w*4,y*4+h*4),(0,255,0),3)
    elif step=='5.2g':
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY);img=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
    elif step in('5.3','5.4','5.6'):
        _,buf=cv2.imencode('.jpg',img,[int(cv2.IMWRITE_JPEG_QUALITY),quality]);dec=cv2.imdecode(buf,cv2.IMREAD_COLOR)
        ps=compute_psnr(frame,dec);ss=compare_ssim(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.cvtColor(dec,cv2.COLOR_BGR2GRAY))
        if step=='5.3':img=dec
        elif step=='5.4':
            img=dec;cv2.putText(img,f'PSNR:{ps:.1f}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2);cv2.putText(img,f'SSIM:{ss:.2f}',(10,70),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        else:img=np.hstack((frame,dec))
    return img

# 6. Background Thread
def bg():
    global last_face
    while True:
        ret,frame=cap.read()
        if not ret:continue
        small=cv2.resize(frame,(frame.shape[1]//4,frame.shape[0]//4));gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        faces=cascade.detectMultiScale(gray,1.3,5)
        with lock:
            last_face=None
            for x,y,w,h in faces:
                last_face=frame[y*4:y*4+h*4,x*4:x*4+w*4].copy()
        _,bj=cv2.imencode('.jpg',frame,[int(cv2.IMWRITE_JPEG_QUALITY),quality])
        _,bw=cv2.imencode('.webp',frame,[int(cv2.IMWRITE_WEBP_QUALITY),quality])
        dj=cv2.imdecode(bj,cv2.IMREAD_COLOR);dw=cv2.imdecode(bw,cv2.IMREAD_COLOR)
        pj=compute_psnr(frame,dj);pw=compute_psnr(frame,dw)
        gj=compare_ssim(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.cvtColor(dj,cv2.COLOR_BGR2GRAY))
        gw=compare_ssim(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.cvtColor(dw,cv2.COLOR_BGR2GRAY))
        t=time.time()-start_time
        with lock:
            jpeg_psnr_vals.append(pj);webp_psnr_vals.append(pw)
            jpeg_ssim_vals.append(gj);webp_ssim_vals.append(gw)
            jpeg_size_vals.append(len(bj));webp_size_vals.append(len(bw))
            times.append(round(t,1))
        time.sleep(0.1)

# 7. Routes & Entry
@app.route('/')
def index(): return render_template_string(LANDING_TEMPLATE)
@app.route('/demo')
def demo(): return render_template_string(DEMO_TEMPLATE,quality=quality)
@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            ret,frame=cap.read()
            if not ret: continue
            small=cv2.resize(frame,(frame.shape[1]//4,frame.shape[0]//4));gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
            for x,y,w,h in cascade.detectMultiScale(gray,1.3,5):cv2.rectangle(frame,(x*4,y*4),(x*4+w*4,y*4+h*4),(0,255,0),3)
            _,buf=cv2.imencode('.jpg',frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+buf.tobytes()+b'\r\n')
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/face_feed')
def face_feed():
    def genf():
        while True:
            with lock: f=last_face
            if f is None: time.sleep(0.1); continue
            _,buf=cv2.imencode('.jpg',f)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+buf.tobytes()+b'\r\n')
    return Response(genf(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/set_quality',methods=['POST'])
def set_quality():
    global quality,start_time
    q=request.get_json().get('quality')
    if q: quality=int(q)
    with lock: jpeg_psnr_vals.clear();webp_psnr_vals.clear();jpeg_ssim_vals.clear();webp_ssim_vals.clear();jpeg_size_vals.clear();webp_size_vals.clear();times.clear()
    start_time=time.time()
    return jsonify(status='ok')
@app.route('/metrics')
def metrics():
    with lock: return jsonify(times=times,jpeg_psnr=jpeg_psnr_vals,webp_psnr=webp_psnr_vals,jpeg_ssim=jpeg_ssim_vals,webp_ssim=webp_ssim_vals,jpeg_size=jpeg_size_vals,webp_size=webp_size_vals)
@app.route('/step_image')
def step_image():
    step=request.args.get('step','5.1')
    ret,frame=cap.read()
    if not ret: return '',404
    buf=cv2.imencode('.jpg',process_step(frame,step))[1]
    return Response(buf.tobytes(),mimetype='image/jpeg')
if __name__=='__main__':
    threading.Thread(target=bg,daemon=True).start()
    app.run(host='0.0.0.0',port=5000,threaded=True)
