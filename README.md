# Resemble AI Text-to-Speech (TTS) Integration

This documentation explains how to use the Resemble AI Text-to-Speech (TTS) integration implemented in Python. The integration allows you to generate TTS audio from text and retrieve a list of available voice models using Resemble AI's API.

---

## **Overview**

The integration provides two main functionalities:

1. **Generate TTS Audio**: Converts text into speech using a specified voice model and saves the output as an audio file.
2. **List Available Voices**: Retrieves a paginated list of available voice models from Resemble AI.

The integration is built using:

- `httpx` for making HTTP requests.
- `FastMCP` for server functionality.
- `dotenv` for managing environment variables.

---

## **Prerequisites**

Before using the integration, ensure the following:

1. **Resemble AI API Key**:
    - Obtain an API key from Resemble AI.
    - Set it as an environment variable named `RESEMBLE_API_KEY`:
        
        ```bash
        export RESEMBLE_API_KEY='your-api-key'
        
        ```
        
2. **Python Libraries**:
    - Ensure you have a virtual environment (venv) set up.
    - Use `uv` to sync the required libraries:
    
    ```bash
    uv sync
    ```
    

---

## **Code Explanation**

### **1. Environment Setup**

The integration uses the `dotenv` library to load environment variables from a `.env` file. The `RESEMBLE_API_KEY` is required to authenticate requests to the Resemble AI API.

```python
from dotenv import load_dotenv
import os

load_dotenv()
RESEMBLE_API_KEY = os.getenv("RESEMBLE_API_KEY", "Not found")

```

---

### **2. Constants**

The following constants are defined for the Resemble AI API endpoints:

```python
RESEMBLE_SYNTHESIZE_URL = "<https://f.cluster.resemble.ai/synthesize>"
RESEMBLE_VOICES_URL = "<https://app.resemble.ai/api/v2/voices>"

```

---

### **3. `make_resemble_request` Function**

This function makes an HTTP POST request to the Resemble AI API to generate TTS audio from text.

```python
async def make_resemble_request(text: str, voice_uuid: str = "55592656", output_format: str = "mp3") -> Dict[str, Any] | None:
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }
    data = {
        "voice_uuid": voice_uuid,
        "data": text,
        "sample_rate": 48000,
        "output_format": output_format,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(RESEMBLE_SYNTHESIZE_URL, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making Resemble AI request: {e}")
            return None

```

---

### **4. `generate_tts` Function**

This function is a tool exposed by the `FastMCP` server. It generates TTS audio from text and saves it as an audio file.

```python
@mcp.tool()
async def generate_tts(text: str, voice_uuid: str = str(uuid.uuid4())[:8], output_format: str = "mp3") -> str:
    response = await make_resemble_request(text, voice_uuid, output_format)

    if not response or "audio_content" not in response:
        return "Unable to generate TTS audio."

    audio_bytes = base64.b64decode(response["audio_content"])
    output_file = f"output.{output_format}"
    with open(output_file, "wb") as audio_file:
        audio_file.write(audio_bytes)

    return f"TTS audio generated and saved as {output_file}"

```

---

### **5. `list_voices` Function**

This function retrieves a paginated list of available voice models from Resemble AI.

```python
@mcp.tool()
async def list_voices(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "page": page,
        "page_size": page_size
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(RESEMBLE_VOICES_URL, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_message = f"Error retrieving voices: {str(e)}"
            print(error_message)
            return {"error": error_message}

```

---

### **6. Server Initialization**

The `FastMCP` server is initialized and run when the script is executed.

```python
if __name__ == "__main__":
    if not RESEMBLE_API_KEY:
        print("Warning: RESEMBLE_API_KEY environment variable is not set.")
        print("Set it using: export RESEMBLE_API_KEY='your-api-key'")

    print("Starting Resemble AI MCP Server...")
    mcp.run(transport='stdio')

```

---

## **Usage**

### **Generating TTS Audio**

To generate TTS audio, call the `generate_tts` function with the desired text, voice UUID, and output format.

```python
await generate_tts("Hello, world!", voice_uuid="55592656", output_format="mp3")

```

---

### **Listing Available Voices**

To retrieve a list of available voices, call the `list_voices` function with the desired pagination parameters.

```python
await list_voices(page=1, page_size=10)

```

---

## **Error Handling**

- If the `RESEMBLE_API_KEY` is not set, a warning is displayed.
- Errors during API requests are caught and logged, and an appropriate error message is returned.

---

## **Output**

### **TTS Audio Generation**

The generated audio file is saved locally, and the file path is returned.

```
TTS audio generated and saved as output.mp3

```

---

### **List of Voices**

A JSON object containing the list of voices and pagination details is returned.

```json
{
  "data": [
    {
      "uuid": "55592656",
      "name": "John Doe",
      "language": "en-US"
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 10,
    "total": 100
  }
}

```

---

## **Conclusion**

This integration provides a simple and efficient way to generate TTS audio and retrieve voice models using Resemble AI's API. It is designed to be extensible and easy to use within a `FastMCP` server environment.
