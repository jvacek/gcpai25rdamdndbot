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

import random
from typing import Any

from google.adk.tools import ToolContext
from pydantic import BaseModel, Field

# Standard D&D dice faces
VALID_DICE = [4, 6, 8, 10, 12, 20, 100]


class DiceRoll(BaseModel):
    """Represents a dice roll result."""

    dice_type: int = Field(..., description="Number of faces on the die (e.g., 4, 6, 8, 10, 12, 20, 100)")
    result: int = Field(..., description="The rolled value")
    modifier: int = Field(default=0, description="Modifier added to the roll")
    total: int = Field(..., description="Total result including modifier")


class RollResult(BaseModel):
    """Represents the result of a complete roll request."""

    rolls: list[DiceRoll] = Field(..., description="Individual dice rolls")
    total: int = Field(..., description="Sum of all dice rolls plus modifiers")
    expression: str = Field(..., description="Readable expression of what was rolled")


def roll_single_die(dice_type: int, modifier: int = 0) -> DiceRoll:
    """
    Roll a single die of the specified type with an optional modifier.

    Args:
        dice_type: Number of faces on the die (4, 6, 8, 10, 12, 20, 100)
        modifier: Optional modifier to add to the roll

    Returns:
        DiceRoll object with the result

    Raises:
        ValueError: If dice_type is not a valid D&D die
    """
    if dice_type not in VALID_DICE:
        raise ValueError(
            f"Invalid dice type: {dice_type}. Valid types are: {', '.join(map(str, VALID_DICE))}"
        )

    result = random.randint(1, dice_type)
    total = result + modifier

    return DiceRoll(
        dice_type=dice_type,
        result=result,
        modifier=modifier,
        total=total,
    )


def roll_multiple_dice(
    num_dice: int,
    dice_type: int,
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False,
) -> RollResult:
    """
    Roll multiple dice of the same type with an optional modifier.

    Args:
        num_dice: Number of dice to roll
        dice_type: Number of faces on each die
        modifier: Modifier to add to the total
        advantage: If True, roll twice and take the higher result (D&D advantage)
        disadvantage: If True, roll twice and take the lower result (D&D disadvantage)

    Returns:
        RollResult with all individual rolls and the total

    Raises:
        ValueError: If dice_type is not valid, num_dice < 1, or both advantage and disadvantage are True
    """
    if dice_type not in VALID_DICE:
        raise ValueError(
            f"Invalid dice type: {dice_type}. Valid types are: {', '.join(map(str, VALID_DICE))}"
        )
    if num_dice < 1:
        raise ValueError("Number of dice must be at least 1")
    if advantage and disadvantage:
        raise ValueError("Cannot have both advantage and disadvantage")

    rolls: list[DiceRoll] = []

    # Roll the dice
    for _ in range(num_dice):
        roll = roll_single_die(dice_type, 0)
        rolls.append(roll)

    # Calculate total
    base_total = sum(roll.result for roll in rolls)

    # Apply advantage or disadvantage if specified
    if advantage or disadvantage:
        # Roll a second set
        for i in range(num_dice):
            reroll = roll_single_die(dice_type, 0)
            if advantage:
                # Take the higher of the two results
                rolls[i] = rolls[i] if rolls[i].result >= reroll.result else reroll
            else:
                # Take the lower of the two results
                rolls[i] = rolls[i] if rolls[i].result <= reroll.result else reroll

        base_total = sum(roll.result for roll in rolls)

    final_total = base_total + modifier

    # Build expression string
    advantage_str = " (advantage)" if advantage else ""
    disadvantage_str = " (disadvantage)" if disadvantage else ""
    modifier_str = f" + {modifier}" if modifier else ""
    expression = f"{num_dice}d{dice_type}{advantage_str}{disadvantage_str}{modifier_str}"

    return RollResult(
        rolls=rolls,
        total=final_total,
        expression=expression,
    )


def roll_dice_expression(expression: str) -> RollResult:
    """
    Roll dice from a D&D-style expression.

    Supports expressions like:
    - "1d20" - roll one d20
    - "2d6" - roll two d6
    - "1d20+5" - roll one d20 with +5 modifier
    - "2d8+3" - roll two d8 with +3 modifier
    - "1d20-2" - roll one d20 with -2 modifier
    - "1d20 adv" - roll with advantage
    - "1d20 dis" - roll with disadvantage

    Args:
        expression: Dice expression in D&D notation (e.g., "2d6+3", "1d20")

    Returns:
        RollResult with the rolls and total

    Raises:
        ValueError: If the expression cannot be parsed
    """
    expression = expression.strip().lower()

    # Check for advantage/disadvantage
    has_advantage = " adv" in expression or " advantage" in expression
    has_disadvantage = " dis" in expression or " disadvantage" in expression
    if has_advantage:
        expression = expression.replace(" adv", "").replace(" advantage", "")
    if has_disadvantage:
        expression = expression.replace(" dis", "").replace(" disadvantage", "")

    # Parse the basic dice expression
    if "d" not in expression:
        raise ValueError(f"Cannot parse dice expression: {expression}")

    # Split into dice part and modifier part
    if "+" in expression:
        dice_part, modifier_str = expression.split("+", 1)
        modifier = int(modifier_str.strip())
    elif "-" in expression:
        dice_part, modifier_str = expression.split("-", 1)
        modifier = -int(modifier_str.strip())
    else:
        dice_part = expression
        modifier = 0

    # Parse dice part
    if "d" not in dice_part:
        raise ValueError(f"Cannot parse dice expression: {expression}")

    num_dice_str, dice_type_str = dice_part.split("d", 1)
    num_dice = int(num_dice_str) if num_dice_str else 1
    dice_type = int(dice_type_str)

    return roll_multiple_dice(num_dice, dice_type, modifier, has_advantage, has_disadvantage)


# Function for the ADK tool
def roll_dice(expression: str, tool_context: ToolContext) -> dict[str, Any]:
    """
    Roll dice for D&D gameplay. This tool is for rolling dice for monsters, NPCs, and environmental effects.

    Args:
        expression: Dice expression in D&D notation. Examples:
            - "1d20" - roll one d20
            - "2d6+3" - roll two d6 and add 3
            - "1d20+5" - roll one d20 with +5 modifier
            - "1d20 adv" - roll with advantage (roll twice, take higher)
            - "1d20 dis" - roll with disadvantage (roll twice, take lower)
            - "3d8+7" - roll three d8 and add 7

    Returns:
        Dictionary containing:
            - total: The final total
            - expression: What was rolled
            - rolls: Individual dice results
            - details: Detailed breakdown of each die
    """
    try:
        result = roll_dice_expression(expression)
        return {
            "total": result.total,
            "expression": result.expression,
            "rolls": [roll.result for roll in result.rolls],
            "details": [
                {
                    "dice_type": roll.dice_type,
                    "result": roll.result,
                    "modifier": roll.modifier,
                }
                for roll in result.rolls
            ],
        }
    except Exception as e:
        return {"error": str(e)}

