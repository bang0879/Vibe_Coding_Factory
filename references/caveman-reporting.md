# Caveman Reporting

Use Caveman format only between agents or inside task status handoffs. Use normal Korean for user-facing reports.

## Format

Keep it terse:

```text
DONE <task-id>
DID <concrete work performed>
OUT <artifact/result produced>
HANDOFF <next-agent|none>: <what was handed off>
EVIDENCE <command/browser check/file proof>
CHECK pass <passed>/<total>
FILES <path1>, <path2>
NEXT <next-task-id|user-approval|none>
```

For failures:

```text
FAIL <task-id>
CAUSE <short cause>
CHECK pass <passed>/<total>
FIX <recommended next action>
```

For blockers:

```text
BLOCKED <task-id>
CAUSE <short cause>
TRIED <n>/3
NEED <specific input>
```

## Rules

- No greetings.
- No prose paragraphs.
- No speculation.
- Mention only task id, concrete work, output, handoff, evidence, checks, files, blocker, and next step.
- `DID` must not describe the persona's general responsibility. It must say what changed or what was verified in this task.
- `HANDOFF` must name the next agent and the exact output being handed over. Use `none` only at the end of a flow.
- Do not hide uncertainty. Use `NEED` when input is required.
