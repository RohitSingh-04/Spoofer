from dotenv import load_dotenv
import os
from urllib.parse import urljoin

load_dotenv()


import time
import threading
import io
import requests
from pynput import mouse, keyboard
from PIL import ImageGrab

# Configuration
UPLOAD_URL = urljoin(os.getenv("SERVER_URL", "http://127.0.0.1:8000/"), os.getenv("UPLOAD_PATH", "/upload"))

COOLDOWN_SECONDS = 2.0  # Minimum time between uploads to prevent server spam
JPEG_QUALITY = 60       # Compression level (1-100, lower is smaller file size)

last_upload_time = 0

def capture_and_upload(is_bw=False):
    """Captures the screen, optionally converts to B/W, compresses, and uploads."""
    try:
        # 1. Take the screenshot
        screenshot = ImageGrab.grab()
        
        # 2. Convert color mode
        if is_bw:
            # Convert to 8-bit pixels, black and white (grayscale)
            screenshot = screenshot.convert("L")
        elif screenshot.mode in ("RGBA", "P"):
            # Convert to standard RGB for JPEG compatibility
            screenshot = screenshot.convert("RGB")
            
        # 3. Compress the image in-memory
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='JPEG', quality=JPEG_QUALITY)
        img_buffer.seek(0)
        
        # 4. Upload to the URL
        files = {'file': ('screenshot.jpg', img_buffer, 'image/jpeg')}
        response = requests.post(UPLOAD_URL, files=files, timeout=10)
        
        if response.status_code in (200, 201):
            mode_str = "B/W" if is_bw else "Color"
            print(f"Successfully uploaded {mode_str}! (Size: {img_buffer.getbuffer().nbytes / 1024:.1f} KB)")
        else:
            print(f"Upload failed. Server returned: {response.status_code}")
            
    except Exception as e:
        print(f"Error during capture/upload: {e}")

def on_scroll(x, y, dx, dy):
    """Triggered on mouse scroll."""
    global last_upload_time
    current_time = time.time()
    
    if current_time - last_upload_time > COOLDOWN_SECONDS:
        last_upload_time = current_time
        print("Scroll detected. Capturing color screenshot...")
        threading.Thread(target=capture_and_upload, args=(False,), daemon=True).start()

def on_press(key):
    """Triggered on keyboard key press."""
    global last_upload_time
    try:
        # Check if the pressed key is 'b'
        if hasattr(key, 'char') and key.char == 'b':
            current_time = time.time()
            if current_time - last_upload_time > COOLDOWN_SECONDS:
                last_upload_time = current_time
                print("'b' key pressed. Capturing B/W screenshot...")
                threading.Thread(target=capture_and_upload, args=(True,), daemon=True).start()

        #for testing
        if hasattr(key, 'char') and key.char == 'q':
            print("exit...")
            exit()
    except Exception:
        pass

# Start both listeners concurrently
if __name__ == "__main__":
    print(f"Listening for mouse scrolls (Color) and 'b' key presses (B/W)...")
    print(f"Throttled to 1 screenshot per {COOLDOWN_SECONDS}s. Press Ctrl+C to stop. or press 'q'")
    
    mouse_listener = mouse.Listener(on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_press)
    
    mouse_listener.start()
    keyboard_listener.start()
    
    try:
        # Keep the main thread alive while listeners run in the background
        mouse_listener.join()
        keyboard_listener.join()
    except KeyboardInterrupt:
        print("\nStopping script.")