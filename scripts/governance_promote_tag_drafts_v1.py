#!/usr/bin/env python3
"""DEPRECATED alias — use governance_promote_intake_drafts_v1 (evidence sink, not Tag name)."""
from __future__ import annotations

from governance_promote_intake_drafts_v1 import (  # noqa: F401
    build_intake_manifest,
    promote_intake_manifest,
)

# Backward-compat names
build_tag_manifest = build_intake_manifest
promote_tag_manifest = promote_intake_manifest
