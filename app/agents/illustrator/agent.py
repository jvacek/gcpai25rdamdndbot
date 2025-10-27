# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import uuid

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types as genai_types
from vertexai.preview.vision_models import ImageGenerationModel


def _create_imagen_prompt(narrative: str) -> str:
    """Convert a D&D narrative into an optimized Imagen prompt.

    Args:
        narrative: The storyteller's narrative text

    Returns:
        An optimized prompt for fantasy illustration generation
    """
    # Extract key elements and create a focused prompt
    # Keep the narrative but add style guidance
    base_prompt = f"{narrative[:500]}"  # Limit length for better results

    # Add style modifiers for consistent D&D fantasy art
    style_suffix = (
        " | Fantasy art style, Dungeons and Dragons, detailed illustration, "
        "dramatic lighting, epic fantasy scene, high quality digital art, "
        "painterly style, rich colors"
    )

    return base_prompt + style_suffix


async def generate_illustration_tool(narrative: str, tool_context: ToolContext) -> dict:
    """Generate a D&D illustration from the storyteller's narrative.

    Args:
        narrative: The storyteller's narrative text describing the scene

    Returns:
        A dictionary containing the saved artifact filename and status
    """
    try:
        # Initialize Imagen model
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

        # Create an optimized prompt for D&D fantasy art
        prompt = _create_imagen_prompt(narrative)

        logging.info(f"Generating illustration with prompt: {prompt[:100]}...")

        # Generate the image
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )

        if not response or not response.images:
            raise ValueError("No images were generated")

        # Get the image bytes from the first generated image
        image_bytes = response.images[0]._image_bytes

        # Create a unique filename for the illustration
        filename = f"illustration_{uuid.uuid4().hex[:8]}.png"

        # Create a Part with Blob to save as artifact
        part = genai_types.Part(
            inline_data=genai_types.Blob(mime_type="image/png", data=image_bytes)
        )

        # Save the image as an artifact using ADK's artifact service (async)
        version = await tool_context.save_artifact(filename, part)

        logging.info(f"Saved illustration as artifact: {filename} (version: {version})")

        return {
            "status": "success",
            "filename": filename,
            "version": version,
            "message": f"Generated D&D illustration saved as {filename}",
            "prompt_used": prompt[:200],  # Include truncated prompt for reference
        }

    except Exception as e:
        logging.error(f"Failed to generate illustration: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate illustration. Please try again.",
        }


illustrator_agent = Agent(
    name="illustrator_agent",
    model="gemini-2.5-flash",
    instruction="""You are a specialized illustration agent for Dungeons & Dragons campaigns.

Your sole purpose is to generate visual illustrations that match the storyteller's narrative and
save them as artifacts that will be automatically displayed to the user.

## Your Responsibilities

1. **Receive Narrative**: You will be given the storyteller's narrative description of a scene
2. **Generate Illustration**: Use the generate_illustration_tool to create a matching illustration
3. **Save as Artifact**: The tool automatically saves the image as an artifact in the session
4. **Confirm to User**: Let the user know an illustration has been generated for the scene

## Guidelines

- Extract the most visual and important elements from the narrative
- Focus on key scenes: character encounters, dramatic moments, locations, combat
- The illustration should capture the mood and atmosphere of the narrative
- Always use the generate_illustration_tool function to create images
- The tool saves the image as an artifact and returns a dict with 'status' and 'filename'
- The saved artifact will be automatically displayed to the user by the ADK UI
- If status is 'success', provide a brief confirmation message
- If status is 'error', provide a friendly error message to the user

## Example Usage

When you receive a narrative like:
"The party enters a dimly lit tavern filled with suspicious-looking patrons..."

You should:
1. Call generate_illustration_tool with that narrative
2. Check the returned status
3. If successful, provide a brief confirmation like "An illustration has been generated for this scene."
4. The image will automatically appear in the conversation for the user
""",
    tools=[generate_illustration_tool],
)
