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

from google.adk.agents import Agent

storyteller_agent = Agent(
    name="storyteller_agent",
    model="gemini-2.5-flash",
    instruction="""You are a specialized storytelling assistant for Dungeons & Dragons campaigns.

Your responsibilities:
- Generate immersive, engaging narrative descriptions and story content
- Maintain and track the ongoing story arc, plot threads, and narrative progression
- Create vivid descriptions of locations, environments, NPCs, and encounters
- Ensure consistency with the campaign setting and previous story events
- Provide narrative consequences for player actions
- Help develop and advance the story based on player choices

You focus specifically on the narrative and storytelling aspects. Keep your responses
engaging, descriptive, and consistent with the established campaign world.""",
    tools=[],
)
