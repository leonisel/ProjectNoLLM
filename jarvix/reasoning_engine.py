"""
Jarvix NoLLM
Reasoning Engine V2

Evaluates thoughts and chooses the best course of action.

The reasoning engine does not generate responses.
It decides WHAT Jarvix should do.
"""

from dataclasses import dataclass
from typing import List

from .thought import Thought


@dataclass
class ReasoningResult:

    action: str = "RESPOND"

    confidence: float = 0.0

    explanation: str = ""

    selected_thought: Thought | None = None

    plan: list = None

class ReasoningEngine:

    def __init__(self):
        self.last_result = None
        self.reasoning_history = []

    ############################################################
    # Main reasoning function
    ############################################################

    def reason(self, thoughts: List[Thought]) -> ReasoningResult:

        result = ReasoningResult()

        if not thoughts:

            result.explanation = "No thoughts available."

            self.last_result = result

            return result

        ########################################################
        # Step 1
        # Sort thoughts by priority
        ########################################################

        ordered = sorted(

            thoughts,

            key=lambda t: (t.priority, t.confidence),

            reverse=True

        )

        ########################################################
        # Step 2
        # Choose best thought
        ########################################################

        best = ordered[0]

        result.selected_thought = best

        result.action = best.goal
        result.plan = self.create_plan(best)
        result.confidence = best.confidence
        result.explanation = best.text

        self.last_result = result

        return result

    ############################################################
    # Plan generation
    ############################################################

    def create_plan(self, thought):

        if thought.goal == "LOOKUP":

            return [
                "search_memory",
                "evaluate_facts",
                "generate_answer"
            ]


        if thought.goal == "STORE_FACT":

            return [
                "validate_fact",
                "check_conflicts",
                "store_memory"
            ]


        if thought.goal == "GREET":

            return [
                "create_social_response"
            ]


        if thought.goal == "EMPATHIZE":

            return [
                "recognize_emotion",
                "create_supportive_response"
            ]


        return [
            "understand",
            "respond"
        ]


    ############################################################
    # Utility
    ############################################################

    def explain(self):

        if self.last_result is None:

            return "No reasoning performed."

        return (

            f"Action: {self.last_result.action}\n"

            f"Reason: {self.last_result.explanation}\n"

            f"Confidence: {self.last_result.confidence:.2f}"

        )