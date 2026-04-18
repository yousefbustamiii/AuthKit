import base64
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

@dataclass
class AppConfig:
    name: str = "Authentication Testing"

@dataclass
class ArgonConfig:
    time_cost: int = 3
    memory_cost: int = 32768
    parallelism: int = 3
    hash_len: int = 32
    salt_len: int = 16

@dataclass
class SendgridConfig:
    api_key: str
    sender_email: str
    api_url: str = "https://api.sendgrid.com/v3/mail/send"

@dataclass
class OTPConfig:
    expire_minutes: int

@dataclass
class SessionConfig:
    expire_days: int

@dataclass
class GoogleConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url: str = "https://oauth2.googleapis.com/token"
    userinfo_url: str = "https://www.googleapis.com/oauth2/v3/userinfo"
    scopes: str = "openid email"

@dataclass
class GithubConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    auth_url: str = "https://github.com/login/oauth/authorize"
    token_url: str = "https://github.com/login/oauth/access_token"
    user_emails_url: str = "https://api.github.com/user/emails"
    user_url: str = "https://api.github.com/user"
    scopes: str = "read:user user:email"

@dataclass
class StripeConfig:
    secret_key: str
    webhook_secret: str
    price_id_plan_1: str
    price_id_plan_2: str
    price_id_plan_3: str
    success_url: str = "https://authkitclient.pages.dev/billing/success"
    cancel_url: str = "https://authkitclient.pages.dev/billing/cancel"

class Settings(BaseSettings):
    model_config = ConfigDict(ignored_types=(cached_property,), env_file=Path(__file__).resolve().parents[3] / ".env")

    # --- Loaded from .env ---
    AES_MASTER_KEY_B64: str
    BLAKE2S_HASHING_KEY_B64: str

    PSQL_URL: str
    REDIS_URL: str

    SENDGRID_API_KEY: str
    SENDGRID_SENDER_EMAIL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    # --- Hardcoded below, no .env needed ---

    @cached_property
    def geo_path(self) -> str:
        base_dir = Path(__file__).resolve().parents[3]
        return str(base_dir / "data" / "geoip.mmdb")

    @cached_property
    def cf_guard_enabled(self) -> bool:
        return False

    @cached_property
    def trusted_proxy_count(self) -> int:
        return 0

    @cached_property
    def app(self) -> AppConfig:
        return AppConfig(name="Authentication Testing")

    @cached_property
    def argon(self) -> ArgonConfig:
        return ArgonConfig()

    @cached_property
    def sendgrid(self) -> SendgridConfig:
        return SendgridConfig(
            api_key=self.SENDGRID_API_KEY,
            sender_email=self.SENDGRID_SENDER_EMAIL,
        )

    @cached_property
    def otp(self) -> OTPConfig:
        return OTPConfig(expire_minutes=10)

    @cached_property
    def session(self) -> SessionConfig:
        return SessionConfig(expire_days=60)

    @cached_property
    def aes_key(self) -> bytes:
        return base64.b64decode(self.AES_MASTER_KEY_B64)

    @cached_property
    def blake2s_hashing_key(self) -> bytes:
        return base64.b64decode(self.BLAKE2S_HASHING_KEY_B64)

    @cached_property
    def psql_dsn(self) -> str:
        return self.PSQL_URL

    @cached_property
    def redis_url(self) -> str:
        return self.REDIS_URL

    @cached_property
    def cors_allowed_origins(self) -> list[str]:
        return ["https://authkitclient.pages.dev"]

    @cached_property
    def google(self) -> GoogleConfig:
        return GoogleConfig(
            client_id=self.GOOGLE_CLIENT_ID,
            client_secret=self.GOOGLE_CLIENT_SECRET,
            redirect_uri=self.GOOGLE_REDIRECT_URI,
        )

    @cached_property
    def github(self) -> GithubConfig:
        return GithubConfig(
            client_id=self.GITHUB_CLIENT_ID,
            client_secret=self.GITHUB_CLIENT_SECRET,
            redirect_uri=self.GITHUB_REDIRECT_URI,
        )

    @cached_property
    def stripe(self) -> StripeConfig:
        return StripeConfig(
            secret_key=self.STRIPE_SECRET_KEY,
            webhook_secret=self.STRIPE_WEBHOOK_SECRET,
            price_id_plan_1="price_1TNVtvELlYFFgkEW2exX72vD",
            price_id_plan_2="price_1TNVu4ELlYFFgkEWuhYnLCV9",
            price_id_plan_3="price_1TNVuDELlYFFgkEWynQDASIM",
        )

settings = Settings()
