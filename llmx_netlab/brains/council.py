"""The council: Carbon 4 decides, Muse advises, strictest wins."""
from .carbon4 import Carbon4
from .muse import MuseAdvisor


class Council:
    def __init__(self):
        self.decider = Carbon4()
        self.advisor = MuseAdvisor()

    def review(self, action, question, evidence):
        decision = self.decider.decide(action, evidence, question)
        advice = self.advisor.advise(question, evidence)
        return {"decision": decision, "advice": advice,
                "final": decision["verdict"]}
