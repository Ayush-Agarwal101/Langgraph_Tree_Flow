class DecisionTracker:

    def __init__(self):
        self.decisions = {}

    def add(self, full_path, decision, reason, mandatory):
        self.decisions[full_path] = {
            "decision": decision,
            "reason": reason,
            "mandatory": mandatory
        }

    def get(self, full_path):
        return self.decisions.get(full_path)

    def all(self):
        return self.decisions
