# research-agent job job_01M7ZKXZFAD4BXCP0T5QAXWVCF

Read 2026-11-21, outcome `partial`, cost USD 0.045487. Claims kept by the service only with a
verbatim quote found in the source. Sources 2, 8 and 10 were flagged `injectionSuspected`.
This file is the claim list as returned; the full job stays in research-agent under the id above.

| Claim | Source |
|---|---|
| Memory types split into two dimensions: how long information stays useful (working, session, long-term) and what it represents (episodic, semantic, procedural). | arize.com/resources/ai-memory (flagged) |
| Most AI memory systems perform four jobs: select, store, retrieve, maintain. | same |
| A memory system needs mechanisms for replacement, consolidation, invalidation, expiration, compaction and deletion. | same |
| A system can store and retrieve the correct information while the agent still ignores it, misuses it, or applies it when newer context should take priority. | same |
| Zep facts are bi-temporal: `valid_at` and `invalid_at` track when something was true, separately from when the system learned it. An invalidated fact stays in the graph. | getzep.com/blog/how-zep-tracks-provenance-in-agent-memory |
| A produced fact may draw on several sources and its wording matches none, so one source pointer cannot be recovered later by string matching. | same |
| Defaults are still "never expire": Mem0 memories without an expiration date never expire; Google Memory Bank sets no expiration unless a TTL is configured. A user reported on 2026-04-24 stale or contradictory facts for mutable attributes. | botnet.com/resources/ops-memory-expiry-what-changed |
| Google Memory Bank supports separate TTLs for direct writes and for memories created or updated by LLM extraction. | same |
| Memory poisoning requires only one successful write. Agents designed to write and retrieve memory more aggressively are more exploitable. Existing prompt injection defenses fail to cover it. | arxiv.org/html/2606.04329v2 (flagged) |
| Label provenance on every memory entry: source, identity, timestamp, model version. | learn.microsoft.com/en-us/security/zero-trust/sfi/manage-agentic-memory-safety |
| On LongMemEval-S, swapping only the embedding model shifts accuracy by +6.2pp at n=500; Mem0 beats MiniLM-RAG by +11pp but loses to cloud-RAG by 1.2pp. | arxiv.org/html/2606.29914v1 (flagged) |
| The right amount of memory is a property of the model: DeepSeek-V3.2 gains +9.5 points of task completion with its full 191-guideline set. | arxiv.org/abs/2611.26361 |

Not answered by the sources: LoCoMo results; MemGPT or Letta, A-MEM, the Anthropic memory tool,
LangMem; LongMemEval headline scores; measured results for Zep or Graphiti on a public benchmark.
