import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    GODADDY_API_KEY: str
    GODADDY_API_SECRET: str
    GODADDY_BASE_URL: str = "https://api.ote-godaddy.com"  # Default to Test env

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            GODADDY_API_KEY=os.getenv("GODADDY_API_KEY", ""),
            GODADDY_API_SECRET=os.getenv("GODADDY_API_SECRET", ""),
            GODADDY_BASE_URL=os.getenv(
                "GODADDY_BASE_URL", "https://api.ote-godaddy.com"
            ),
        )
