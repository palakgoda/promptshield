# Contributing to PromptShield

Thank you for your interest in contributing to PromptShield! This project is designed to be highly modular, enabling developers to build, test, and drop in custom AI firewall guardrails with minimal effort.

---

## 🏗️ Repository Structure

*   `src/main.py`: Core routing engine, dynamic provider router, and static assets server.
*   `src/database.py`: Local SQLite database manager for request audit logging.
*   `plugins/`: Folder containing drop-in security rules.
    *   `plugins/base.py`: The abstract base class `BasePlugin` which all security shields must subclass.
*   `dashboard/`: Static UI folder for the monitoring console.
*   `tests/`: Unit test suite running on `pytest`.

---

## 🔌 Creating a Custom Security Plugin

PromptShield uses dynamic module scanning. To add a custom guardrail, you only need to create a single Python file in the `plugins/` directory:

1.  Create a file under `plugins/your_plugin_name.py`.
2.  Inherit from `BasePlugin` and implement the `inspect` method.

### Code Blueprint
```python
from plugins.base import BasePlugin

class YourCustomPlugin(BasePlugin):
    def __init__(self):
        # The name parameter is displayed on the dashboard when triggered
        super().__init__(name="Your Custom Plugin Name")

    def inspect(self, prompt_text: str) -> dict:
        """
        Processes incoming prompts.
        - If unsafe, return safe=False and a descriptive block reason.
        - If safe, return safe=True and the original or mutated (redacted) prompt.
        """
        if "forbidden_word" in prompt_text.lower():
            return {
                "safe": False,
                "prompt": prompt_text,
                "reason": "Triggered custom word block list."
            }
            
        return {
            "safe": True,
            "prompt": prompt_text, # Can return mutated text (e.g. for redaction)
            "reason": ""
        }
```

Dynamic discovery will automatically load, sort, and execute your plugin on all incoming proxy payloads at runtime. No editing of `src/main.py` is needed!

---

## 🧪 Testing Guidelines

Before submitting a pull request, please make sure your changes do not break the existing test coverage.

### Run tests locally:
```bash
python -m pytest
```

Please add unit tests under `tests/test_engine.py` for any new plugins or features you implement.

---

## 🐋 Containerized Development

You can run PromptShield locally inside a docker container:

```bash
# Start container with live hot-reloads of your code and plugins folder
docker compose up --build
```
This mounts `./plugins` and `./data` as local volumes. Any changes to your local plugin files will be applied instantly without needing to rebuild the container.
