import uuid

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.cloud import texttospeech
from google.genai import types as genai_types


async def narrator(text: str, tool_context: ToolContext) -> dict:
    """Converts text to speech and saves it to a file."""
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    MODEL = "gemini-2.5-flash-tts"
    VOICE = "Algenib"
    LANGUAGE_CODE = "en-us"

    voice = texttospeech.VoiceSelectionParams(
        name=VOICE, language_code=LANGUAGE_CODE, model_name=MODEL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    filename = f"speech_{uuid.uuid4().hex[:8]}.mp3"

    part = genai_types.Part(
        inline_data=genai_types.Blob(
            mime_type="audio/mpeg", data=response.audio_content
        )
    )

    version = await tool_context.save_artifact(filename, part)

    return {"status": "success", "filename": filename, "version": version}


narrator_agent = Agent(
    name="narrator_agent",
    model="gemini-2.5-flash",
    instruction="Read aloud in a dark, scary but fast-paced style.",
    tools=[narrator],
)
