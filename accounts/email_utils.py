import smtplib
import socket
import ssl

import requests
from django.conf import settings
from django.core.mail import EmailMessage, send_mail


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
    elif host.lower() == "smtp.gmail.com":
        candidates = [(port, use_ssl, use_tls), (587, False, True), (465, True, False)]
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


class IPv4SMTP(smtplib.SMTP):
    def _get_socket(self, host, port, timeout):
        if self.debuglevel > 0:
            self._print_debug("connect: to", (host, port), self.source_address)

        last_error = None
        for family, socktype, proto, _, address in socket.getaddrinfo(
            host, port, socket.AF_INET, socket.SOCK_STREAM
        ):
            sock = None
            try:
                sock = socket.socket(family, socktype, proto)
                if timeout is not None:
                    sock.settimeout(timeout)
                if self.source_address:
                    sock.bind(self.source_address)
                sock.connect(address)
                return sock
            except OSError as exc:
                last_error = exc
                if sock is not None:
                    sock.close()

        if last_error:
            raise last_error
        raise OSError(f"No IPv4 address found for {host}")


class IPv4SMTPSSL(smtplib.SMTP_SSL):
    def _get_socket(self, host, port, timeout):
        raw_socket = IPv4SMTP._get_socket(self, host, port, timeout)
        return self.context.wrap_socket(raw_socket, server_hostname=self._host)


def _send_smtp_mail(attempt, subject, message, recipient_list):
    timeout = settings.EMAIL_TIMEOUT
    context = ssl.create_default_context()
    client = None
    try:
        if attempt["use_ssl"]:
            client = IPv4SMTPSSL(
                attempt["host"],
                attempt["port"],
                timeout=timeout,
                context=context,
            )
        else:
            client = IPv4SMTP(
                attempt["host"],
                attempt["port"],
                timeout=timeout,
            )
            if attempt["use_tls"]:
                client.ehlo()
                client.starttls(context=context)
                client.ehlo()

        if attempt["username"] and settings.EMAIL_HOST_PASSWORD:
            client.login(attempt["username"], settings.EMAIL_HOST_PASSWORD)

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
        )
        client.send_message(
            email.message(),
            from_addr=settings.DEFAULT_FROM_EMAIL,
            to_addrs=recipient_list,
        )
        return len(recipient_list)
    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                client.close()


def _send_resend_mail(subject, message, recipient_list):
    if not settings.RESEND_API_KEY:
        raise EmailDeliveryError("RESEND_API_KEY is not configured")

    response = requests.post(
        settings.RESEND_API_URL,
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.RESEND_FROM_EMAIL,
            "to": recipient_list,
            "subject": subject,
            "text": message,
        },
        timeout=settings.EMAIL_TIMEOUT,
    )
    if response.status_code >= 400:
        raise EmailDeliveryError(
            f"Resend API error {response.status_code}: {response.text}"
        )
    print(f"EMAIL sent resend to={len(recipient_list)}")
    return len(recipient_list)


def send_service_mail(subject, message, recipient_list):
    if settings.EMAIL_PROVIDER == "resend" or settings.RESEND_API_KEY:
        print(f"EMAIL attempt resend to={len(recipient_list)}")
        return _send_resend_mail(subject, message, recipient_list)

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
            sent_count = _send_smtp_mail(attempt, subject, message, recipient_list)
            print(f"EMAIL sent {label}")
            return sent_count
        except Exception as exc:
            error = f"{label} -> {exc.__class__.__name__}: {exc}"
            print(f"EMAIL failed {error}")
            errors.append(error)

    raise EmailDeliveryError(" / ".join(errors))
