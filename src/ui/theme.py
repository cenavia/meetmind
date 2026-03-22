"""Tema Gradio MeetMind (spec 013): Soft con superficies oscuras y texto legible."""

from __future__ import annotations

import gradio as gr


def meetmind_theme() -> gr.themes.Base:
    """
    Ajusta tokens del tema Soft para que bloques, inputs, archivo y acordeón
    no queden en blanco con texto gris (problema típico modo claro + CSS custom).
    """
    return gr.themes.Soft(primary_hue="blue", secondary_hue="slate").set(
        body_background_fill="#0b1220",
        body_background_fill_dark="#0b1220",
        body_text_color="#e8edff",
        body_text_color_dark="#e8edff",
        body_text_color_subdued="#aeb9d9",
        body_text_color_subdued_dark="#aeb9d9",
        block_background_fill="#131d33",
        block_background_fill_dark="#131d33",
        block_border_color="#2e3d63",
        block_border_color_dark="#2e3d63",
        block_label_background_fill="#1f3258",
        block_label_background_fill_dark="#1f3258",
        block_label_text_color="#f4f6ff",
        block_label_text_color_dark="#f4f6ff",
        block_label_border_color="#3d5a80",
        block_label_border_color_dark="#3d5a80",
        input_background_fill="#161f35",
        input_background_fill_dark="#161f35",
        input_background_fill_hover="#1a2742",
        input_background_fill_hover_dark="#1a2742",
        input_background_fill_focus="#1c2d4a",
        input_background_fill_focus_dark="#1c2d4a",
        input_border_color="#2e3d63",
        input_border_color_dark="#2e3d63",
        input_placeholder_color="#b4c5eb",
        input_placeholder_color_dark="#b4c5eb",
        border_color_primary="#2e3d63",
        border_color_primary_dark="#2e3d63",
        panel_background_fill="#131d33",
        panel_background_fill_dark="#131d33",
        panel_border_color="#2e3d63",
        panel_border_color_dark="#2e3d63",
        accordion_text_color="#e8edff",
        accordion_text_color_dark="#e8edff",
        button_primary_background_fill="#3d5eff",
        button_primary_background_fill_dark="#3d5eff",
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill="#243558",
        button_secondary_background_fill_dark="#243558",
        button_secondary_text_color="#e8edff",
        button_secondary_text_color_dark="#e8edff",
    )
