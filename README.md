# Spoofer

Spoofer is a dual-component application featuring a Python client script for capturing screenshots and a FastAPI backend for storing and viewing them. The client script includes dynamic capture controls, and the backend provides a simple web interface to view all captured images or download the latest one.

## Features

### Client Script
*   **Screenshot on Scroll:** Automatically captures the screen when scrolling.
*   **Color Control:** Press `b` on the keyboard to toggle black and white (grayscale) mode for captures.
*   **Exit:** Press `q` to exit the capture script.
*   **Dynamic Uploading:** Concatenates a base Server URL and a dynamic Upload Path to submit images to the backend.

### FastAPI Backend
*   **`/` (Root):** Displays a gallery of all captured images.
*   **`/latest-image`:** Shows the most recent screenshot and provides a download button.
*   **Dynamic Upload Endpoint:** The endpoint for receiving images is configured dynamically via environment variables.

## Prerequisites

*   Python 3.8+
*   pip (Python package installer)

## Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/RohitSingh-04/Spoofer](https://github.com/RohitSingh-04/Spoofer)
    cd Spoofer
    ```
2.  Install the required dependencies (you may want to use a virtual environment):
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Both the backend and the client rely on environment variables for configuration. You need to set up a `.env` file in the root directory (or wherever your backend expects it).

Create a `.env` file with the following variables:

```env
# URL of your FastAPI server (used by the client)
SERVER_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
# The dynamic path for the upload endpoint (used by both client and backend)
# Make sure it starts with a slash, e.g., /upload-secret-path
UPLOAD_PATH=/your-dynamic-upload-endpoint
```

## How to Run?

1. Start the Backend Server
```bash
uv run fastapi dev /src/spoofer/main.py
```

2. Run the Client Script
```bash
python scripts/uploader.py
```

### Note:
- we can use the client and the server in different machines, but make sure the required enivironment variables are configured for both.