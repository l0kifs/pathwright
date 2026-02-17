from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuration settings.
    """
    model_config = SettingsConfigDict(
        env_prefix="PATHWRIGHT__",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="pathwright", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")

    # Access control settings
    path_whitelist: list[str] = Field(
        default_factory=list,
        description="Allowed path patterns. Empty list means all paths are allowed unless blacklisted.",
    )
    path_blacklist: list[str] = Field(
        default_factory=list,
        description="Denied path patterns. Evaluated before whitelist.",
    )


def get_settings() -> Settings:
    """
    Get configuration settings.
    """
    return Settings()
