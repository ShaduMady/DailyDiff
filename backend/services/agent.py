import json
import ollama

MODEL = "llama3.2"


def _chat(system: str, user: str) -> str:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        format="json",
    )
    try:
        text = response.message.content
    except AttributeError:
        text = response["message"]["content"]
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def structure_entry_stream(raw_text: str, weekly_focus: str, last_entries: list[dict]):
    system = (
        "You are a personal note structuring assistant.\n"
        "The user gives you a messy brain dump from their day — notes, thoughts, tasks, ideas, anything.\n"
        "Your job is to turn it into a clean, structured changelog entry.\n"
        "Return ONLY valid JSON. No markdown, no explanation, no code fences."
    )
    user = f"""Weekly focus: {weekly_focus}

Today's raw notes:
{raw_text}

Previous entries for context:
{json.dumps(last_entries, default=str)}

Return this exact JSON structure:
{{
  "summary": "one clear sentence summarizing the day",
  "tags": ["learning"|"building"|"social"|"health"|"blocked"|"thinking"],
  "changelog": ["specific thing that happened or was learned"],
  "key_ideas": ["any interesting idea or insight worth keeping"],
  "open_questions": ["anything unresolved or worth thinking about"],
  "action_items": ["concrete next step if any"],
  "drift_score": 0-100,
  "connections": ["v0.0.X: one sentence explaining the link"] or []
}}"""

    full_text = ""
    for chunk in ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        stream=True,
        format="json",
    ):
        try:
            token = chunk.message.content
        except AttributeError:
            token = chunk["message"]["content"]
        if token:
            full_text += token
            yield token, None

    result = json.loads(full_text)
    yield None, result


def structure_entry(raw_text: str, weekly_focus: str, last_entries: list[dict]) -> dict:
    system = (
        "You are a personal note structuring assistant.\n"
        "The user gives you a messy brain dump from their day — notes, thoughts, tasks, ideas, anything.\n"
        "Your job is to turn it into a clean, structured changelog entry.\n"
        "Return ONLY valid JSON. No markdown, no explanation, no code fences."
    )

    user = f"""Weekly focus: {weekly_focus}

Today's raw notes:
{raw_text}

Previous entries for context:
{json.dumps(last_entries, default=str)}

Return this exact JSON structure:
{{
  "summary": "one clear sentence summarizing the day",
  "tags": ["learning"|"building"|"social"|"health"|"blocked"|"thinking"],
  "changelog": ["specific thing that happened or was learned"],
  "key_ideas": ["any interesting idea or insight worth keeping"],
  "open_questions": ["anything unresolved or worth thinking about"],
  "action_items": ["concrete next step if any"],
  "drift_score": 0-100,
  "connections": ["v0.0.X: one sentence explaining the link"] or []
}}"""

    text = _chat(system, user)
    return json.loads(text)


def generate_weekly_summary(entries: list[dict]) -> dict:
    system = (
        "You are a personal growth analyst.\n"
        "Given a set of daily entries from this week, write a weekly release note.\n"
        "Return ONLY valid JSON."
    )

    user = f"""Entries this week:
{json.dumps(entries, default=str)}

Return:
{{
  "week_version": "v{{week_number}}.0",
  "summary": "one sentence describing the week",
  "highlights": ["top 3 things that went well"],
  "blockers": ["recurring challenges or stuck points"],
  "pattern": "one insight about how this week went"
}}"""

    text = _chat(system, user)
    return json.loads(text)
