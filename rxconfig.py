import reflex as rx

class CodereflexConfig(rx.Config):
    pass

config = CodereflexConfig(
    app_name="code_REFLEX",
    db_url="sqlite:///reflex.db",
)