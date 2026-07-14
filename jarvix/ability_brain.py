"""
ability_brain.py

Jarvix Ability Brain v1.5 (Integrated with ConceptReasoner)

Purpose:
- Store executable abilities.
- Decide whether an ability can answer a request.
- Execute the ability.
- Allow new abilities to be registered later.
"""

from __future__ import annotations

import random
import re
from typing import Callable, Dict, Optional

# Import the ConceptReasoner (make sure the path matches your project structure)
from .concept_reasoner import ConceptReasoner


# --------------------------------------------------
# Ability
# --------------------------------------------------

class Ability:

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable[[str], str],
        keywords=None
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.keywords = set(keywords or [])

    def matches(self, text: str) -> bool:
        text = text.lower()

        if self.name.lower() in text:
            return True

        return any(word in text for word in self.keywords)

    def execute(self, text: str) -> str:
        return self.handler(text)


# --------------------------------------------------
# Ability Brain
# --------------------------------------------------

class AbilityBrain:

    def __init__(self, agent_instance=None):
        self.abilities: Dict[str, Ability] = {}
        self.agent = agent_instance
        self.reasoner: Optional[ConceptReasoner] = None

        self._register_builtin()
        
        # If the agent is passed on init, bind it immediately
        if agent_instance:
            self.bind_agent(agent_instance)

    def bind_agent(self, agent):
        """Binds the main Jarvix agent instance to access brain, memory, and graph assets."""
        self.agent = agent
        
        # Accessing the graph and reasoner from Jarvix's multi-layered Brain pipeline
        graph = getattr(agent, "graph", None) or getattr(agent.brain, "graph", None)
        reasoner = getattr(agent, "reasoner", None) or getattr(agent.brain, "reasoner", None)
        
        # Pull the primary memory system (fallback to agent's default if needed)
        memory = getattr(agent, "memory", None) or getattr(agent, "memory_manager", None)

        # Instantiate ConceptReasoner using the resolved components
        self.reasoner = ConceptReasoner(
            graph=graph,
            reasoner=reasoner,
            memory=memory
        )

    # -------------------------

    def register(self, ability: Ability):
        self.abilities[ability.name.lower()] = ability

    # -------------------------

    def can_handle(self, text: str) -> bool:
        # 1. First, check if our new ConceptReasoner can handle the problem type
        if self.reasoner:
            problem_type = self.reasoner.classify_problem(text)
            if problem_type in ["arithmetic", "counting", "pipeline"]:
                return True

        # 2. Fall back to standard keyword-matching abilities
        for ability in self.abilities.values():
            if ability.matches(text):
                return True

        return False

    # -------------------------

    def execute(self, text: str) -> Optional[str]:
        # 1. First, let the ConceptReasoner try to handle it if initialized
        if self.reasoner:
            problem_type = self.reasoner.classify_problem(text)
            if problem_type in ["arithmetic", "counting", "pipeline"]:
                result = self.reasoner.understand_request(text)
                if result.success:
                    return (
                        f"[Ability Engine] Answer: {result.answer}\n"
                        f"Reasoning details:\n{result.explanation}"
                    )

        # 2. Fall back to standard match-and-execute loop
        for ability in self.abilities.values():
            if ability.matches(text):
                return ability.execute(text)

        return None

    # --------------------------------------------------
    # Built-in abilities
    # --------------------------------------------------

    def _register_builtin(self):

        self.register(
            Ability(
                "count",
                "Count numbers.",
                self._count,
                keywords=["count", "counting"]
            )
        )

        self.register(
            Ability(
                "hello",
                "Greets the user.",
                self._hello,
                keywords=["hello", "hi", "hey"]
            )
        )

        self.register(
            Ability(
                "echo",
                "Echo text.",
                self._echo,
                keywords=["echo", "repeat"]
            )
        )

        self.register(
            Ability(
                "reverse",
                "Reverse text.",
                self._reverse,
                keywords=["reverse", "backwards"]
            )
        )

        self.register(
            Ability(
                "uppercase",
                "Convert text to uppercase.",
                self._uppercase,
                keywords=["uppercase", "caps"]
            )
        )

        self.register(
            Ability(
                "lowercase",
                "Convert text to lowercase.",
                self._lowercase,
                keywords=["lowercase"]
            )
        )

        self.register(
            Ability(
                "random",
                "Generate a random number.",
                self._random,
                keywords=["random"]
            )
        )

        self.register(
            Ability(
                "coin",
                "Flip a coin.",
                self._coin,
                keywords=["coin", "flip"]
            )
        )

        self.register(
            Ability(
                "dice",
                "Roll a die.",
                self._dice,
                keywords=["dice", "roll"]
            )
        )

        self.register(
            Ability(
                "help",
                "Show abilities.",
                self._help,
                keywords=["help", "abilities"]
            )
        )

    # --------------------------------------------------
    # Ability Handlers
    # --------------------------------------------------

    def _echo(self, text: str) -> str:
        return text.replace("echo", "", 1).strip()

    def _reverse(self, text: str) -> str:
        text = text.replace("reverse", "", 1).strip()
        return text[::-1]

    def _uppercase(self, text: str) -> str:
        return text.upper()

    def _lowercase(self, text: str) -> str:
        return text.lower()

    def _random(self, text: str) -> str:
        return str(random.randint(1, 100))

    def _coin(self, text: str) -> str:
        return random.choice(["Heads", "Tails"])

    def _dice(self, text: str) -> str:
        return str(random.randint(1, 6))

    def _help(self, text: str) -> str:
        lines = ["I can do:"]
        for ability in self.abilities.values():
            lines.append(f"- {ability.name}: {ability.description}")
        return "\n".join(lines)

    def _count(self, text: str) -> str:
        m = re.search(r"\d+", text)
        end = int(m.group()) if m else 10
        end = max(0, min(end, 100))
        return ", ".join(str(i) for i in range(end + 1))

    def _hello(self, text: str) -> str:
        return "Hello! Nice to see you."


# --------------------------------------------------
# Example
# --------------------------------------------------

if __name__ == "__main__":

    brain = AbilityBrain()

    while True:
        q = input("> ")

        if brain.can_handle(q):
            print(brain.execute(q))
        else:
            print("No matching ability.")