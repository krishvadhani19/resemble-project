from typing import Any, Dict
import httpx
import base64
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import uuid

# Initialize the FastMCP server with a name for the service
mcp = FastMCP("resemble-server")

# Load environment variables from a .env file (if it exists)
load_dotenv()

# Constants for Resemble AI API endpoints
RESEMBLE_SYNTHESIZE_URL = "https://f.cluster.resemble.ai/synthesize"  # URL for text-to-speech synthesis
RESEMBLE_VOICES_URL = "https://app.resemble.ai/api/v2/voices"  # URL to fetch available voice models

# Retrieve the Resemble AI API key from environment variables
# If not found, default to "Not found" (though this will likely cause errors)
RESEMBLE_API_KEY = os.getenv("RESEMBLE_API_KEY", "Not found")

async def make_resemble_request(text: str, voice_uuid: str = "55592656", output_format: str = "mp3") -> Dict[str, Any] | None:
    """
    Make a request to the Resemble AI API to generate text-to-speech (TTS) audio.

    Args:
        text: The text to convert into speech.
        voice_uuid: The UUID of the voice model to use (default: "55592656").
        output_format: The format of the output audio file (default: "mp3").

    Returns:
        A dictionary containing the API response (including the generated audio) or None if an error occurs.
    """
    # Set up headers for the API request, including authorization and content type
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",  # Enable compression for faster responses
    }

    # Define the payload for the API request
    data = {
        "voice_uuid": voice_uuid,  # Specify the voice model to use
        "data": text,  # The text to synthesize
        "sample_rate": 48000,  # Set the sample rate for the audio
        "output_format": output_format,  # Specify the output format (e.g., mp3)
    }

    # Use an asynchronous HTTP client to make the request
    async with httpx.AsyncClient() as client:
        try:
            # Send a POST request to the Resemble AI synthesis endpoint
            response = await client.post(RESEMBLE_SYNTHESIZE_URL, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 4xx or 5xx)
            return response.json()  # Return the JSON response from the API
        except Exception as e:
            # Handle any errors that occur during the request
            print(f"Error making Resemble AI request: {e}")
            return None

@mcp.tool()
async def generate_tts(text: str, voice_uuid: str = str(uuid.uuid4())[:8], output_format: str = "mp3") -> str:
    """
    Generate text-to-speech (TTS) audio from text using Resemble AI.

    Args:
        text: The text to convert to speech.
        voice_uuid: The UUID of the voice model to use (default: a random 8-character string).
        output_format: The format of the output audio (default: "mp3").

    Returns:
        A link to the generated audio file or an error message if the request fails.
    """
    # Make the request to Resemble AI to generate TTS audio
    response = await make_resemble_request(text, voice_uuid, output_format)

    # Check if the response is valid and contains the expected "audio_content" field
    if not response or "audio_content" not in response:
        return "Unable to generate TTS audio."

    # Decode the base64-encoded audio content from the response
    audio_bytes = base64.b64decode(response["audio_content"])

    # Save the decoded audio to a file
    output_file = f"output.{output_format}"  # Define the output file name
    with open(output_file, "wb") as audio_file:
        audio_file.write(audio_bytes)  # Write the audio bytes to the file

    # Return a success message with the path to the generated audio file
    return f"TTS audio generated and saved as {output_file}"

@mcp.tool()
async def list_voices(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Retrieve a list of available voice models from Resemble AI.

    Args:
        page: The page number to retrieve (default: 1).
        page_size: The number of voices per page (default: 10).

    Returns:
        A dictionary containing the list of voices and pagination information.
    """
    # Set up headers for the API request, including authorization
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json",
    }

    # Define query parameters for pagination
    params = {
        "page": page,  # Specify the page number
        "page_size": page_size  # Specify the number of voices per page
    }

    # Use an asynchronous HTTP client to make the request
    async with httpx.AsyncClient() as client:
        try:
            # Send a GET request to the Resemble AI voices endpoint
            response = await client.get(
                RESEMBLE_VOICES_URL, 
                headers=headers, 
                params=params, 
                timeout=30.0
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Return the JSON response from the API
        except Exception as e:
            # Handle any errors that occur during the request
            error_message = f"Error retrieving voices: {str(e)}"
            print(error_message)
            return {"error": error_message}

if __name__ == "__main__":
    # Check if the Resemble AI API key is set
    if not RESEMBLE_API_KEY:
        print("Warning: RESEMBLE_API_KEY environment variable is not set.")
        print("Set it using: export RESEMBLE_API_KEY='your-api-key'")
    
    # Initialize and run the FastMCP server
    mcp.run(transport='stdio')