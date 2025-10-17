from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()
progress = {}  # Store progress by upload ID

@app.get("/")
async def main():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <body>
    <h2>File Upload with Progress (WebSocket)</h2>
    <input type="file" id="fileInput">
    <button onclick="upload()">Upload</button>
    <br><br>
    <progress id="progressBar" value="0" max="100"></progress>
    <script>
    async function upload() {
        const file = document.getElementById('fileInput').files[0];
        const ws = new WebSocket(`ws://${location.host}/ws/${file.name}`);
        ws.onmessage = (event) => {
            const percent = event.data;
            document.getElementById('progressBar').value = percent;
        };

        const formData = new FormData();
        formData.append('file', file);
        await fetch('/upload', { method: 'POST', body: formData });
        alert("Upload complete!");
        ws.close();
    }
    </script>
    </body>
    </html>
    """)

@app.websocket("/ws/{filename}")
async def websocket_endpoint(websocket: WebSocket, filename: str):
    await websocket.accept()
    progress[filename] = 0
    try:
        while True:
            if filename in progress:
                await websocket.send_text(str(progress[filename]))
            await asyncio.sleep(0.2)
    except Exception:
        progress.pop(filename, None)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    progress[filename] = 0

    with open(f"uploads/{filename}", "wb") as f:
        chunk_size = 1024 * 1024  # 1MB
        total_bytes = 0
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            total_bytes += len(chunk)
            # Simulate tracking (in reality you’d know total size)
            progress[filename] = min(100, total_bytes // 10000)  # fake % calc

    progress[filename] = 100
    await asyncio.sleep(1)
    progress.pop(filename, None)
    return {"status": "ok"}
