# Prompt Engineering Lab - Experiment 8

## Structured vs Unstructured Output

Demonstrates how asking for a specific format (markdown table)
produces clearer, more comparable, and machine-parseable output than
free-text prose for the same information.

## Task

Describe three programming languages (Python, Java, C++) in two ways:

| Variant | Prompt Style |
|---------|--------------|
| Unstructured | "Describe Python, Java, and C++ in a short paragraph." |
| Structured | "Create a markdown table with columns: Language, Typing, Primary Use Case, Difficulty." |

## Model and Parameters

- Model: openai/gpt-oss-20b
- Temperature: 0.2 (low, to reduce formatting drift)
- Max tokens: 600

## Setup

Reuse the environment from Experiment 1:

    Copy-Item ..\EXP_1\.env .
    python -m pip install -r requirements.txt

## Run

    python structured_output.py

## Expected Output

- Unstructured response (prose paragraph)
- Structured response (markdown table)
- A table parser that extracts rows and verifies expected languages
- A comparison block (chars, words, lines, parseability)

## Key Findings

1. **Unstructured is natural but hard to compare** - each fact about
   each language sits in flowing prose. Fine for reading; awkward for
   comparing across items.

2. **Structured is compact and machine-readable** - fixed columns
   force the model to compare on the same axes. Rows line up.
   Parseable with a few lines of Python.

3. **What makes structured prompts work:**
   - Explicit column names
   - Explicit row set (one per language)
   - A concrete example of the format
   - Low temperature to reduce formatting variance
   - "Return ONLY the table" to suppress prose wrapping

## When to Use Which

| Goal | Recommendation |
|------|----------------|
| Compare items on fixed attributes | Structured |
| Feed results into another program | Structured |
| Present to stakeholders | Structured |
| Explore a topic narratively | Unstructured |
| Provide rich context for a single item | Unstructured |

## Security

- Never commit .env
- Never paste API keys in chat, logs, or screenshots

## License

For educational / lab use only.
