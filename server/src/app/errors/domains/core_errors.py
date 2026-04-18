from server.src.app.errors.base import AppError

class OrgNotFoundError(AppError):
    code = "ORG_NOT_FOUND"
    status_code = 404
    message = "Organization not found."

class InvalidOrgNameError(AppError):
    code = "INVALID_ORG_NAME"
    status_code = 400
    message = "The organization name is invalid."

    def __init__(self, detail: str = None):
        super().__init__()
        if detail:
            self.message = detail

class InvalidProjectNameError(AppError):
    code = "INVALID_PROJECT_NAME"
    status_code = 400
    message = "The project name is invalid."

    def __init__(self, detail: str = None):
        super().__init__()
        if detail:
            self.message = detail

class OrgAccessDeniedError(AppError):
    code = "ORG_ACCESS_DENIED"
    status_code = 403
    message = "You do not have permission to perform this action."

class OrgLastOwnedError(AppError):
    code = "ORG_LAST_OWNED"
    status_code = 409
    message = "You cannot delete your only owned organization."

class OrgOwnerCannotLeaveError(AppError):
    code = "ORG_OWNER_CANNOT_LEAVE"
    status_code = 403
    message = "Owners cannot leave their organization."

class PendingOrgDeletionNotFoundError(AppError):
    code = "PENDING_ORG_DELETION_NOT_FOUND"
    status_code = 404
    message = "No pending organization deletion found."

class OrgMemberNotFoundError(AppError):
    code = "ORG_MEMBER_NOT_FOUND"
    status_code = 404
    message = "The target user is not an active member of this organization."

class OrgRoleChangeSelfError(AppError):
    code = "ORG_ROLE_CHANGE_SELF"
    status_code = 400
    message = "You cannot change your own role."

class OrgRoleChangeNotAllowedError(AppError):
    code = "ORG_ROLE_CHANGE_NOT_ALLOWED"
    status_code = 409
    message = "This role change is not permitted."

class OrgInvalidInviteRoleError(AppError):
    code = "ORG_INVALID_INVITE_ROLE"
    status_code = 400
    message = "Invitation role must be either 'admin' or 'member'."

class OrgInviteAlreadyMemberError(AppError):
    code = "ORG_INVITE_ALREADY_MEMBER"
    status_code = 409
    message = "This user is already a member of the organization."

class OrgInvitationInvalidKeyError(AppError):
    code = "ORG_INVITATION_INVALID_KEY"
    status_code = 400
    message = "The invitation key format is invalid."

class OrgInvitationNotFoundError(AppError):
    code = "ORG_INVITATION_NOT_FOUND"
    status_code = 404
    message = "Invitation not found, expired, or does not belong to your account."

class OrgTransferToSelfError(AppError):
    code = "ORG_TRANSFER_TO_SELF"
    status_code = 400
    message = "You cannot transfer ownership to yourself."

class OrgTransferTargetNotFoundError(AppError):
    code = "ORG_TRANSFER_TARGET_NOT_FOUND"
    status_code = 404
    message = "The target user is not a member of this organization."

class OrgTransferNameMismatchError(AppError):
    code = "ORG_TRANSFER_NAME_MISMATCH"
    status_code = 409
    message = "The organization name you entered does not match."

class ProjectNotFoundError(AppError):
    code = "PROJECT_NOT_FOUND"
    status_code = 404
    message = "Project not found."

class ProjectNameMismatchError(AppError):
    code = "PROJECT_NAME_MISMATCH"
    status_code = 409
    message = "The project name you entered does not match."

class InvalidApiKeyNameError(AppError):
    code = "INVALID_API_KEY_NAME"
    status_code = 400
    message = "The API key name is invalid."

    def __init__(self, detail: str = None):
        super().__init__()
        if detail:
            self.message = detail

class ApiKeyNotFoundError(AppError):
    code = "API_KEY_NOT_FOUND"
    status_code = 404
    message = "API key not found."

class InvalidRotateConfirmationError(AppError):
    code = "INVALID_ROTATE_CONFIRMATION"
    status_code = 400
    message = "You must type ROTATE to confirm."

class InvalidRevokeConfirmationError(AppError):
    code = "INVALID_REVOKE_CONFIRMATION"
    status_code = 400
    message = "You must type REVOKE to confirm."
