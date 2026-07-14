"""
Jarvix NoLLM
Thought Engine

Produces internal thoughts before a response.

The Thought Engine never talks directly to the user.
It creates ideas for the Executive Controller.
"""

from dataclasses import dataclass
from typing import List


from dataclasses import dataclass, field
from typing import List


@dataclass
class Thought:
    """
    A complete internal representation of one thought.

    Every subsystem should receive this object instead of raw strings.
    """

    # Original user text
    text: str

    # Basic properties
    priority: float = 0.5
    source: str = "general"
    confidence: float = 0.7
    goal: str = "RESPOND"

    # Parsed knowledge
    intent: str = ""
    entities: List[str] = field(default_factory=list)
    triples: List = field(default_factory=list)

    # Reasoning
    conclusions: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)

    # Memory
    consolidated: bool = False
    importance: float = 0.5

    # Extra information
    metadata: dict = field(default_factory=dict)


class ThoughtEngine:

    def __init__(self):

        self.active_thoughts: List[Thought] = []

    ####################################################################
    # Utility
    ####################################################################

    def clear(self):

        self.active_thoughts.clear()

    def add(
        self,
        text,
        priority=0.5,
        source="general",
        confidence=0.7,
        goal="RESPOND",
        metadata=None
    ):

        self.active_thoughts.append(

            Thought(
            text=text,
            priority=priority,
            source=source,
            confidence=confidence,
            goal=goal,
            metadata=metadata or {}
)

        )


    ####################################################################
    # Decorate a thought with parser information
    ####################################################################

    def _decorate_thought(self, thought, parse_result):

        thought.intent = getattr(parse_result, "intent", "")

        thought.entities = getattr(parse_result, "entities", [])

        thought.triples = getattr(parse_result, "triples", [])

        thought.metadata["parse_result"] = parse_result

    ####################################################################
    # Main thinking function
    ####################################################################

    def think(self, parse_result):

        self.clear()

        intent = parse_result.intent
        entities = []

        if hasattr(parse_result, "entities"):
            entities = parse_result.entities

        ############################################################
        # Greeting
        ############################################################

        if intent == "GREETING":

            self.add(
                "The user is greeting me.",
                priority=1.0,
                source="conversation",
                goal="GREET"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)

        ############################################################
        # Question
        ############################################################

        elif intent == "QUESTION":

            # 1. Add a thought to resolve the question
            self.add(
                "The user is asking a question.",
                priority=1.0,
                source="conversation",
                goal="RESPOND"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)

            # 2. Add an explicit search memory look-up trace if we have entities
            if entities:
                joined_entities = ", ".join(f"'{e}'" for e in entities)
                self.add(
                    f"Search memory for relationships involving: {joined_entities}.",
                    priority=0.9,
                    source="memory",
                    goal="RETRIEVE_FACT"
                )

        ############################################################
        # Teaching
        ############################################################

        elif intent == "TEACH":

            self.add(
                "The user is teaching me something.",
                priority=1.0,
                source="learning",
                goal="STORE_FACT"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
            if hasattr(parse_result, "subject"):

                self.add(
                    f"Remember information about '{parse_result.subject}'.",
                    priority=0.95,
                    source="memory",
                    goal="STORE_FACT"
                )

        ############################################################
        # Correction
        ############################################################

        elif intent == "CORRECTION":

            self.add(
                "The user is correcting existing knowledge.",
                priority=0.95,
                source="learning",
                goal="UPDATE_FACT"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
        ############################################################
        # Thanks
        ############################################################

        elif intent == "THANKS":

            self.add(
                "The user is thanking me.",
                priority=0.80,
                source="conversation",
                goal="THANK"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
        ############################################################
        # Farewell
        ############################################################

        elif intent == "FAREWELL":

            self.add(
                "The conversation is ending.",
                priority=0.80,
                source="conversation",
                goal="FAREWELL"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
        ############################################################
        # Emotion
        ############################################################

        elif intent == "EMOTION":

            self.add(
                "The user expressed an emotion.",
                priority=0.90,
                source="social",
                goal="EMPATHIZE"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
        ############################################################
        # Opinion
        ############################################################

        elif intent == "OPINION":

            self.add(
                "The user expressed an opinion.",
                priority=0.75,
                source="reasoning",
                goal="DISCUSS"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)
        ############################################################
        # Default
        ############################################################

        else:

            self.add(
                "Understand the user's statement.",
                priority=0.60,
                source="general",
                goal="RESPOND"
            )
            thought = self.active_thoughts[-1]
            self._decorate_thought(thought, parse_result)

        return self.active_thoughts

    ####################################################################
    # Thought utilities
    ####################################################################

    def highest_priority(self):

        if not self.active_thoughts:

            return None

        return max(
            self.active_thoughts,
            key=lambda t: t.priority
        )

    def thoughts_by_goal(self, goal):

        return [
            thought
            for thought in self.active_thoughts
            if thought.goal == goal
        ]

    def thoughts_by_source(self, source):

        return [
            thought
            for thought in self.active_thoughts
            if thought.source == source
        ]

    def summary(self):

        return [

            {
                "text": t.text,
                "goal": t.goal,
                "source": t.source,
                "priority": t.priority,
                "confidence": t.confidence
            }

            for t in self.active_thoughts

        ]
        
def _decorate_thought(self, thought, parse_result):

    thought.intent = getattr(parse_result, "intent", "")

    thought.entities = getattr(parse_result, "entities", [])

    if hasattr(parse_result, "triples"):
        thought.triples = parse_result.triples