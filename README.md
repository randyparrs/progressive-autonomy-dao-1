# Progressive Autonomy DAO

A DAO experiment built on GenLayer where the AI agent gradually takes over decision making as it proves itself trustworthy.

## What is this?

I wanted to build something that shows off what GenLayer can actually do differently from regular smart contracts. The idea is simple  instead of humans always voting on everything, the DAO starts with full human control and slowly gives the AI more power based on how well it performs.

The AI starts at level 0 (just watching) and can reach level 3 (full autonomy) if the community keeps rating its decisions as correct.

## Autonomy Levels

| Level | Name | What happens |
|-------|------|-------------|
| 0 | HUMAN_ONLY | Humans vote on everything |
| 1 | AI_ASSISTED | AI gives a recommendation, humans decide |
| 2 | AI_SUPERVISED | AI decides, humans can override |
| 3 | AI_AUTONOMOUS | AI decides everything, community audits |

## How it works

When someone submits a proposal, the contract calls an LLM to evaluate it. Multiple validators on the GenLayer network independently run the same evaluation and have to agree on the result that's the Equivalence Principle in action.

After a proposal resolves, members can rate whether the AI made a good call. Good ratings push the AI toward higher autonomy, bad ones push it back down.

## Built with

- GenLayer Studio
- Python (GenLayer Intelligent Contract SDK)
- `gl.vm.run_nondet_unsafe` for Equivalence Principle
- Optimistic Democracy consensus

## How to run it

1. Go to [GenLayer Studio](https://studio.genlayer.com)
2. Create a new file and paste `progressive_autonomy_dao.py`
3. Set execution mode to Normal (Full Consensus)
4. Deploy with your address as `owner_address`
5. Call `submit_proposal` and watch the AI evaluate it

## Functions

- `submit_proposal(title, description)` — submit a new proposal
- `vote(proposal_id, support)` — vote yes or no
- `rate_ai_decision(proposal_id, was_correct)` — rate the AI
- `get_dao_summary()` — see current autonomy level and AI score
- `get_proposal(proposal_id)` — check a specific proposal
- `add_member(address)` — add a new DAO member

## Notes

This is a hackathon project for the GenLayer Incentivized Builder Program, AI Governance track. The contract starts at AI_ASSISTED level so you can see the AI evaluation working right away.
