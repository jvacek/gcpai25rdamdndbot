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


async def generate_illustration_tool(narrative: str, tool_context: ToolContext) -> str:
    """Generate a D&D illustration from the storyteller's narrative.

    Args:
        narrative: The storyteller's narrative text describing the scene

    Returns:
        The filename of the saved illustration artifact
    """
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

    # Return just the filename - the artifact will display automatically
    return filename


illustrator_agent = Agent(
    name="illustrator_agent",
    model="gemini-2.5-flash",
    instruction="""You are a specialized illustration agent for Dungeons & Dragons campaigns.

Your sole purpose is to generate visual illustrations that match the storyteller's narrative.

## Critical Instructions

1. Call the generate_illustration_tool with the narrative you receive
2. DO NOT provide any text response, confirmation message, or explanation
3. The image artifact will be automatically displayed to the user
4. Your response should be EMPTY after the tool call - no additional text whatsoever

## What to Do

Simply call generate_illustration_tool with the narrative. That's it. Nothing else.
""",
    tools=[generate_illustration_tool],
)
