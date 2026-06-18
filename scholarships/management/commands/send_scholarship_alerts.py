from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from scholarships.models import ScholarshipAlert


class Command(BaseCommand):
    help = "Send deadline reminder emails for registered scholarship calendar alerts."

    def add_arguments(self, parser):
        parser.add_argument("--days-before", type=int, default=1)
        parser.add_argument("--date", help="Base date in YYYY-MM-DD. Defaults to today.")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        days_before = options["days_before"]
        base_date = (
            timezone.datetime.fromisoformat(options["date"]).date()
            if options.get("date")
            else timezone.localdate()
        )
        target_date = base_date + timedelta(days=days_before)

        alerts = (
            ScholarshipAlert.objects.select_related("user", "wishlist__scholarship")
            .filter(
                remind_days_before=days_before,
                wishlist__scholarship__recruitment_end=target_date,
            )
            .exclude(last_sent_for_date=target_date)
        )

        sent = 0
        skipped = 0
        for alert in alerts:
            user = alert.user
            scholarship = alert.wishlist.scholarship
            email = (user.email or "").strip()
            if not email:
                skipped += 1
                self.stdout.write(f"skip no email: user={user.username}, scholarship={scholarship.name}")
                continue

            subject = f"[ScholarMate] 내일 마감: {scholarship.name}"
            body = "\n".join(
                [
                    f"{user.username}님, 등록한 장학금 알림입니다.",
                    "",
                    f"장학금: {scholarship.name}",
                    f"기관: {scholarship.foundation_name or '정보 없음'}",
                    f"마감일: {target_date.isoformat()}",
                    "",
                    "제출 서류:",
                    scholarship.required_documents_details or "제출 서류 정보가 없습니다.",
                    "",
                    "ScholarMate 캘린더에서 상세 정보를 확인해 주세요.",
                ]
            )

            if options["dry_run"]:
                self.stdout.write(f"dry-run send: {email} / {scholarship.name}")
            else:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                alert.last_sent_for_date = target_date
                alert.save(update_fields=["last_sent_for_date", "updated_at"])
            sent += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"scholarship alerts checked: target={target_date}, sent={sent}, skipped={skipped}"
            )
        )
