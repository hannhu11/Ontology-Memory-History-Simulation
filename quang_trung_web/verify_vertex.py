from __future__ import annotations

import sys

from google import genai
from google.genai import types

from llm_provider import (
    configured_google_cloud_location,
    configured_google_cloud_project,
    configured_model,
)


def main() -> int:
    project = configured_google_cloud_project()
    location = configured_google_cloud_location()
    model = configured_model()
    if not project:
        print("GOOGLE_CLOUD_PROJECT is not configured.", file=sys.stderr)
        return 2

    client = genai.Client(vertexai=True, project=project, location=location)
    models = client.models.list()
    names = [item.name for item in models][:10]
    print(f"Vertex AI connection OK: project={project}, location={location}")
    print("Visible models:", names)

    response = client.models.generate_content(
        model=model,
        contents="Return exactly OK.",
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=64,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    text = (response.text or "").strip()
    if "OK" not in text:
        print(f"Vertex generate_content returned unexpected text: {text!r}", file=sys.stderr)
        return 3
    print(f"Vertex generate_content OK with model={model}: {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
