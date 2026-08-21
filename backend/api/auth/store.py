import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from .models import PublicUser, StoredUser

# email -> StoredUser
USERS: dict[str, StoredUser] = {}

# token -> email
SESSIONS: dict[str, str] = {}


def _norm_email(email: str) -> str:
    return email.strip().lower()


def register_user(name: str, email: str, password: str) -> tuple[PublicUser | None, str | None]:
    email = _norm_email(email)
    if not name or not email or not password:
        return None, "name, email, and password are required"
    if len(password) < 6:
        return None, "password must be at least 6 characters"
    if email in USERS:
        return None, "an account with that email already exists"
    USERS[email] = StoredUser(
        name=name.strip(), email=email, password_hash=generate_password_hash(password)
    )
    return USERS[email].public(), None


def login_user(email: str, password: str) -> tuple[PublicUser | None, str | None]:
    email = _norm_email(email)
    user = USERS.get(email)
    if not user or not check_password_hash(user.password_hash, password):
        return None, "invalid email or password"
    return user.public(), None


def issue_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = _norm_email(email)
    return token


def user_from_token(token: str | None) -> StoredUser | None:
    if not token:
        return None
    email = SESSIONS.get(token)
    if not email:
        return None
    return USERS.get(email)


def revoke_token(token: str) -> None:
    SESSIONS.pop(token, None)


def update_password(email: str, new_password: str) -> tuple[bool, str | None]:
    email = _norm_email(email)
    user = USERS.get(email)
    if not user:
        return False, "no account with that email"
    if len(new_password) < 6:
        return False, "new password must be at least 6 characters"
    user.password_hash = generate_password_hash(new_password)
    for t in [t for t, e in SESSIONS.items() if e == email]:
        SESSIONS.pop(t, None)
    return True, None


def seed_demo_users() -> None:
    demo = [("Ada Lovelace", "ada@example.com", "bookly123")]
    for name, email, password in demo:
        e = _norm_email(email)
        if e not in USERS:
            USERS[e] = StoredUser(
                name=name, email=e, password_hash=generate_password_hash(password)
            )
