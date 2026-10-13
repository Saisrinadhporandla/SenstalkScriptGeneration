import json
import os

from bedrock_client import ask
from excel_reader import read_test_cases

BROWSER_NAME = "Chrome"
REFERENCE_PATH = "reference/helpers_sample.script"
OUTPUT_FOLDER = "generated"

RULES = """You write Eggplant Functional scripts in SenseTalk for Eggplant Functional {version}.

1. Reply with the contents of one .script file and nothing else. No explanations, no markdown, no code fences.
2. Write only SenseTalk. Never write Python, JavaScript or any other language.
3. Use only the commands and functions listed under ALLOWED NAMES, plus SenseTalk language words such as put, set, if, then, else, end if, repeat, end repeat, return, exit, to, handle, end.
4. Never use anything listed under DEPRECATED NAMES.
5. Do not call a handler unless you define it in your own script. Never give a handler the same name as a built-in command or function.
6. Write one block per step, starting with the comment: // Step N: <the step text>
7. Copy on-screen texts exactly as written in the step. Do not rephrase, correct or shorten them.
8. Find things on screen by text with text: searches. Use an image name only if the step names one.
9. Every verification step must call LogSuccess when the check passes and LogError when it fails, so a passed run really means the check passed.
10. Do not guess. Do not use index numbers, pixel positions or screen layout unless the step states them. If a step cannot be written exactly with the allowed names and the information in the step, write only this line for it: // NEEDS REVIEW: Step N: <short reason>
11. The style reference shows only how scripts look. Do not call its handlers and do not copy its mistakes, such as variables that are never defined."""

LAUNCH_PATTERN = """HOW TO OPEN A URL (taken from your working script):
TypeText windowsKey,"r"
Wait 2
TypeText "{browser} {url}"
TypeText return"""


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_vocabulary(path="vocabulary.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def build_prompt(test_case, vocabulary, reference_text):
    rules=RULES.format(version=vocabulary["docs_version"])
    allowed="ALLOWED NAMES\n"+", ".join(vocabulary["commands"]) + "\n" + ", ".join(vocabulary["functions"])
    deprecated = "DEPRECATED NAMES (never use)\n" + ", ".join(vocabulary["deprecated"])
    launch=LAUNCH_PATTERN.format(browser=BROWSER_NAME,url=test_case["url"])
    style = "STYLE REFERENCE ONLY\n" + reference_text

    lines = [
    "TEST CASE",
    "ID: " + str(test_case["id"]),
    "Name: " + str(test_case["name"]),
    "URL: " + str(test_case["url"]),
   ]
    for step in test_case["steps"]:
     lines.append(
        "Step " + str(step["number"]) + ": "
        + str(step["text"])
    )

    test_case_text = "\n".join(lines)

    parts=[rules,allowed,deprecated,launch,style,test_case_text, "Reply with the script file contents only."]
    return "\n\n".join(parts)

def generate_script(test_case, vocabulary):
      reference_text = read_text(REFERENCE_PATH)
      prompt = build_prompt(
      test_case, vocabulary, reference_text)
      return ask(prompt)

def save_script(test_case, script_text):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    path = os.path.join(
        OUTPUT_FOLDER,
        str(test_case["id"]) + ".script"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(script_text)
    return path

if __name__ == "__main__":
    vocabulary = load_vocabulary()

    test_cases = read_test_cases("./TestCases.xlsx")

    for test_case in test_cases:
        script_text = generate_script(test_case, vocabulary)
        saved_path = save_script(test_case, script_text)

        print("Script saved to:", saved_path)
        