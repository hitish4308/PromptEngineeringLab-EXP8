"""
Experiment 8 - Structured vs Unstructured Output

Task: Compare LLM output for the same topic (Python, Java, C++) when:
  1. Unstructured - free-text paragraph
  2. Structured  - markdown table with fixed columns

Demonstrates how explicit format instructions improve clarity,
comparability, and parseability.
"""

import os
import re
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ---------- Setup ----------
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get("NVIDIA_API_KEY")
if not api_key:
    raise SystemExit("NVIDIA_API_KEY not found. Create a .env file.")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)

MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.2
MAX_TOKENS = 600


# ---------- Prompts ----------
UNSTRUCTURED_PROMPT = (
    "Describe Python, Java, and C++ in a short paragraph."
)

STRUCTURED_PROMPT = (
    "Create a markdown table with exactly these columns: "
    "Language, Typing (static/dynamic), Primary Use Case, Difficulty (Beginner/Intermediate/Advanced).\n"
    "Include exactly three rows, one for each language: Python, Java, C++.\n"
    "Use this exact format:\n\n"
    "| Language | Typing | Primary Use Case | Difficulty |\n"
    "|----------|--------|------------------|------------|\n"
    "| ...      | ...    | ...              | ...        |\n\n"
    "Return ONLY the table with no introduction and no trailing text."
)


# ---------- Helpers ----------
def ask_llm(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = resp.choices[0].message.content
        return (content or "").strip() or "[no content returned]"
    except Exception as e:
        return f"[API error] {type(e).__name__}: {e}"


def parse_markdown_table(text: str):
    """Extract rows from a markdown table. Returns list of lists."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    table_lines = [l for l in lines if l.startswith("|") and l.endswith("|")]
    if len(table_lines) < 3:
        return None

    rows = []
    for i, line in enumerate(table_lines):
        # Skip the separator line (e.g., |---|---|)
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def show_block(label: str, prompt: str, response: str):
    width = 72
    print("=" * width)
    print(f"  {label}")
    print("=" * width)
    print("PROMPT:")
    print(textwrap.indent(prompt, "  "))
    print()
    print("RESPONSE:")
    print(textwrap.indent(response, "  "))
    print()
    print(f"  [chars: {len(response)} | words: {len(response.split())} | lines: {len(response.splitlines())}]")
    print()


# ---------- Main ----------
if __name__ == "__main__":
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE} | Max tokens: {MAX_TOKENS}")

    # ---- Unstructured ----
    print("\n>>> Sending UNSTRUCTURED prompt...")
    unstruct_resp = ask_llm(UNSTRUCTURED_PROMPT)
    show_block("UNSTRUCTURED", UNSTRUCTURED_PROMPT, unstruct_resp)

    # ---- Structured ----
    print(">>> Sending STRUCTURED prompt...")
    struct_resp = ask_llm(STRUCTURED_PROMPT)
    show_block("STRUCTURED (Markdown Table)", STRUCTURED_PROMPT, struct_resp)

    # ---- Parse the structured table ----
    print("=" * 72)
    print("  TABLE PARSER")
    print("=" * 72)
    rows = parse_markdown_table(struct_resp)
    if rows:
        print(f"Parsed {len(rows)} row(s):\n")
        headers = rows[0]
        data_rows = rows[1:]
        print("  HEADERS:", headers)
        for r in data_rows:
            print("  ROW:", r)
        print()
        print(f"  Expected 3 languages, found {len(data_rows)} row(s).")
        langs = [r[0].lower() if r else "" for r in data_rows]
        for lang in ("python", "java", "c++"):
            present = any(lang in l for l in langs)
            print(f"  '{lang}': {'FOUND' if present else 'MISSING'}")
    else:
        print("  Could not parse a markdown table from the structured response.")
        print("  (The model may have returned a different format.)")

    # ---- Comparison ----
    print("\n" + "=" * 72)
    print("  COMPARISON")
    print("=" * 72)
    print(f"{'Aspect':<28}{'Unstructured':<22}{'Structured':<22}")
    print("-" * 72)
    print(f"{'Format':<28}{'Free prose':<22}{'Markdown table':<22}")
    print(f"{'Characters':<28}{len(unstruct_resp):<22}{len(struct_resp):<22}")
    print(f"{'Words':<28}{len(unstruct_resp.split()):<22}{len(struct_resp.split()):<22}")
    print(f"{'Lines':<28}{len(unstruct_resp.splitlines()):<22}{len(struct_resp.splitlines()):<22}")
    print(f"{'Parseable':<28}{'No':<22}{'Yes (table)':<22}")
    print(f"{'Comparable across langs':<28}{'Hard (prose)':<22}{'Easy (columns)':<22}")

    # ---- Summary ----
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print("""
Findings:

1. UNSTRUCTURED OUTPUT
   - Reads naturally and gives context
   - Hard to compare facts across items (languages, products, etc.)
   - No fixed schema - every run may look different
   - Not machine-parseable without extra NLP work

2. STRUCTURED OUTPUT (Markdown Table)
   - Fixed columns force the model to compare on the same axes
   - Rows line up, making diffs and scans trivial
   - Output is parseable in a few lines of Python
   - Easier to check for completeness (all 3 languages, all 4 columns)
   - Renders nicely in GitHub README, VS Code, and most IDEs

3. PRACTICAL GUIDANCE
   - Use structured output when:
       * comparing multiple items on fixed attributes
       * feeding results into another program
       * presenting to stakeholders
   - Use unstructured output when:
       * narrative context matters more than comparison
       * the task is exploratory or open-ended
   - Always specify the exact schema (columns, order, format) for
     reliable structured responses
   - Show an example row - it's the strongest format anchor
""")
