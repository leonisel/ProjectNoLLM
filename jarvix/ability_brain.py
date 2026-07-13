"""
ability_brain.py

Jarvix Ability Brain v1

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

    def __init__(self):

        self.abilities: Dict[str, Ability] = {}

        self._register_builtin()

    # -------------------------

    def register(self, ability: Ability):

        self.abilities[ability.name.lower()] = ability

    # -------------------------

    def can_handle(self, text: str) -> bool:

        for ability in self.abilities.values():

            if ability.matches(text):
                return True

        return False

    # -------------------------

    def execute(self, text: str) -> Optional[str]:

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