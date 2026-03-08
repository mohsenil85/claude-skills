---
name: review
description: Review code changes for bugs, security issues, and style problems
disable-model-invocation: true
---

# Code Review

Review code changes and provide structured feedback with severity levels.

## Input

Accepts an optional argument:
- **PR number** (e.g., `/review 42`) — review that PR's diff
- **No argument** — review the current uncommitted diff (`git diff` + `git diff --staged`)

## Process

1. **Get the diff**:
   - If PR number given: `gh pr diff <number>`
   - If no argument: `git diff` and `git diff --staged`
   - If no diff at all, check `git diff main..HEAD` for branch changes

2. **Read context**: For each changed file, read enough surrounding code to understand the change in context. Don't review the diff in isolation — understand what the code does.

3. **Analyze for issues** in these categories:
   - **Bugs**: Logic errors, off-by-one, null/undefined access, race conditions, resource leaks
   - **Security**: Injection, XSS, auth bypass, secrets in code, unsafe deserialization, path traversal
   - **Logic**: Wrong assumptions, missing edge cases, incorrect error handling, silent failures
   - **Style**: Naming, dead code, unnecessary complexity, inconsistency with surrounding code

4. **Output structured review**:

For each finding, use this format:

```
### [CRITICAL|WARNING|NIT] Brief description
**File**: path/to/file.ext:L42-L50
**Category**: Bug | Security | Logic | Style

Description of the issue.

**Suggested fix**:
\`\`\`diff
- old code
+ new code
\`\`\`
```

5. **Summary**: End with a brief overall assessment — is this safe to merge? What's the most important thing to address?

## Severity levels

- **CRITICAL**: Must fix before merge. Bugs that will break things, security vulnerabilities, data loss risks.
- **WARNING**: Should fix. Logic issues, poor error handling, potential problems under certain conditions.
- **NIT**: Optional. Style, naming, minor improvements. Don't block a merge for nits.

## Rules

- Be specific — point to exact lines, not vague "this could be better"
- If the code looks good, say so. Don't manufacture issues.
- Don't suggest style changes that contradict the project's existing conventions
- Focus on substance over style — one real bug matters more than ten nits
- If reviewing a PR, check the PR description for context on what the change is trying to do
