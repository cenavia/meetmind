"""Tema Gradio MeetMind (spec 013): base Soft con acentos discretos."""

from __future__ import annotations

import gradio as gr


def meetmind_theme() -> gr.themes.Base:
    return gr.themes.Soft(primary_hue="blue", secondary_hue="slate")
