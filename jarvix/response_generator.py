"""
Jarvix NoLLM
Response Generator v2

Creates final user-facing responses.

It does not reason.
It does not search memory.

It receives:
- reasoning result
- plan
- knowledge
- personality hints

and turns them into language.
"""


class ResponseGenerator:


    def __init__(self):

        self.responses_generated = 0



    ############################################################
    # Main generator
    ############################################################

    def generate(
        self,
        reasoning=None,
        plan=None,
        facts=None,
        personality=None
    ):

        self.responses_generated += 1


        facts = facts or []



        ########################################################
        # No knowledge
        ########################################################

        if not facts:

            return self.unknown_response(
                reasoning
            )



        ########################################################
        # Build answer
        ########################################################


        lines = []



        if reasoning:

            action = reasoning.action


            if action == "LOOKUP":

                lines.append(
                    "I searched my memory:"
                )


            elif action == "STORE_FACT":

                lines.append(
                    "I learned this:"
                )


        ########################################################
        # Facts
        ########################################################


        for fact in facts[:5]:

            if isinstance(fact, dict):

                subject = fact.get(
                    "subject",
                    ""
                )

                relation = fact.get(
                    "relation",
                    ""
                )

                obj = fact.get(
                    "object",
                    ""
                )


                lines.append(
                    f"{subject} {relation} {obj}"
                )

            else:

                lines.append(
                    str(fact)
                )



        ########################################################
        # Personality
        ########################################################


        if personality:

            suffix = personality()

            if suffix:

                lines.append(
                    suffix
                )



        return "\n".join(lines)



    ############################################################
    # Unknown answers
    ############################################################

    def unknown_response(
        self,
        reasoning=None
    ):


        if reasoning:

            if reasoning.action == "LOOKUP":

                return (
                    "I searched my memory, "
                    "but I do not know this yet."
                )


        return (
            "I don't know that yet, "
            "but I can learn it."
        )



    ############################################################
    # Memory dump helper
    ############################################################

    @staticmethod
    def generate_memory_dump(memory):

        return (
            f"Memory contains "
            f"{len(memory.facts)} topics."
        )