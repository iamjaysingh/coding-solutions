#!/usr/bin/env python3
"""
Coding Solutions Generator
Generates programming problem solutions across multiple languages.
Commits solutions to build GitHub contributions.
Author: Jay Singh (iamjaysingh)
"""

import os
import sys
import json
import random
import datetime
import subprocess
import argparse
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOLUTIONS_DIR = os.path.join(SCRIPT_DIR, "solutions")
PROBLEMS_FILE = os.path.join(SCRIPT_DIR, "problems.json")
TRACKER_FILE = os.path.join(SCRIPT_DIR, "tracker.json")


def load_problems():
    with open(PROBLEMS_FILE, "r") as f:
        return json.load(f)


def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return {"solved": [], "total": 0, "by_language": {}, "by_difficulty": {}}


def save_tracker(tracker):
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


def get_ai_solution(language, problem_name, problem_desc, difficulty):
    """Use Gemini AI to generate a solution."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""Write a complete, working {language} program that solves this problem:

Problem: {problem_name}
Description: {problem_desc}
Difficulty: {difficulty}

Requirements:
- Write ONLY the code, no markdown fences or explanations
- Include a header comment with problem name and description
- Add inline comments explaining the logic
- Include a main function that demonstrates the solution with example inputs/outputs
- Make it between 30-80 lines
- Use clean, readable code style
- Include time complexity in a comment"""

        response = model.generate_content(prompt)
        code = response.text.strip()
        if code.startswith("```"):
            lines = code.split("\n")[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return code if len(code) > 20 else None
    except Exception as e:
        print(f"  ⚠️ AI error: {e}")
        return None


def pick_unsolved_problem(problems, tracker, language=None):
    """Pick a random unsolved problem, optionally filtered by language."""
    solved_keys = set(tracker.get("solved", []))
    available = []
    for prob in problems:
        for lang in prob["languages"]:
            key = f"{lang}/{prob['category']}/{prob['id']}"
            if key not in solved_keys:
                if language is None or lang == language:
                    available.append((prob, lang, key))
    if not available:
        # Reset if all solved
        tracker["solved"] = []
        save_tracker(tracker)
        return pick_unsolved_problem(problems, tracker, language)
    return random.choice(available)


def get_file_ext(lang):
    return {"python": ".py", "cpp": ".cpp", "c": ".c", "java": ".java",
            "javascript": ".js", "go": ".go", "rust": ".rs"}.get(lang, ".txt")


def get_fallback_solution(lang, problem):
    """Generate a template-based solution."""
    name = problem["name"]
    desc = problem["description"]
    cat = problem["category"]
    diff = problem["difficulty"]
    date = datetime.date.today().isoformat()

    headers = {
        "python": f'#!/usr/bin/env python3\n"""\n{name}\n{desc}\nCategory: {cat} | Difficulty: {diff}\nDate: {date} | Author: Jay Singh\n"""\n\n',
        "cpp": f'/*\n * {name}\n * {desc}\n * Category: {cat} | Difficulty: {diff}\n * Date: {date} | Author: Jay Singh\n */\n\n#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\n\n',
        "c": f'/*\n * {name}\n * {desc}\n * Category: {cat} | Difficulty: {diff}\n * Date: {date} | Author: Jay Singh\n */\n\n#include <stdio.h>\n#include <stdlib.h>\n\n',
        "java": f'/*\n * {name}\n * {desc}\n * Category: {cat} | Difficulty: {diff}\n * Date: {date} | Author: Jay Singh\n */\n\nimport java.util.*;\n\n',
        "javascript": f'/*\n * {name}\n * {desc}\n * Category: {cat} | Difficulty: {diff}\n * Date: {date} | Author: Jay Singh\n */\n\n',
        "go": f'/*\n * {name}\n * {desc}\n * Category: {cat} | Difficulty: {diff}\n * Date: {date} | Author: Jay Singh\n */\n\npackage main\n\nimport "fmt"\n\n',
    }

    # Use the embedded solution from problems.json if available
    if "solutions" in problem and lang in problem["solutions"]:
        return headers.get(lang, "") + problem["solutions"][lang]

    return headers.get(lang, "") + f"// TODO: Implement {name}\n"


def generate_solution(num_solutions=1, force_language=None):
    """Generate and save coding solutions."""
    problems = load_problems()
    tracker = load_tracker()
    today = datetime.date.today().isoformat()
    generated = []

    for i in range(num_solutions):
        prob, lang, key = pick_unsolved_problem(problems, tracker, force_language)
        print(f"\n  📝 Problem {i+1}: {prob['name']} ({lang}, {prob['difficulty']})")

        # Try AI first
        code = get_ai_solution(lang, prob["name"], prob["description"], prob["difficulty"])
        source = "AI"
        if not code:
            code = get_fallback_solution(lang, prob)
            source = "Template"

        # Save file
        lang_dir = os.path.join(SOLUTIONS_DIR, lang, prob["category"])
        os.makedirs(lang_dir, exist_ok=True)
        ext = get_file_ext(lang)
        filename = prob["id"] + ext
        filepath = os.path.join(lang_dir, filename)

        with open(filepath, "w") as f:
            f.write(code)

        print(f"  ✅ Saved: solutions/{lang}/{prob['category']}/{filename} ({source})")

        # Update tracker
        tracker["solved"].append(key)
        tracker["total"] += 1
        tracker["by_language"][lang] = tracker["by_language"].get(lang, 0) + 1
        tracker["by_difficulty"][prob["difficulty"]] = tracker["by_difficulty"].get(prob["difficulty"], 0) + 1
        generated.append({"problem": prob["name"], "lang": lang, "file": filepath, "key": key})

    save_tracker(tracker)
    update_readme(tracker)
    return generated


def update_readme(tracker):
    """Update the root README with stats."""
    today = datetime.date.today().isoformat()
    total = tracker.get("total", 0)

    readme = f"""# 💻 Coding Solutions

> Daily programming problem solutions across multiple languages
> By **Jay Singh** ([iamjaysingh](https://github.com/iamjaysingh))

## 📊 Stats

| Metric | Value |
|--------|-------|
| 📁 Total Solutions | **{total}** |
| 📅 Last Updated | **{today}** |

## 🗂️ Languages\n\n"""

    for lang, count in sorted(tracker.get("by_language", {}).items(), key=lambda x: x[1], reverse=True):
        emoji = {"python":"🐍","cpp":"⚡","c":"⚙️","java":"☕","javascript":"🟨","go":"🐹"}.get(lang, "💻")
        readme += f"| {emoji} {lang} | **{count}** solutions |\n"

    readme += f"""\n## 📈 By Difficulty\n\n"""
    for diff in ["Easy", "Medium", "Hard"]:
        count = tracker.get("by_difficulty", {}).get(diff, 0)
        emoji = {"Easy":"🟢","Medium":"🟡","Hard":"🔴"}.get(diff, "⚪")
        readme += f"| {emoji} {diff} | **{count}** |\n"

    readme += """\n## 📂 Structure

```
solutions/
├── python/
├── cpp/
├── c/
├── java/
├── javascript/
└── go/
    ├── basics/
    ├── math/
    ├── sorting/
    ├── searching/
    ├── data-structures/
    ├── strings/
    └── dynamic-programming/
```

---
*Auto-generated daily by [Coding Solutions Generator](https://github.com/iamjaysingh/coding-solutions)* ✨
"""

    with open(os.path.join(SCRIPT_DIR, "README.md"), "w") as f:
        f.write(readme)


def git_commit_push(generated):
    """Commit and push each solution separately for multiple contributions."""
    os.chdir(SCRIPT_DIR)
    subprocess.run(["git", "config", "user.name", "Jay Singh"], check=True)
    subprocess.run(["git", "config", "user.email", "jayrakeshsingh8796@gmail.com"], check=True)

    for item in generated:
        try:
            subprocess.run(["git", "add", "-A"], check=True)
            msg = f"✅ Solved: {item['problem']} ({item['lang']})"
            result = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  📦 Committed: {msg}")
            else:
                if "nothing to commit" not in (result.stdout + result.stderr):
                    print(f"  ⚠️ Commit issue: {result.stderr}")
        except Exception as e:
            print(f"  ❌ Git error: {e}")

    # Push all at once
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  🚀 Pushed to GitHub!")
    else:
        subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description="Coding Solutions Generator")
    parser.add_argument("--count", type=int, default=2, help="Number of solutions to generate")
    parser.add_argument("--language", type=str, help="Force specific language")
    parser.add_argument("--dry-run", action="store_true", help="Skip git operations")
    args = parser.parse_args()

    os.makedirs(SOLUTIONS_DIR, exist_ok=True)

    print("=" * 55)
    print("  💻 Coding Solutions Generator")
    print("=" * 55)

    generated = generate_solution(args.count, args.language)

    if not args.dry_run and generated:
        git_commit_push(generated)
        print(f"\n  🎉 Done! {len(generated)} solutions committed.")
    elif args.dry_run:
        print(f"\n  🏃 Dry run — {len(generated)} solutions generated.")


if __name__ == "__main__":
    main()
