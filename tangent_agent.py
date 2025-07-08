# tangent_agent.py

"""
Prototype: Tangent Consciousness Agent (Trait-Based Goal Modeling with Layered Role Skew)

This agent models structured human-like goals with:
- Decay-based priority scores

- Hierarchical identity structure: category → subcategory → trait
- Trait-based coefficients informed by personality schemas (e.g., MBTI, Jungian types)
- Layered roles (e.g., parent, spouse, introvert) that modulate trait expression using combined skew factors
- Synecdochic trait expressions with associated standard deviation coefficients

The agent interprets stimuli and reprioritizes internal goals based on dynamic interactions between goals, traits, and layered roles.
"""

import random
import math
import time
from collections import defaultdict

class RoleContext:
    def __init__(self, layered_role_skews):
        """
        layered_role_skews: list of dicts, each mapping trait → skew coefficient.
        These represent distinct roles (e.g., parent, engineer, extrovert).
        Final skew is the product of all active skews for a trait.
        """
        self.layered_role_skews = layered_role_skews

    def skew_for(self, trait):
        skew = 1.0
        for role in self.layered_role_skews:
            skew *= role.get(trait, 1.0)
        return skew


class Goal:
    def __init__(self, name, category=None, subcategory=None, trait=None, trait_sigma=1.0, initial_score=1.0):
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.trait = trait  # terminal psychological identity
        self.trait_sigma = trait_sigma  # weighting coefficient (like IQ or MBTI strength)
        self.score = initial_score  # Priority or salience
        self.last_updated = time.time()

    def decay(self, rate=0.01):
        elapsed = time.time() - self.last_updated
        self.score *= math.exp(-rate * elapsed)
        self.last_updated = time.time()

    def reinforce(self, boost=0.5):
        self.score += boost * self.trait_sigma
        self.last_updated = time.time()

    def weighted_score(self, role_context=None):
        skew = role_context.skew_for(self.trait) if role_context else 1.0
        return self.score * self.trait_sigma * skew

    def __repr__(self):
        return (
            f"Goal(name='{self.name}', score={self.score:.2f}, category={self.category}, "
            f"subcategory={self.subcategory}, trait={self.trait}, sigma={self.trait_sigma})"
        )


class TangentAgent:
    def __init__(self, goals, role_context=None):
        self.goals = {g.name: g for g in goals}
        self.memory = []
        self.state = {}
        self.role_context = role_context or RoleContext([])

    def perceive(self, stimulus):
        self._decay_goals()
        relevance_map = self._assess_relevance(stimulus)
        best_match = max(relevance_map.items(), key=lambda kv: kv[1], default=(None, 0))

        interpretation = {
            "stimulus": stimulus,
            "best_goal": best_match[0],
            "relevance_score": best_match[1],
            "aligned": best_match[1] > 0.3
        }

        if interpretation["aligned"] and best_match[0] in self.goals:
            self.goals[best_match[0]].reinforce()

        self.memory.append(interpretation)
        return interpretation

    def _decay_goals(self):
        for goal in self.goals.values():
            goal.decay()

    def _assess_relevance(self, stimulus):
        scores = {}
        for goal in self.goals.values():
            keyword = goal.name.lower()
            if keyword in stimulus.lower():
                scores[goal.name] = goal.weighted_score(self.role_context)
        return scores

    def prioritized_goals(self):
        return sorted(self.goals.values(), key=lambda g: g.weighted_score(self.role_context), reverse=True)

    def act(self):
        if not self.memory:
            return "Waiting for stimuli..."

        latest = self.memory[-1]
        if latest["aligned"]:
            return f"Reinforcing '{latest['best_goal']}': aligned with '{latest['stimulus']}'."
        else:
            return f"Holding stimulus '{latest['stimulus']}'—not yet actionable."


# --- Example Run ---
if __name__ == "__main__":
    parent_role = {
        "competitive": 0.8,
        "nurturing": 1.4,
        "constructive": 1.0
    }

    introvert_role = {
        "expressive": 0.7,
        "analytical": 1.2,
        "visionary": 1.1
    }

    engineer_role = {
        "analytical": 1.5,
        "constructive": 1.2
    }

    layered_roles = [parent_role, introvert_role, engineer_role]

    goals = [
        Goal("build", category="development", subcategory="systems", trait="constructive", trait_sigma=1.2),
        Goal("model", category="architecture", subcategory="simulation", trait="analytical", trait_sigma=1.4),
        Goal("future", category="direction", subcategory="planning", trait="visionary", trait_sigma=1.5),
        Goal("publish", category="communication", subcategory="output", trait="expressive", trait_sigma=1.1),
        Goal("eat", category="physical", subcategory="needs", trait="survival", trait_sigma=0.7, initial_score=0.2)
    ]

    agent = TangentAgent(goals, role_context=RoleContext(layered_roles))

    stimuli = [
        "The model is progressing.",
        "We should go outside.",
        "Future versions will be more advanced.",
        "Don't forget to publish the results.",
        "I'm feeling hungry."
    ]

    for s in stimuli:
        print("Input:", s)
        result = agent.perceive(s)
        print("Interpretation:", result)
        print("Action:", agent.act())
        print("Prioritized Goals:", agent.prioritized_goals())
        print("---")
