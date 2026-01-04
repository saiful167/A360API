from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import importlib
import socket
import time
from datetime import datetime
# নিশ্চিত করুন আপনার প্রোজেক্টে utils.py ফাইল এবং তাতে LOGGER অবজেক্ট আছে
try:
    from utils import LOGGER
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    LOGGER = logging.getLogger(__name__)

app = FastAPI(
    title="A360",
    description="A Project Made To Centralize Various APIs 📖 No Authorization Needed, All Endpoints Included :"
)

start_time = time.time()

# HTML ফাইল লোড করার ফাংশনগুলো
def load_html_file(file_path, title, fallback_msg):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        return f"<h1>{title}</h1><p>{fallback_msg}</p>"
    except Exception as e:
        LOGGER.error(f"Error loading {file_path}: {e}")
        return f"<h1>Error</h1><p>Could not load page.</p>"

def get_actual_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def get_server_address():
    ip = get_actual_ip()
    port = int(os.getenv("PORT", 4434))
    return f"http://{ip}:{port}"

def get_uptime():
    uptime_seconds = time.time() - start_time
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def count_plugins():
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        return 0
    return len([f for f in os.listdir(plugins_dir) if f.endswith(".py") and f != "__init__.py"])

def count_endpoints():
    return len([route for route in app.routes if route.path not in ["/", "/report", "/health", "/api/health"]])

@app.get("/", response_class=HTMLResponse)
async def root():
    return load_html_file("templates/index.html", "Welcome to AbirAPI", "Index page not found.")

@app.get("/report", response_class=HTMLResponse)
async def report():
    return load_html_file("templates/report.html", "API Report", "Report page not found.")

@app.get("/health", response_class=HTMLResponse)
async def health():
    return load_html_file("templates/health.html", "API Health", "Health page not found.")

@app.get("/api/health")
async def health_api():
    # এখানে ডিকশনারি ফরম্যাট ঠিক করা হয়েছে
    return {
        "Api Owner": "@saifulmn",
        "Owner Name": "Saiful Islam",
        "Api Updates": "@saifulmn",
        "Api About": "An Asynchronous Multifunctional API Built With Pyrofork Telethon & FastAPI Framework & Python Lang By @ISmartCoder",
        "Api Version": "1.16.1",
        "Api Health": "Operational",
        "Api Uptime": get_uptime(),
        "Total Endpoints": count_endpoints(),
        "Total Plugins": count_plugins(),
        "Last Checked": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def load_plugins():
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        return

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                # ডাইনামিক ইমপোর্ট
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "router"):
                    app.include_router(module.router)
                    LOGGER.info(f"Successfully loaded plugin: {module_name}")
                else:
                    LOGGER.warning(f"Plugin {module_name} does not have a router")
            except Exception as e:
                LOGGER.error(f"Failed to load plugin {module_name}: {str(e)}")

# প্লাগিন লোড করা হচ্ছে
load_plugins()

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 4434))
    LOGGER.info(f"API Running At {get_server_address()}")
    uvicorn.run(
        "main:app", # নিশ্চিত করুন আপনার ফাইলটির নাম main.py
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true"
                )


