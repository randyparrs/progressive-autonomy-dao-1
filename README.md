Progressive Autonomy DAO
A DAO experiment built on GenLayer where the AI agent gradually takes over decision making as it proves itself trustworthy. Built on Testnet Bradbury.
---
What is this
I wanted to build something that shows off what GenLayer can actually do differently from regular smart contracts. The idea is simple, instead of humans always voting on everything, the DAO starts with full human control and slowly gives the AI more power based on how well it performs.
The AI starts at level 1 (assisted) and can reach level 3 (full autonomy) if the community keeps rating its decisions as correct. If the AI starts making bad calls and the community rates it down, the autonomy drops back to lower levels. The whole thing is a feedback loop where trust is earned, not assumed.
---
Autonomy Levels
The DAO operates in four progressive levels of AI involvement.
Level 0 HUMAN_ONLY means humans vote on everything and the AI does not participate in decisions.
Level 1 AI_ASSISTED means the AI evaluates each proposal and gives a recommendation but humans still vote and make the final call.
Level 2 AI_SUPERVISED means the AI decides automatically but humans can override the decision through voting.
Level 3 AI_AUTONOMOUS means the AI decides everything on its own and the community audits the decisions afterwards.
---
How it works
When someone submits a proposal, the contract calls an LLM to evaluate it. Multiple validators on the GenLayer network independently run the same evaluation through `gl.vm.run_nondet_unsafe` and have to agree on the result before the recommendation is committed onchain. That is the Equivalence Principle in action.
After a proposal resolves, members can rate whether the AI made a good call using the `rate_ai_decision` function. Good ratings increase the AI community score and push it toward higher autonomy levels. Bad ratings drop the score and demote the AI back down. The thresholds are 60 for level 1, 75 for level 2, and 90 for level 3.
---
Functions
submit_proposal takes a title and a description and creates a new proposal. The AI automatically evaluates it if the autonomy level is 1 or higher.
vote takes a proposal id and a boolean support value to vote yes or no on a proposal.
rate_ai_decision takes a proposal id and a boolean was_correct value to rate whether the AI made the right call. This is what drives the autonomy progression.
add_member takes a member address and adds them to the DAO. Only the owner can call this.
get_dao_summary shows the current autonomy level, AI community score, total members, and total proposals.
get_proposal takes a proposal id and shows the full proposal state including votes and AI recommendation.
get_autonomy_level shows the current autonomy level as a name.
get_ai_score shows the current AI community score from 0 to 100.
---
Test results
I tested the DAO by submitting a proposal to allocate budget for community education. The AI evaluated it through Optimistic Democracy and recommended APPROVE with 100% confidence. After voting and rating the decision as correct, the AI score went to 100 out of 100 which automatically promoted the autonomy level from AI_ASSISTED to AI_SUPERVISED. This shows the progression mechanism working as intended where good performance unlocks more responsibility.
---
How to run it
Go to GenLayer Studio at https://studio.genlayer.com and create a new file called progressive_autonomy_dao.py. Paste the contract code and set execution mode to Normal Full Consensus. Deploy with your address as owner_address.
Follow this order and wait for FINALIZED at each step. Run get_dao_summary first, then submit_proposal with a title and description, then get_proposal to see the AI recommendation, then vote with the proposal id, then rate_ai_decision to evaluate the AI's call, then get_dao_summary again to see the updated autonomy level.
Note: the contract in this repository uses the Address type in the constructor as required by genvm-lint. When deploying in GenLayer Studio use a version that receives str in the constructor and converts internally with Address(owner_address) since Studio requires primitive types to parse the contract schema correctly.
---
Built with
GenLayer Intelligent Contract SDK in Python, gl.vm.run_nondet_unsafe for Equivalence Principle consensus, and Optimistic Democracy through GenLayer Studio.
---
Resources
GenLayer Docs: https://docs.genlayer.com
Optimistic Democracy: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy
Equivalence Principle: https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/optimistic-democracy/equivalence-principle
GenLayer Studio: https://studio.genlayer.com
Discord: https://discord.gg/8Jm4v89VAu
