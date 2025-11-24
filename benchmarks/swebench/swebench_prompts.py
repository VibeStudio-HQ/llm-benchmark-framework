"""
Optimized prompts for SWE-bench
Based on research from top-performing models
"""


class SWEBenchPrompts:
    """Collection of different SWE-bench prompting strategies"""

    @staticmethod
    def minimal(instance: dict) -> str:
        """
        Minimal prompt - Let model decide format
        Used by: GPT-4, Claude baseline
        """
        return f"""You are an expert software engineer. Fix the following GitHub issue by generating a code patch.

Repository: {instance['repo']}
Issue: {instance['problem_statement']}

Generate a git diff patch to fix this issue. Provide only the patch code."""

    @staticmethod
    def structured(instance: dict) -> str:
        """
        Structured prompt with clear instructions
        Best for general-purpose models
        """
        return f"""You are a software engineer tasked with fixing a GitHub issue.

REPOSITORY: {instance['repo']}
ISSUE ID: {instance['instance_id']}

PROBLEM DESCRIPTION:
{instance['problem_statement']}

TASK:
Generate a unified diff patch that fixes this issue. The patch must:
1. Be in valid unified diff format
2. Start with 'diff --git a/path b/path'
3. Include proper line numbers with @@ markers
4. Show context lines around changes
5. Be complete and applicable

OUTPUT FORMAT:
Generate ONLY the patch code. No explanations or comments.

PATCH:
"""

    @staticmethod
    def few_shot(instance: dict) -> str:
        """
        Few-shot prompt with example
        Helps models understand expected format
        """
        return f"""Fix GitHub issues by generating unified diff patches.

EXAMPLE:
Issue: Function returns None instead of empty list
Patch:
diff --git a/utils.py b/utils.py
--- a/utils.py
+++ b/utils.py
@@ -10,7 +10,7 @@ def get_items():
     if not items:
-        return None
+        return []
     return items

---

NOW FIX THIS ISSUE:

Repository: {instance['repo']}
Issue ID: {instance['instance_id']}

Problem:
{instance['problem_statement']}

Generate the patch (unified diff format only):
"""

    @staticmethod
    def chain_of_thought(instance: dict) -> str:
        """
        Chain-of-thought prompting
        Encourages reasoning before patching
        """
        return f"""You are an expert software engineer. Fix the following GitHub issue using step-by-step reasoning.

Repository: {instance['repo']}
Issue: {instance['instance_id']}

Problem Description:
{instance['problem_statement']}

Instructions:
1. First, analyze what the issue is asking for
2. Identify which files likely need changes
3. Determine the specific code changes needed
4. Generate a unified diff patch

Think through the problem, then provide ONLY the final patch in unified diff format.

Analysis and Patch:
"""

    @staticmethod
    def agent_style(instance: dict) -> str:
        """
        Agent-style prompt with role and constraints
        Best for instruct-tuned models
        """
        return f"""<role>
You are a senior software engineer with expertise in debugging and fixing code issues.
</role>

<task>
Fix the GitHub issue below by generating a precise code patch.
</task>

<repository>
{instance['repo']}
</repository>

<issue_id>
{instance['instance_id']}
</issue_id>

<problem>
{instance['problem_statement']}
</problem>

<requirements>
- Output ONLY a unified diff patch
- Use proper diff format: diff --git a/file b/file
- Include @@ line markers
- Show 3 lines of context before/after changes
- No explanations, just the patch
</requirements>

<output>
"""

    @staticmethod
    def direct_instruction(instance: dict) -> str:
        """
        Direct, imperative instructions
        Works well for code-specialized models
        """
        return f"""Generate a unified diff patch to fix this issue.

Repo: {instance['repo']}
Issue: {instance['instance_id']}

{instance['problem_statement']}

Requirements:
- Valid unified diff format
- Start with: diff --git a/<file> b/<file>
- Include @@ line numbers
- Show context lines

Patch:
diff --git"""

    @staticmethod
    def template_based(instance: dict) -> str:
        """
        Template with placeholders
        Guides model to fill in the structure
        """
        return f"""Complete this patch template to fix the GitHub issue.

Issue Information:
- Repository: {instance['repo']}
- Issue ID: {instance['instance_id']}
- Problem: {instance['problem_statement']}

Patch Template (fill in the changes):

diff --git a/[FILE_PATH] b/[FILE_PATH]
--- a/[FILE_PATH]
+++ b/[FILE_PATH]
@@ -[START_LINE],[NUM_LINES] +[START_LINE],[NUM_LINES] @@
[CONTEXT_LINE]
-[OLD_CODE_LINE]
+[NEW_CODE_LINE]
[CONTEXT_LINE]

Generate the complete patch:
"""

    @staticmethod
    def zero_shot_cot(instance: dict) -> str:
        """
        Zero-shot chain-of-thought
        Simple "Let's think step by step" trigger
        """
        return f"""Fix the following GitHub issue. Let's think step by step.

Repository: {instance['repo']}
Issue: {instance['problem_statement']}

Generate a unified diff patch to resolve this. Let's approach this systematically:

1. Understand the problem
2. Identify the fix
3. Generate the patch

Patch:
"""

    @staticmethod
    def best_practice(instance: dict) -> str:
        """
        Current best practice based on SWE-bench leaderboard
        Combines clarity, structure, and constraints
        """
        return f"""Fix the GitHub issue below by generating a git diff patch.

<repository>{instance['repo']}</repository>
<issue>{instance['instance_id']}</issue>

<description>
{instance['problem_statement']}
</description>

<instructions>
1. Analyze the issue carefully
2. Generate a unified diff patch that fixes it
3. Ensure the patch is in valid git diff format
4. Include only the necessary changes
</instructions>

<format>
diff --git a/path/to/file.py b/path/to/file.py
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -line,count +line,count @@
 context
-old code
+new code
 context
</format>

Generate the patch now (patch only, no explanation):
"""


# Default prompt to use - matches original working code
DEFAULT_PROMPT = SWEBenchPrompts.minimal
