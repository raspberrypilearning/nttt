"""
Loads and exposes the marker registry (``markers.yml``).

This is the single source of truth for the structural markers used in both the
legacy (kramdown-rpf) and the Raspberry Flavoured Markdown (RFM) syntaxes. Other
modules ask this module *what* the markers are; the actual list lives in the data
file so it can be edited without touching Python.
"""
import os
import re
import ruamel.yaml


_MARKERS_FILE = os.path.join(os.path.dirname(__file__), "markers.yml")
_registry_cache = None

# Matches an RFM alert token such as "[!TASK]" and captures the keyword.
_ALERT_TOKEN_RE = re.compile(r"\[!\s*([^\]\s][^\]]*?)\s*\]")


def load_markers(markers_file=_MARKERS_FILE):
    """Returns the parsed marker registry as a dict, caching the default file."""
    global _registry_cache

    if markers_file == _MARKERS_FILE and _registry_cache is not None:
        return _registry_cache

    yaml_parser = ruamel.yaml.YAML(typ="safe")
    with open(markers_file, encoding="utf-8") as f:
        registry = yaml_parser.load(f) or {}

    registry.setdefault("markers", [])
    registry.setdefault("raw_patterns", [])

    if markers_file == _MARKERS_FILE:
        _registry_cache = registry
    return registry


def _markers(registry=None):
    return (registry or load_markers()).get("markers", [])


def hideable_strings(registry=None):
    """
    Returns the list of literal strings to hide from translators (both syntaxes
    plus raw patterns). Each is matched as a substring against Crowdin source
    text. Order is preserved and duplicates removed.
    """
    registry = registry or load_markers()
    strings = []

    for marker in _markers(registry):
        if not marker.get("hide", False):
            continue
        legacy = marker.get("legacy") or {}
        rfm = marker.get("rfm") or {}
        for value in (legacy.get("open"), legacy.get("close"), rfm.get("alert")):
            if value:
                strings.append(value)

    strings.extend(registry.get("raw_patterns", []))

    # de-duplicate, preserving order
    seen = set()
    unique = []
    for s in strings:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def alert_keywords(registry=None):
    """Returns the set of canonical English RFM alert keywords (e.g. {"TASK", "HINT"})."""
    keywords = set()
    for marker in _markers(registry):
        rfm = marker.get("rfm") or {}
        alert = rfm.get("alert")
        if alert:
            match = _ALERT_TOKEN_RE.search(alert)
            if match:
                keywords.add(match.group(1).strip().upper())
    return keywords


def legacy_tag_names(registry=None):
    """
    Returns the set of known legacy section tag names (e.g. {"task", "hint"}),
    derived from the registry's legacy open markers ("--- task ---" -> "task").
    """
    names = set()
    for marker in _markers(registry):
        legacy = marker.get("legacy") or {}
        opener = legacy.get("open", "")
        stripped = opener.strip().strip("-").strip()
        if stripped:
            names.add(stripped)
    return names
