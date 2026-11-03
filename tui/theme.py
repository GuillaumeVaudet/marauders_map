from textual.theme import Theme

# Palette : change les couleurs ici, styles.tcss n'utilise que ces variables.
NIGHT_CIRCUIT = Theme(
    name="night-circuit",
    primary="#ff5c57",      # structure : cadres, titres, en-têtes
    secondary="#3fe0e8",    # interaction : sélection, focus, données
    accent="#fcee0a",       # logo uniquement
    error="#ff2e88",        # actions destructrices
    warning="#ffb454",
    success="#3fe0a0",
    foreground="#e9ded8",
    background="#07090e",
    surface="#0d1118",
    panel="#161c26",
    dark=True,
    variables={
        "footer-background": "#0d1118",
        "footer-foreground": "#e9ded8",
        "footer-item-background": "#0d1118",
        "footer-key-foreground": "#07090e",
        "footer-key-background": "#ff5c57",
        "footer-description-foreground": "#e9ded8",
        "footer-description-background": "#0d1118",
        "input-cursor-background": "#3fe0e8",
        "input-cursor-foreground": "#07090e",
        "input-selection-background": "#3fe0e8 30%",
        "scrollbar": "#7a3532",
        "scrollbar-hover": "#ff5c57",
        "scrollbar-active": "#3fe0e8",
        "scrollbar-background": "#0d1118",
        "scrollbar-background-hover": "#0d1118",
        "scrollbar-background-active": "#0d1118",
        "scrollbar-corner-color": "#0d1118",
    },
)
