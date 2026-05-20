import asyncio
import logging

from openai import AsyncOpenAI, APITimeoutError, APIConnectionError, RateLimitError
from config import (
    BASE_URL,
    API_KEY,
    MODEL_NAME,
    MAX_TOKEN,
    TEMPERATURE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
)
from app.prompts.comment_prompt import build_prompt, get_language_rule

logger = logging.getLogger(__name__)

# Use AsyncOpenAI so we never block the FastAPI event loop
client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    timeout=REQUEST_TIMEOUT,
)

# Phrases the LLM sometimes adds despite instructions — strip lines containing these
_BLOCKED_PHRASES = [
    "here is",
    "here's",
    "certainly",
    "sure!",
    "of course",
    "this code",
    "this function",
    "this class",
    "the docstring",
    "the comment",
    "i'll generate",
    "i will generate",
    "as requested",
    "explanation:",
    "reasoning:",
    "note:",
]


def _clean_response(raw: str, language: str) -> str:
    """
    Remove hallucinated preamble lines and stray markdown fences,
    then ensure the output is wrapped correctly for the target language.
    """
    # Strip markdown code fences
    cleaned_lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        # Skip markdown fences
        if stripped.startswith("```"):
            continue
        # Skip hallucinated preamble lines
        lower = stripped.lower()
        if any(phrase in lower for phrase in _BLOCKED_PHRASES):
            continue
        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines).strip()

    rule = get_language_rule(language)
    wrap_start = rule["wrap_start"]
    wrap_end = rule.get("wrap_end", "")

    # ── Language-specific fallback wrapping ───────────────────────────────────
    if language.lower() == "python":
        # Must be a valid triple-quoted docstring
        if not result.startswith('"""') and not result.startswith("'''"):
            result = f'"""\n{result}\n"""'

    elif language.lower() in ("csharp", "fsharp", "swift", "dart", "rust"):
        # Each line must start with ///
        if not any(ln.strip().startswith("///") for ln in result.splitlines()):
            result = "\n".join(f"/// {ln}" for ln in result.splitlines())

    elif language.lower() in ("go",):
        # GoDoc: each line starts with //
        if not any(ln.strip().startswith("//") for ln in result.splitlines()):
            result = "\n".join(f"// {ln}" for ln in result.splitlines())

    elif language.lower() == "powershell":
        if not result.startswith("<#"):
            result = f"<#\n{result}\n#>"

    elif wrap_start in ("/**", "/*"):
        # Block comment languages — ensure proper wrapping
        if not result.startswith(wrap_start):
            inner = "\n".join(f" * {ln}" for ln in result.splitlines())
            end = wrap_end if wrap_end else " */"
            result = f"{wrap_start}\n{inner}\n{end}"

    return result


async def generate_comment(
    code: str,
    language: str,
    comment_style: str,
    model: str,
    temperature: str,
    tokens: str,
) -> str:
    """
    Generate a documentation comment for the given code snippet.

    Uses AsyncOpenAI so the FastAPI event loop is never blocked.
    Retries up to MAX_RETRIES times on transient errors.

    Args:
        code: Source code to document.
        language: Language identifier (e.g. 'python', 'go').
        comment_style: Comment style hint from the extension (e.g. '//', '/**').

    Returns:
        A clean, correctly-formatted documentation comment string.

    Raises:
        RuntimeError: If all retry attempts fail.
    """
    system_prompt, user_prompt = build_prompt(code, language)

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 2):  # +2 = initial try + retries
        try:
            logger.debug("LLM call attempt %d for language=%s", attempt, language)

            model = model or MODEL_NAME

            temperature = temperature if temperature is not None else TEMPERATURE

            max_tokens = tokens if tokens is not None else MAX_TOKEN

            completion = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            raw = completion.choices[0].message.content or ""
            raw = raw.strip()

            if not raw:
                raise ValueError("LLM returned an empty response.")

            return _clean_response(raw, language)

        except (APITimeoutError, APIConnectionError) as exc:
            last_error = exc
            logger.warning(
                "LLM timeout/connection error on attempt %d: %s", attempt, exc
            )
            if attempt <= MAX_RETRIES:
                await asyncio.sleep(1.5 * attempt)  # back-off: 1.5s, 3s
            continue

        except RateLimitError as exc:
            last_error = exc
            logger.warning("Rate limited on attempt %d: %s", attempt, exc)
            if attempt <= MAX_RETRIES:
                await asyncio.sleep(3 * attempt)
            continue

        except Exception as exc:
            # Non-retryable — surface immediately
            logger.error("Unexpected LLM error: %s", exc)
            raise RuntimeError(f"LLM error: {exc}") from exc

    raise RuntimeError(
        f"LLM failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}"
    )
