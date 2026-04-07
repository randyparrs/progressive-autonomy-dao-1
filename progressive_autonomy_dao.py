# { "Depends": "py-genlayer:test" }

# ============================================================
#  Progressive Autonomy DAO
#  AI Governance Track — GenLayer Hackathon
#
#  A DAO that progressively delegates decision-making power
#  to an AI agent based on its track record of correct,
#  fair, and community-aligned decisions.
#
#  Autonomy Levels:
#    0 - HUMAN_ONLY    : All decisions require human voting
#    1 - AI_ASSISTED   : AI recommends, humans approve/veto
#    2 - AI_SUPERVISED : AI decides, humans can override
#    3 - AI_AUTONOMOUS : AI decides fully, community audits
#
#  Requirements met:
#     Optimistic Democracy consensus
#     Equivalence Principle (gl.vm.run_nondet_unsafe)
# ============================================================

import json
from genlayer import *
from dataclasses import dataclass


@allow_storage
@dataclass
class Proposal:
    id: u256
    title: str
    description: str
    proposer: str
    votes_for: u256
    votes_against: u256
    ai_recommendation: str   # "pending" | "APPROVE" | "REJECT"
    ai_confidence: u256      # 0-100
    status: str              # "pending" | "approved" | "rejected" | "ai_decided"
    human_overridden: bool


class ProgressiveAutonomyDAO(gl.Contract):

    # ── State ──────────────────────────────────────────────
    owner: str
    autonomy_level: u256
    ai_total_decisions: u256
    ai_correct_decisions: u256
    ai_community_score: u256
    proposal_count: u256
    proposals: DynArray[Proposal]
    members: DynArray[str]
    voted_log: DynArray[str]   # "proposal_id:address" flat list

    # ── Constructor ────────────────────────────────────────
    def __init__(self, owner_address: str):
        self.owner = owner_address
        self.autonomy_level = u256(1)
        self.ai_total_decisions = u256(0)
        self.ai_correct_decisions = u256(0)
        self.ai_community_score = u256(0)
        self.proposal_count = u256(0)
        self.members.append(owner_address)

    # ══════════════════════════════════════════════════════
    #  READ FUNCTIONS
    # ══════════════════════════════════════════════════════

    @gl.public.view
    def get_autonomy_level(self) -> str:
        names = {0: "HUMAN_ONLY", 1: "AI_ASSISTED", 2: "AI_SUPERVISED", 3: "AI_AUTONOMOUS"}
        return names.get(int(self.autonomy_level), "UNKNOWN")

    @gl.public.view
    def get_ai_score(self) -> u256:
        return self.ai_community_score

    @gl.public.view
    def get_proposal_count(self) -> u256:
        return self.proposal_count

    @gl.public.view
    def get_proposal(self, proposal_id: u256) -> str:
        idx = int(proposal_id)
        if idx >= len(self.proposals):
            return "Proposal not found"
        p = self.proposals[idx]
        return (
            f"ID: {int(p.id)} | "
            f"Title: {p.title} | "
            f"Status: {p.status} | "
            f"Votes For: {int(p.votes_for)} | "
            f"Votes Against: {int(p.votes_against)} | "
            f"AI Rec: {p.ai_recommendation} | "
            f"AI Confidence: {int(p.ai_confidence)}%"
        )

    @gl.public.view
    def get_dao_summary(self) -> str:
        names = {0: "HUMAN_ONLY", 1: "AI_ASSISTED", 2: "AI_SUPERVISED", 3: "AI_AUTONOMOUS"}
        level_name = names.get(int(self.autonomy_level), "UNKNOWN")
        return (
            f"=== Progressive Autonomy DAO ===\n"
            f"Autonomy Level: {level_name} ({int(self.autonomy_level)}/3)\n"
            f"AI Score: {int(self.ai_community_score)}/100\n"
            f"Members: {len(self.members)}\n"
            f"Proposals: {int(self.proposal_count)}"
        )

    # ══════════════════════════════════════════════════════
    #  ADD MEMBER (owner only)
    # ══════════════════════════════════════════════════════

    @gl.public.write
    def add_member(self, new_member: str) -> None:
        assert gl.message.sender_address == self.owner, "Only owner can add members"
        assert not self._is_member(new_member), "Already a member"
        self.members.append(new_member)

    # ══════════════════════════════════════════════════════
    #  SUBMIT PROPOSAL
    # ══════════════════════════════════════════════════════

    @gl.public.write
    def submit_proposal(self, title: str, description: str) -> None:
        sender = str(gl.message.sender_address)
        assert self._is_member(sender), "Not a DAO member"

        pid = self.proposal_count
        ai_rec = "pending"
        ai_conf = u256(0)
        status = "pending"
        level = int(self.autonomy_level)

        if level >= 1:
            # ── AI evaluates using Equivalence Principle ✅ ──
            rec, conf = self._ai_evaluate_proposal(title, description)
            ai_rec = rec
            ai_conf = u256(conf)

            if level == 3:
                # AI_AUTONOMOUS: AI decides immediately
                status = "ai_decided"
                self.ai_total_decisions = u256(int(self.ai_total_decisions) + 1)

        proposal = Proposal(
            id=pid,
            title=title,
            description=description,
            proposer=sender,
            votes_for=u256(0),
            votes_against=u256(0),
            ai_recommendation=ai_rec,
            ai_confidence=ai_conf,
            status=status,
            human_overridden=False,
        )
        self.proposals.append(proposal)
        self.proposal_count = u256(int(pid) + 1)

    # ══════════════════════════════════════════════════════
    #  VOTE
    # ══════════════════════════════════════════════════════

    @gl.public.write
    def vote(self, proposal_id: u256, support: bool) -> None:
        sender = str(gl.message.sender_address)
        assert self._is_member(sender), "Not a DAO member"

        idx = int(proposal_id)
        assert idx < len(self.proposals), "Invalid proposal"
        assert not self._has_voted(proposal_id, sender), "Already voted"

        p = self.proposals[idx]
        assert p.status == "pending", "Proposal not open for voting"

        if support:
            p.votes_for = u256(int(p.votes_for) + 1)
        else:
            p.votes_against = u256(int(p.votes_against) + 1)

        total_members = len(self.members)
        quorum = (total_members // 2) + 1

        if int(p.votes_for) >= quorum:
            p.status = "approved"
            if int(self.autonomy_level) == 2 and p.ai_recommendation == "REJECT":
                p.human_overridden = True
        elif int(p.votes_against) >= quorum:
            p.status = "rejected"
            if int(self.autonomy_level) == 2 and p.ai_recommendation == "APPROVE":
                p.human_overridden = True

        self.proposals[idx] = p
        self.voted_log.append(f"{int(proposal_id)}:{sender}")

    # ══════════════════════════════════════════════════════
    #  RATE AI DECISION
    # ══════════════════════════════════════════════════════

    @gl.public.write
    def rate_ai_decision(self, proposal_id: u256, was_correct: bool) -> None:
        sender = str(gl.message.sender_address)
        assert self._is_member(sender), "Not a DAO member"

        idx = int(proposal_id)
        assert idx < len(self.proposals), "Invalid proposal"

        p = self.proposals[idx]
        assert p.ai_recommendation != "pending", "No AI decision to rate"

        total = int(self.ai_total_decisions) + 1
        correct = int(self.ai_correct_decisions) + (1 if was_correct else 0)
        new_score = (correct * 100) // total


        self.ai_total_decisions = u256(total)
        self.ai_correct_decisions = u256(correct)
        self.ai_community_score = u256(new_score)

        self._update_autonomy_level(new_score)

    # ══════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ══════════════════════════════════════════════════════

    def _is_member(self, addr: str) -> bool:
        for i in range(len(self.members)):
            if self.members[i] == addr:
                return True
        return False

    def _has_voted(self, proposal_id: u256, addr: str) -> bool:
        key = f"{int(proposal_id)}:{addr}"
        for i in range(len(self.voted_log)):
            if self.voted_log[i] == key:
                return True
        return False

    def _update_autonomy_level(self, score: int) -> None:
        thresholds = {1: 60, 2: 75, 3: 90}
        current = int(self.autonomy_level)
        if current < 3:
            next_lvl = current + 1
            if score >= thresholds[next_lvl]:
                self.autonomy_level = u256(next_lvl)
                return
        if current > 0:
            if score < thresholds[current] - 10:
                self.autonomy_level = u256(current - 1)

    # ── AI Evaluation — Equivalence Principle  ──────────

    def _ai_evaluate_proposal(self, title: str, description: str) -> tuple:
        """
        Uses gl.vm.run_nondet_unsafe with leader/validator pattern.
        Leader evaluates the proposal with an LLM.
        Validator independently re-runs and compares:
          - recommendation must match exactly (APPROVE/REJECT)
          - confidence within ±10 points
        This satisfies both Optimistic Democracy and Equivalence Principle.
        """

        def leader_fn():
            prompt = f"""You are an AI governance agent for a DAO.
Evaluate the proposal below and return ONLY a JSON object, no extra text.

Proposal Title: {title}
Proposal Description: {description}

Return exactly:
{{"recommendation": "APPROVE", "confidence": 80, "reasoning": "one sentence"}}

Rules:
- recommendation: must be exactly "APPROVE" or "REJECT"
- confidence: integer 0-100
- reasoning: one sentence max

Consider: community benefit, feasibility, risks, decentralization alignment."""
            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            rec = data.get("recommendation", "REJECT")
            conf = int(data.get("confidence", 50))
            if rec not in ("APPROVE", "REJECT"):
                rec = "REJECT"
            conf = max(0, min(100, conf))
            return json.dumps({"recommendation": rec, "confidence": conf}, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                validator_raw = leader_fn()
                leader_data = json.loads(leader_result.calldata)
                validator_data = json.loads(validator_raw)
                # Recommendation must match exactly
                if leader_data["recommendation"] != validator_data["recommendation"]:
                    return False
                # Confidence within ±10 points
                return abs(leader_data["confidence"] - validator_data["confidence"]) <= 10
            except Exception:
                return False

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        data = json.loads(raw)
        return data["recommendation"], data["confidence"]
