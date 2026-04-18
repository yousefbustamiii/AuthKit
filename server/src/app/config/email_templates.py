from dataclasses import asdict, dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from server.src.app.config.settings import settings

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR.parent / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"])
)

class BaseTemplate:
    template_file: str  # Requirement for subclasses

    def render(self) -> str:
        template = jinja_env.get_template(self.template_file)
        
        context = asdict(self)
        context.update({
            "app_name": settings.app.name,
            "otp_expire_minutes": settings.otp.expire_minutes
        })
        
        return template.render(**context)

    @property
    def html(self) -> str:
        return self.render()

@dataclass
class SignupTemplate(BaseTemplate):
    otp: str
    device: str
    country: str
    timestamp: str
    template_file = "signup.html"

    @property
    def subject(self) -> str:
        return f"Welcome to {settings.app.name} - Verify Your Email"

@dataclass
class LoginTemplate(BaseTemplate):
    otp: str
    device: str
    country: str
    timestamp: str
    template_file = "login.html"

    @property
    def subject(self) -> str:
        return f"Login into your {settings.app.name} account"

@dataclass
class EmailChangeTemplate(BaseTemplate):
    otp: str
    new_email: str
    device: str
    country: str
    timestamp: str
    template_file = "email_change.html"

    @property
    def subject(self) -> str:
        return f"Change your {settings.app.name} email"

@dataclass
class PasswordResetTemplate(BaseTemplate):
    otp: str
    device: str
    country: str
    timestamp: str
    template_file = "password_reset.html"

    @property
    def subject(self) -> str:
        return f"Password Reset for your {settings.app.name} account"

@dataclass
class DeletionTemplate(BaseTemplate):
    otp: str
    device: str
    country: str
    timestamp: str
    template_file = "deletion.html"

    @property
    def subject(self) -> str:
        return f"{settings.app.name} Account Deletion"

@dataclass
class PasswordChangeSuccessTemplate(BaseTemplate):
    device: str
    country: str
    timestamp: str
    template_file = "password_change_success.html"

    @property
    def subject(self) -> str:
        return f"Your {settings.app.name} password has been changed"

@dataclass
class PasswordResetSuccessTemplate(BaseTemplate):
    device: str
    country: str
    timestamp: str
    template_file = "password_reset_success.html"

    @property
    def subject(self) -> str:
        return f"Your {settings.app.name} password has been reset"

@dataclass
class EmailChangeSuccessTemplate(BaseTemplate):
    device: str
    country: str
    timestamp: str
    template_file = "email_change_success.html"

    @property
    def subject(self) -> str:
        return f"Your {settings.app.name} email has been updated"

@dataclass
class AccountDeletionSuccessTemplate(BaseTemplate):
    device: str
    country: str
    timestamp: str
    template_file = "deletion_success.html"

    @property
    def subject(self) -> str:
        return f"Your {settings.app.name} account has been deleted"

@dataclass
class NewLoginTemplate(BaseTemplate):
    device: str
    country: str
    timestamp: str
    template_file = "new_login.html"

    @property
    def subject(self) -> str:
        return f"New login detected on your {settings.app.name} account"

@dataclass
class OAuthWelcomeTemplate(BaseTemplate):
    provider: str
    device: str
    country: str
    timestamp: str
    template_file = "oauth_welcome.html"

    @property
    def subject(self) -> str:
        return f"Welcome to {settings.app.name} — signed in via {self.provider}"

@dataclass
class OrgDeletionTemplate(BaseTemplate):
    otp: str
    device: str
    country: str
    timestamp: str
    template_file = "core/organization_deletion.html"

    @property
    def subject(self) -> str:
        return f"{settings.app.name} Organization Deletion"

@dataclass
class OrgInvitationTemplate(BaseTemplate):
    token: str
    org_name: str
    role: str
    template_file = "core/organization_invitation.html"

    @property
    def subject(self) -> str:
        return f"You've been invited to join {self.org_name} on {settings.app.name}"

@dataclass
class BillingUpgradeTemplate(BaseTemplate):
    org_name: str
    old_plan: str
    new_plan: str
    timestamp: str
    template_file = "core/billing/billing_upgrade.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} plan upgraded to {self.new_plan} on {settings.app.name}"

@dataclass
class BillingCancelTemplate(BaseTemplate):
    org_name: str
    plan: str
    period_end: str
    timestamp: str
    template_file = "core/billing/billing_cancel.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} subscription cancellation scheduled on {settings.app.name}"

@dataclass
class BillingSubscriptionStartedTemplate(BaseTemplate):
    org_name: str
    plan: str
    next_billing_date: str
    timestamp: str
    template_file = "core/billing/billing_subscription_started.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} subscription activated on {settings.app.name}"

@dataclass
class BillingPaymentReceivedTemplate(BaseTemplate):
    org_name: str
    amount: str
    currency: str
    invoice_url: str
    timestamp: str
    template_file = "core/billing/billing_payment_received.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"Payment received for {self.org_name} on {settings.app.name}"

@dataclass
class BillingPaymentFailedTemplate(BaseTemplate):
    org_name: str
    amount: str
    currency: str
    invoice_url: str
    timestamp: str
    template_file = "core/billing/billing_payment_failed.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"Payment failed for {self.org_name} on {settings.app.name} — action required"

@dataclass
class BillingPaymentActionRequiredTemplate(BaseTemplate):
    org_name: str
    amount: str
    currency: str
    invoice_url: str
    timestamp: str
    template_file = "core/billing/billing_payment_action_required.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"Authentication required to complete payment for {self.org_name} on {settings.app.name}"

@dataclass
class BillingSubscriptionEndedTemplate(BaseTemplate):
    org_name: str
    plan: str
    timestamp: str
    template_file = "core/billing/billing_subscription_ended.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} subscription has ended on {settings.app.name}"

@dataclass
class BillingTrialEndingTemplate(BaseTemplate):
    org_name: str
    plan: str
    trial_end_date: str
    timestamp: str
    template_file = "core/billing/billing_trial_ending.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} trial ending soon on {settings.app.name}"

@dataclass
class BillingSubscriptionPausedTemplate(BaseTemplate):
    org_name: str
    plan: str
    timestamp: str
    template_file = "core/billing/billing_subscription_paused.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} subscription has been paused on {settings.app.name}"

@dataclass
class BillingSubscriptionResumedTemplate(BaseTemplate):
    org_name: str
    plan: str
    timestamp: str
    template_file = "core/billing/billing_subscription_resumed.html"

    @property
    def device(self) -> str:
        return f"{settings.app.name} Billing"

    @property
    def subject(self) -> str:
        return f"{self.org_name} subscription has been resumed on {settings.app.name}"


class DummyTemplate(BaseTemplate):
    template_file = "dummy.html"
    @property
    def html(self) -> str:
        return "<html><body>Dummy</body></html>"
