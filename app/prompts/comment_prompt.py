"""
Language-aware prompt builder for the AI comment generator.

Each language gets a tailored system prompt and output rules so the LLM
produces the correct comment format with zero hallucination preamble.
"""

# ── Per-language format rules ─────────────────────────────────────────────────

_LANGUAGE_RULES: dict[str, dict] = {
    "python": {
        "format": "PEP 257 triple-double-quote docstring",
        "example": '"""\nSummary line.\n\nArgs:\n    x (int): Description.\n\nReturns:\n    int: Description.\n"""',
        "wrap_start": '"""',
        "wrap_end": '"""',
    },
    "javascript": {
        "format": "JSDoc block comment",
        "example": "/**\n * Summary line.\n *\n * @param {type} name - Description.\n * @returns {type} Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "typescript": {
        "format": "JSDoc block comment (TypeScript)",
        "example": "/**\n * Summary line.\n *\n * @param name - Description.\n * @returns Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "java": {
        "format": "Javadoc block comment",
        "example": "/**\n * Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "kotlin": {
        "format": "KDoc block comment",
        "example": "/**\n * Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "csharp": {
        "format": "C# XML documentation comment",
        "example": '/// <summary>\n/// Summary line.\n/// </summary>\n/// <param name="x">Description.</param>\n/// <returns>Description.</returns>',
        "wrap_start": "///",
        "wrap_end": "",
    },
    "cpp": {
        "format": "Doxygen block comment",
        "example": "/**\n * @brief Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "c": {
        "format": "Doxygen block comment",
        "example": "/**\n * @brief Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "go": {
        "format": "GoDoc comment (// lines directly above the declaration)",
        "example": "// FunctionName does X.\n// It accepts Y and returns Z.",
        "wrap_start": "//",
        "wrap_end": "",
    },
    "rust": {
        "format": "Rust doc comment (/// lines)",
        "example": "/// Summary line.\n///\n/// # Arguments\n///\n/// * `name` - Description.\n///\n/// # Returns\n///\n/// Description.",
        "wrap_start": "///",
        "wrap_end": "",
    },
    "php": {
        "format": "PHPDoc block comment",
        "example": "/**\n * Summary line.\n *\n * @param type $name Description.\n * @return type Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "ruby": {
        "format": "YARD documentation comment (# lines)",
        "example": "# Summary line.\n#\n# @param name [Type] Description.\n# @return [Type] Description.",
        "wrap_start": "#",
        "wrap_end": "",
    },
    "swift": {
        "format": "Swift Markup doc comment (/// lines)",
        "example": "/// Summary line.\n///\n/// - Parameters:\n///   - name: Description.\n/// - Returns: Description.",
        "wrap_start": "///",
        "wrap_end": "",
    },
    "sql": {
        "format": "SQL block comment",
        "example": "-- Summary: What this query does.\n-- Parameters: description of params/CTEs.",
        "wrap_start": "--",
        "wrap_end": "",
    },
    "html": {
        "format": "HTML comment",
        "example": "<!-- Summary: What this block renders. -->",
        "wrap_start": "<!--",
        "wrap_end": "-->",
    },
    "css": {
        "format": "CSS block comment",
        "example": "/**\n * Summary: What these styles do.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "scss": {
        "format": "SCSS block comment",
        "example": "/**\n * Summary: What these styles do.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "bash": {
        "format": "Shell script comment (# lines)",
        "example": "# Summary: What this script/function does.\n# Args: $1 - description, $2 - description.\n# Returns: exit code meaning.",
        "wrap_start": "#",
        "wrap_end": "",
    },
    "powershell": {
        "format": "PowerShell comment-based help",
        "example": "<#\n.SYNOPSIS\n    Summary line.\n.DESCRIPTION\n    Detailed description.\n.PARAMETER Name\n    Description.\n.OUTPUTS\n    Description.\n#>",
        "wrap_start": "<#",
        "wrap_end": "#>",
    },
    "dart": {
        "format": "Dart doc comment (/// lines)",
        "example": "/// Summary line.\n///\n/// [param] is the input.\n/// Returns description.",
        "wrap_start": "///",
        "wrap_end": "",
    },
    "scala": {
        "format": "Scaladoc block comment",
        "example": "/**\n  * Summary line.\n  *\n  * @param name Description.\n  * @return Description.\n  */",
        "wrap_start": "/**",
        "wrap_end": "  */",
    },
    "r": {
        "format": "Roxygen2 comment (# lines)",
        "example": "#' Summary line.\n#'\n#' @param name Description.\n#' @return Description.\n#' @examples\n#' functionName(x)",
        "wrap_start": "#'",
        "wrap_end": "",
    },
    "lua": {
        "format": "LuaDoc comment",
        "example": "--- Summary line.\n-- @param name description\n-- @return description",
        "wrap_start": "---",
        "wrap_end": "",
    },
    "perl": {
        "format": "POD inline comment block",
        "example": "# Summary: What this subroutine does.\n# Params: name - description.\n# Returns: description.",
        "wrap_start": "#",
        "wrap_end": "",
    },
    "elixir": {
        "format": "Elixir @doc module attribute",
        "example": '@doc """\nSummary line.\n\n## Parameters\n\n  - name: Description.\n\n## Returns\n\n  - Description.\n"""',
        "wrap_start": '@doc """',
        "wrap_end": '"""',
    },
    "haskell": {
        "format": "Haddock comment (-- | lines)",
        "example": "-- | Summary line.\n--\n-- Arguments:\n--\n--   * 'name' - Description.",
        "wrap_start": "-- |",
        "wrap_end": "",
    },
    "fsharp": {
        "format": "F# XML doc comment (/// lines)",
        "example": '/// <summary>\n/// Summary line.\n/// </summary>\n/// <param name="x">Description.</param>\n/// <returns>Description.</returns>',
        "wrap_start": "///",
        "wrap_end": "",
    },
    "julia": {
        "format": "Julia docstring (triple-double-quote)",
        "example": '"""\n    functionName(x)\n\nSummary line.\n\n# Arguments\n- `x`: Description.\n\n# Returns\n- Description.\n"""',
        "wrap_start": '"""',
        "wrap_end": '"""',
    },
    "objectivec": {
        "format": "HeaderDoc / Doxygen comment",
        "example": "/**\n * @brief Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
    "groovy": {
        "format": "Groovydoc block comment",
        "example": "/**\n * Summary line.\n *\n * @param name Description.\n * @return Description.\n */",
        "wrap_start": "/**",
        "wrap_end": " */",
    },
}

_DEFAULT_RULE = {
    "format": "standard line comment",
    "example": "// Summary: What this code does.\n// Params: name - description.\n// Returns: description.",
    "wrap_start": "//",
    "wrap_end": "",
}

# ── System prompt (role persona) ──────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a precise documentation comment generator.

ABSOLUTE RULES — follow without exception:
1. Output ONLY the raw comment — nothing else.
2. Do NOT write any sentence before or after the comment.
3. Do NOT say "Here is", "This code", "Sure!", "Certainly", "I'll generate", or anything similar.
4. Do NOT repeat or quote the code.
5. Do NOT use markdown fences (``` or ~~~).
6. Do NOT explain your reasoning.
7. Start your output with the very first character of the comment — no blank line before it.
8. Keep the comment concise but complete.
9. For functions/methods: document all parameters and return values.
10. For classes/structs: document the purpose and all public attributes.
"""

# ── User prompt template ──────────────────────────────────────────────────────

_USER_PROMPT_TEMPLATE = """\
Generate a {format} documentation comment for the following {language} code.

Required output format example:
{example}

Code to document:
{code}
"""


def build_prompt(code: str, language: str) -> tuple[str, str]:
    """
    Build system + user prompt pair for a given language.

    Args:
        code: The source code to document.
        language: The VS Code language identifier (e.g. 'python', 'go').

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    rule = _LANGUAGE_RULES.get(language.lower(), _DEFAULT_RULE)
    user_prompt = _USER_PROMPT_TEMPLATE.format(
        format=rule["format"],
        language=language,
        example=rule["example"],
        code=code,
    )
    return _SYSTEM_PROMPT, user_prompt


def get_language_rule(language: str) -> dict:
    """Return the format rule dict for a language, falling back to default."""
    return _LANGUAGE_RULES.get(language.lower(), _DEFAULT_RULE)
