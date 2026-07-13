"""
thought_consolidator.py

Jarvix Thought Consolidator v1
"""

from __future__ import annotations

import re


class ThoughtConsolidator:

    def __init__(self, memory):

        self.memory = memory
        self.minimum_length = 80

    # ==========================================================
    # Public
    # ==========================================================

    def run_cycle(self):

        """
        Runs one consolidation pass.
        """

        for topic, fact, state in self.memory.get_unconsolidated():

            self.consolidate(topic, fact)

    # ==========================================================
    # Consolidation
    # ==========================================================

    def consolidate(self, topic, fact):

        # Already small enough
        if len(fact) < self.minimum_length:

            self.memory.mark_consolidated(topic, fact)
            return

        pieces = self.extract_atomic_facts(fact)

        # Couldn't simplify
        if len(pieces) <= 1:

            self.memory.mark_consolidated(topic, fact)
            return

        for piece in pieces:

            piece = piece.strip()

            if not piece:
                continue

            # Ignore duplicates
            if self.memory.get_fact_state(topic, piece):
                continue

            self.memory.add_fact(
                topic,
                piece,
                confidence=0.45
            )

            self.memory.link_fact(
                topic,
                fact,
                piece
            )

        self.memory.mark_consolidated(topic, fact)

    # ==========================================================
    # Fact Extraction
    # ==========================================================

    def extract_atomic_facts(self, text):

        """
        Very simple V1.

        Splits long thoughts into individual facts.
        """

        text = text.replace("\n", ". ")

        pieces = re.split(
            r"\.\s+|;\s+|\band\b|\bbut\b|\bbecause\b",
            text,
            flags=re.IGNORECASE
        )

        facts = []

        for piece in pieces:

            piece = piece.strip()

            if len(piece) < 5:
                continue

            facts.append(piece)

        return facts