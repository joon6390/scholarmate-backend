from django.conf import settings
from django.core.mail import EmailMessage, get_connection, send_mail


class EmailDeliveryError(Exception):
    pass


def _mask(value):
    if not value:
        return ""
    if "@" in value:
        name, domain = value.split("@", 1)
        return f"{name[:2]}***@{domain}"
    return f"{value[:2]}***"


def _naver_usernames(username):
    usernames = [username]
    if username.endswith("@naver.com"):
        usernames.append(username.split("@", 1)[0])
    return list(dict.fromkeys(usernames))


def _smtp_attempts():
    host = settings.EMAIL_HOST
    port = int(settings.EMAIL_PORT)
    use_ssl = bool(settings.EMAIL_USE_SSL)
    use_tls = bool(settings.EMAIL_USE_TLS)
    usernames = [settings.EMAIL_HOST_USER]

    if host.lower() == "smtp.naver.com":
        usernames = _naver_usernames(settings.EMAIL_HOST_USER)
        candidates = [(port, use_ssl, use_tls), (465, True, False), (587, False, True)]
    else:
        candidates = [(port, use_ssl, use_tls)]

    attempts = []
    seen = set()
    for candidate_port, candidate_ssl, candidate_tls in candidates:
        for username in usernames:
            key = (host, candidate_port, candidate_ssl, candidate_tls, username)
            if key in seen:
                continue
            seen.add(key)
            attempts.append(
                {
                    "host": host,
                    "port": candidate_port,
                    "use_ssl": candidate_ssl,
                    "use_tls": candidate_tls,
                    "username": username,
                }
            )
    return attempts


def send_service_mail(subject, message, recipient_list):
    if not settings.EMAIL_BACKEND.endswith("smtp.EmailBackend"):
        return send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

    errors = []
    for attempt in _smtp_attempts():
        label = (
            f"{attempt['host']}:{attempt['port']} "
            f"ssl={attempt['use_ssl']} tls={attempt['use_tls']} "
            f"user={_mask(attempt['username'])}"
        )
        print(f"EMAIL attempt {label}")
        try:
            connection = get_connection(
                backend=settings.EMAIL_BACKEND,
                host=attempt["host"],
                port=attempt["port"],
                username=attempt["username"],
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=attempt["use_ssl"],
                use_tls=attempt["use_tls"],
                timeout=settings.EMAIL_TIMEOUT,
                fail_silently=False,
            )
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                connection=connection,
            )
            sent_count = email.send()
            print(f"EMAIL sent {label}")
            return sent_count
        except Exception as exc:
            error = f"{label} -> {exc.__class__.__name__}: {exc}"
            print(f"EMAIL failed {error}")
            errors.append(error)

    raise EmailDeliveryError(" / ".join(errors))
