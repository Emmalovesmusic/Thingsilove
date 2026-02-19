#!/usr/bin/env python3
"""Generate multilingual versions of an article using local Ollama.

- Reads a source markdown file.
- For each language, asks Ollama to rewrite naturally in that language.
- Preserves frontmatter keys; sets language.

Requires:
- ollama serve running
- model llama3.2:3b installed
"""

import json
import os
from pathlib import Path
import urllib.request

MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")

LANGS = {
    "es": "Spanish (LATAM neutral)",
    "pt": "Portuguese (Brazil)",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "id": "Indonesian",
    "hi": "Hindi",
    "ar": "Arabic (MSA)",
    "ja": "Japanese",
    "ko": "Korean",
}


def ollama_generate(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "").strip()


def main():
    repo = Path("/data/.openclaw/workspace/Thingsilove")
    src = repo / "articles" / "2026-02-18-zhot-30b-views.md"
    text = src.read_text(encoding="utf-8")

    out_root = repo / "articles" / "i18n"
    out_root.mkdir(parents=True, exist_ok=True)

    for code, label in LANGS.items():
        out_dir = out_root / code
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / src.name

        prompt = f"""Rewrite the following markdown article into {label}.

Requirements:
- Keep markdown formatting.
- Keep links EXACTLY as-is.
- Keep the tone positive, confident, not begging.
- Keep it concise.
- Preserve the YAML frontmatter block, but set language: \"{code}\".

ARTICLE:\n{text}
"""
        translated = ollama_generate(prompt)
        # Basic sanity: ensure links survived; if not, fall back to original links appended.
        if "https://open.spotify.com/track/3xaJXivKuXLH7k3mVgDICG" not in translated:
            translated += "\n\n- Rise & Repeat: https://open.spotify.com/track/3xaJXivKuXLH7k3mVgDICG"
        if "https://open.spotify.com/album/7IqE4kinxFSYvWPAlzjrLw" not in translated:
            translated += "\n- Perspective: https://open.spotify.com/album/7IqE4kinxFSYvWPAlzjrLw"
        if "https://ffm.bio/zhot" not in translated:
            translated += "\n- https://ffm.bio/zhot"

        out_path.write_text(translated + "\n", encoding="utf-8")
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
