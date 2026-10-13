"""Compose per-pose prompts from a CharacterSpec.

The turnaround format is a known industry convention: consistent scale,
neutral lighting, T-pose-ish stance, orthographic-ish camera. We bake those
into every pose prompt so the backend produces comparable frames.
"""
from __future__ import annotations

from models.character import CharacterSpec

# Fixed suffix shared by every pose — keeps scale and lighting comparable.
_STYLE_SUFFIX = (
    "full body, character turnaround sheet, neutral studio lighting, "
    "flat grey background, orthographic camera, consistent scale, "
    "clean lineart, high detail, no dynamic pose"
)

_POSE_CAMERA = {
    "front": "facing camera, arms slightly away from body",
    "back": "back to camera, facing away",
    "left": "left profile, facing left",
    "right": "right profile, facing right",
    "three_quarter": "three-quarter view, turned 45 degrees",
}


def build_pose_prompt(spec: CharacterSpec, pose: str) -> str:
    """Build the full prompt string for a single pose of a character.

    Args:
        spec: The character spec (name, description, features).
        pose: One of the keys in `_POSE_CAMERA`. Unknown poses fall back to
            a generic "neutral pose" hint.

    Returns:
        A single-line prompt string ready for the backend.
    """
    camera = _POSE_CAMERA.get(pose, "neutral pose")
    pieces = [spec.description.strip()]

    if spec.features:
        pieces.append(", ".join(sorted(spec.features)))

    pieces.append(camera)
    pieces.append(_STYLE_SUFFIX)
    return ", ".join(p for p in pieces if p)