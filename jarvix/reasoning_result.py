class ReasoningEngine:

    def reason(self, parse_result):

        result = ReasoningResult()

        self.determine_goal(parse_result, result)

        self.collect_memory(parse_result, result)

        self.apply_logic(result)

        self.detect_conflicts(result)

        self.evaluate_confidence(result)

        self.plan_action(result)

        return result