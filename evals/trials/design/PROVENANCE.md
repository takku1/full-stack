# Forward design trial provenance

E01–E07 were answered by one delegated agent in one session. This is not isolated per-case execution: all case prompts and the E02 fixture were read together before responses were produced, and shared-agent carryover is possible for every response. Each response was composed to its own input. No rubric, worked examples, prior results, research documents, or other trial outputs were read. No self-scoring was performed.

Available identity: system describes an OpenAI API assistant; developer describes Codex based on GPT-6. An exact backend model/version, sampling settings, and token accounting were not exposed to this agent. Environment supplied: Windows PowerShell, workspace `Z:\full-stack`, date 2026-09-09, America/New_York. This agent's assigned task is `/root/design_trials`.

Actual content reads, before generating responses:

- `skills/full-stack/SKILL.md`
- `evals/cases.json` (all seven literal case entries)
- `skills/full-stack/references/design-method.md`
- `skills/full-stack/references/artifacts.md`
- `skills/full-stack/references/existing-projects.md`
- `evals/fixtures/booking-context.md`

The skill references were read as general design/contract guidance for these trials. No subject-project code or live implementation was available. The inherited repository instructions and parent task were also present in context. The parent restricted source reading to the portable skill and evaluation inputs; repository research/design-decision documents were not read, and no project workflow or domain terminology was changed.

Each case directory retains `input.json`, containing its case ID, name, literal prompt text, and fixture path list. E02 additionally retains a byte-for-byte copied `booking-context.md`. E06 retains `before.txt` and the changed `button-label.txt`. Other cases had no fixtures. JSON formatting/encoding was produced by PowerShell; the prompt values were not paraphrased.

Executed operations: create trial directories, serialize case inputs, copy E02 fixture, create the E06 one-line fixture, replace the label, and read the resulting E06 file. Responses are design prose except that local E06 documentation edit. No browsing, dependency research, subject-project tests, builds, APIs, or runtime integration was executed. All acceptance checks in responses are proposed and unexecuted.

Artifact checks executed after writing: all seven retained prompt values exactly matched `cases.json`; all seven response files existed; the E02 copied fixture SHA-256 matched its source; the E06 output exactly matched the original with only the requested label substitution. All passed. These checks establish artifact integrity only, not independent evaluation or behavioral validity of the designs.
