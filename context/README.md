# context/ — canonical repo documentation

Stable, ground-truth documentation for honeybee_grasshopper_ph: what it is, how a component is built, and the rules for changing it. Distinct from `planning/` (in-flight work) and `docs/` (the generated Hugo site — do not touch).

`CLAUDE.md` at the repo root is the dispatcher; this folder holds the docs it routes to.

## Index

| Doc | Read when you need… |
|-----|---------------------|
| [`PRD.md`](PRD.md) | What this repo is for and what deliberately lives upstream instead |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The two-file component pattern, the registry, `gh_io.IGH`, `.ghuser` regeneration, subpackage map |
| [`TECH_STACK.md`](TECH_STACK.md) | Dependencies, the fsdeploy dev loop, the release orchestrator, versioning |
| [`CODING_STANDARDS.md`](CODING_STANDARDS.md) | IronPython 2.7 rules, imports, type comments, formatting |

Related root docs: `WORKFLOW.md` (ecosystem build/release detail).

## Maintenance rule

When a decision changes how components are built or released, fold it into the relevant doc here. Keep these true.
