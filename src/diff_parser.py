"""Parse and diff resume/cover letter texts for the approve/reject UI.

The LLM wraps changed items in <modified>...</modified> tags.
This module parses texts into structured items, detects which ones
changed, and applies the user's approve/reject choices to build
the final text.
"""

import re

MODIFIED_RE = re.compile(r"<modified>(.*?)</modified>", re.DOTALL)


def parse_into_items(text, mode="bullets"):
    """Parse a text into a list of logical items.

    For resumes (mode='bullets'): splits on bullet markers (·, -, •, *).
    For cover letters (mode='paragraphs'): splits on double newlines.

    Args:
        text: The full text to parse.
        mode: 'bullets' or 'paragraphs'.

    Returns:
        List of item strings (with leading whitespace/bullet markers stripped
        for bullets to make comparison easier).
    """
    if not text:
        return []

    if mode == "bullets":
        # Split on common bullet markers while keeping the marker
        lines = text.split("\n")
        items = []
        current = []
        for line in lines:
            stripped = line.strip()
            # Check if this line starts a new bullet point
            if stripped and stripped[0] in ("·", "-", "•", "*", ">"):
                if current:
                    items.append("\n".join(current))
                current = [line]
            else:
                if current or stripped:  # skip leading empty lines
                    current.append(line)
        if current:
            items.append("\n".join(current))

        # If no bullets found, fall back to line-by-line
        if not items:
            items = [l for l in lines if l.strip()]
        return items

    elif mode == "paragraphs":
        # Split on double newlines; keep single-newline paragraphs together
        items = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return items

    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'bullets' or 'paragraphs'.")


def diff_items(original_items, enhanced_items):
    """Compare original and enhanced item lists, marking which items changed.

    Items are aligned by position (index). The LLM is instructed to preserve
    the count and order of items.

    Args:
        original_items: List of item strings from the original text.
        enhanced_items: List of item strings from the enhanced text
                        (with <modified> tags still present).

    Returns:
        List of dicts: {index, old_text, new_text, changed: bool}
        new_text has <modified> tags stripped for display.
    """
    results = []
    max_len = max(len(original_items), len(enhanced_items))

    for i in range(max_len):
        old = original_items[i] if i < len(original_items) else ""
        new_raw = enhanced_items[i] if i < len(enhanced_items) else ""

        # Strip <modified> tags for the display text
        new_clean = MODIFIED_RE.sub(r"\1", new_raw)

        changed = (old.strip() != new_clean.strip())

        results.append({
            "index": i,
            "old_text": old,
            "new_text": new_clean,
            "changed": changed,
        })

    return results


def apply_approvals(original_items, enhanced_items, approvals):
    """Build the final text by applying the user's approve/reject choices.

    Args:
        original_items: List of item strings from the original text.
        enhanced_items: List of item strings from the enhanced text
                        (may contain <modified> tags).
        approvals: List of bools, same length as items.
                   True = keep the enhanced version (approved).
                   False = revert to original (rejected).

    Returns:
        Final text string with approved changes applied and <modified> tags removed.
    """
    result_items = []
    for i in range(len(enhanced_items)):
        if i < len(approvals) and approvals[i]:
            # Approved: use enhanced, strip <modified> tags
            result_items.append(MODIFIED_RE.sub(r"\1", enhanced_items[i]))
        else:
            # Rejected: use original
            if i < len(original_items):
                result_items.append(original_items[i])

    # Join items back — use double newline for paragraphs, single newline for bullets
    return "\n".join(result_items)


def extract_change_summary(original_text, enhanced_text, mode="bullets"):
    """Convenience function: parse, diff, and return structured change data.

    Args:
        original_text: The original resume/cover-letter text.
        enhanced_text: The LLM-enhanced text with <modified> tags.
        mode: 'bullets' for resume, 'paragraphs' for cover letter.

    Returns:
        Tuple of (original_items, diffs) where diffs is the list from diff_items().
    """
    original_items = parse_into_items(original_text, mode=mode)
    enhanced_items = parse_into_items(enhanced_text, mode=mode)
    diffs = diff_items(original_items, enhanced_items)
    return original_items, enhanced_items, diffs
