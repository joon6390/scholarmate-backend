import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from community.models import Post
from notices.models import Notice


class Command(BaseCommand):
    help = "Prepare local admin account and starter content for development."

    def add_arguments(self, parser):
        parser.add_argument("--admin-username", default=os.getenv("LOCAL_ADMIN_USERNAME", "admin"))
        parser.add_argument("--admin-email", default=os.getenv("LOCAL_ADMIN_EMAIL", "admin@localhost"))
        parser.add_argument(
            "--admin-password",
            default=os.getenv("LOCAL_ADMIN_PASSWORD", "Admin12345!"),
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["admin_username"]
        email = options["admin_email"]
        password = options["admin_password"]

        admin_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
        else:
            changed = False
            if not admin_user.is_staff:
                admin_user.is_staff = True
                changed = True
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                changed = True
            if not admin_user.email:
                admin_user.email = email
                changed = True
            if changed:
                admin_user.save(update_fields=["is_staff", "is_superuser", "email"])
            self.stdout.write(f"Superuser already exists: {username}")

        notices = [
            {
                "title": "ScholarMate 로컬 실행 안내",
                "content": (
                    "이 공지는 로컬 개발 환경 확인용입니다. "
                    "장학금 데이터는 한국장학재단 공개 데이터 기준으로 동기화됩니다."
                ),
                "is_pinned": True,
            },
            {
                "title": "장학금 정보 자동 최신화",
                "content": "Windows 작업 스케줄러가 매주 월요일 오전 10시에 장학금 데이터를 갱신합니다.",
                "is_pinned": False,
            },
        ]
        for data in notices:
            Notice.objects.get_or_create(title=data["title"], defaults=data)

        posts = [
            {
                "title": "국가장학금 신청할 때 체크한 것들",
                "category": "story",
                "scholarship_name": "국가장학금",
                "content": (
                    "신청 전에 소득구간, 성적 기준, 제출 서류를 먼저 확인하면 시간이 줄어듭니다."
                ),
                "tags": ["국가장학금", "신청팁"],
                "author_is_recipient": True,
            },
            {
                "title": "추천 장학금 결과를 비교해봤습니다",
                "category": "feed",
                "scholarship_name": "",
                "content": "추천 이유와 모집 기간을 같이 보니 우선순위를 정하기 쉬웠습니다.",
                "tags": ["추천", "후기"],
                "author_is_recipient": False,
            },
        ]
        for data in posts:
            Post.objects.get_or_create(title=data["title"], defaults={**data, "author": admin_user})

        self.stdout.write(
            self.style.SUCCESS(
                "Local setup complete. "
                f"admin={username}, notices={Notice.objects.count()}, posts={Post.objects.count()}"
            )
        )
