"""This file contains the prompts for the agent."""

from datetime import datetime
from pathlib import Path

from loguru import logger


def load_system_prompt() -> str:
    """Load and format the system prompt from a markdown file."""
    prompt_path = Path(__file__).parent / "system.md"

    if not prompt_path.exists():
        logger.critical(f"Missing required system prompt file: {prompt_path}")
        raise FileNotFoundError(f"Required system prompt file not found: {prompt_path}")

    try:
        raw_prompt = prompt_path.read_text(encoding="utf-8")
        return raw_prompt.format(
            current_date_and_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    except Exception:
        logger.critical("Failed to load or format the system prompt.", exc_info=True)
        raise


SYSTEM_PROMPT = load_system_prompt()
