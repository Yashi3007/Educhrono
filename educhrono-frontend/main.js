import { app, BrowserWindow } from "electron";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let backendProcess;

function startBackend() {
  backendProcess = spawn("python", ["-m", "uvicorn", "app.main:app"], {
    cwd: path.join(__dirname, "../educhrono-backend"), // ✅ backend folder path
    windowsHide: true, 
  });

  backendProcess.stdout.on("data", (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on("data", (data) => {
    console.error(`Backend Error: ${data}`);
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
  });

  win.loadFile(path.join(__dirname, "dist/index.html"));
}

app.whenReady().then(() => {
  startBackend();   // ✅ backend auto start
  createWindow();   // ✅ app open
});