from server.src.app.errors.base import AppError

class InvalidPlanNumberError(AppError):
    code = "INVALID_PLAN_NUMBER"
    status_code = 400
    message = "Plan number must be 1, 2, or 3."


class ActiveSubscriptionNotFoundError(AppError):
    code = "ACTIVE_SUBSCRIPTION_NOT_FOUND"
    status_code = 404
    message = "No active subscription found for this organization."


class SubscriptionAlreadyActiveError(AppError):
    code = "SUBSCRIPTION_ALREADY_ACTIVE"
    status_code = 409
    message = "This organization already has an active subscription."


class SamePlanError(AppError):
    code = "SAME_PLAN"
    status_code = 400
    message = "The organization is already on this plan."


class SubscriptionDowngradeNotAllowedError(AppError):
    code = "SUBSCRIPTION_DOWNGRADE_NOT_ALLOWED"
    status_code = 400
    message = "Downgrading to a lower plan is not allowed. Please contact support."


class SubscriptionAlreadyScheduledForCancellationError(AppError):
    code = "SUBSCRIPTION_ALREADY_SCHEDULED_FOR_CANCELLATION"
    status_code = 409
    message = "This subscription is already scheduled to cancel at the end of the current billing period."
