"""Pydantic schema for the on-disk config.toml. Bump CONFIG_VERSION on breaking changes."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

CONFIG_VERSION = 4


class RenderConfig(BaseModel):
    backend: Literal["local_diffusion", "remote_renderer", "stub"] = "stub"
    width: int = Field(default=1024, ge=256, le=4096)
    height: int = Field(default=1024, ge=256, le=4096)
    steps: int = Field(default=28, ge=8, le=150)
    cfg_scale: float = Field(default=6.5, ge=1.0, le=20.0)
    sampler: Literal["euler_a", "dpmpp_2m", "ddim"] = "dpmpp_2m"
    seed: int = -1
    weights_dir: Path = Path("weights")


class SheetConfig(BaseModel):
    poses: list[str] = Field(
        default_factory=lambda: ["front", "back", "left", "right", "three_quarter"]
    )
    include_expression_grid: bool = True
    include_color_palette: bool = True
    grid_columns: int = Field(default=5, ge=1, le=10)
    gutter_px: int = Field(default=24, ge=0, le=200)
    background_rgba: tuple[int, int, int, int] = (255, 255, 255, 255)


class AppConfig(BaseModel):
    version: int = CONFIG_VERSION
    output_dir: Path = Path("outputs")
    cache_dir: Path = Path(".cache/turnaround")
    render: RenderConfig = Field(default_factory=RenderConfig)
    sheet: SheetConfig = Field(default_factory=SheetConfig)
    remote_endpoint: str | None = None
    telemetry_enabled: bool = False

    @field_validator("remote_endpoint")
    @classmethod
    def _endpoint_shape(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("remote_endpoint must be http(s)")
        return v.rstrip("/")