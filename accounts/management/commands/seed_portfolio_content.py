from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from community.models import Post
from notices.models import Notice


NOTICE_ITEMS = [
    {
        "title": "ScholarMate 베타 서비스 안내",
        "content": (
            "ScholarMate는 학생의 학업 정보와 관심 조건을 바탕으로 장학금 탐색을 "
            "돕는 포트폴리오용 데모 서비스입니다. 현재 주요 기능은 장학금 목록, "
            "추천 결과, 커뮤니티, 공지사항, 문의 접수입니다."
        ),
        "is_pinned": True,
    },
    {
        "title": "맞춤 장학금 추천 이용 방법",
        "content": (
            "마이페이지에서 학년, 전공, 성적, 지역, 소득구간 등의 정보를 입력하면 "
            "조건에 맞는 장학금을 더 쉽게 비교할 수 있습니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "장학금 검색 필터 업데이트",
        "content": (
            "장학금 목록에서 지역, 모집 상태, 학업 조건을 기준으로 결과를 좁혀볼 수 "
            "있도록 필터 기능을 개선했습니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "커뮤니티 이용 안내",
        "content": (
            "커뮤니티 목록은 누구나 둘러볼 수 있습니다. 게시글 상세 보기, 댓글, "
            "좋아요, 북마크, 쪽지 기능은 로그인 후 사용할 수 있습니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "공지사항 공개 정책",
        "content": (
            "공지사항은 로그인하지 않은 사용자도 확인할 수 있습니다. 서비스 변경, "
            "데이터 갱신, 점검 안내를 이곳에서 확인하세요."
        ),
        "is_pinned": False,
    },
    {
        "title": "장학 캘린더 기능 안내",
        "content": (
            "관심 있는 장학금을 저장하면 마감일을 캘린더에서 확인할 수 있습니다. "
            "마감 알림 기능은 로그인 후 사용할 수 있습니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "문의 접수 기능 안내",
        "content": (
            "메인 화면의 문의하기 폼을 통해 서비스 개선 의견이나 오류 제보를 남길 수 "
            "있습니다. 접수된 내용은 관리자에게 전달됩니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "데모 데이터 안내",
        "content": (
            "포트폴리오 시연을 위해 일부 공지사항과 커뮤니티 게시글은 샘플 데이터로 "
            "구성되어 있습니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "개인정보 입력 주의",
        "content": (
            "데모 환경에서는 실제 주민등록번호, 계좌번호, 민감한 개인정보를 입력하지 "
            "않는 것을 권장합니다."
        ),
        "is_pinned": False,
    },
    {
        "title": "서비스 점검 및 개선 예정",
        "content": (
            "추천 정확도 개선, 장학금 데이터 최신화 자동화, 프론트엔드 접근성 개선을 "
            "계속 진행할 예정입니다."
        ),
        "is_pinned": False,
    },
]


POST_ITEMS = [
    {
        "title": "국가장학금 신청 전에 확인한 체크리스트",
        "category": "story",
        "scholarship_name": "국가장학금",
        "content": (
            "신청 전에 소득구간, 성적 기준, 재학 상태, 제출 서류를 먼저 확인했습니다. "
            "가장 도움이 된 것은 마감일을 캘린더에 따로 표시해 둔 것이었습니다."
        ),
        "tags": ["국가장학금", "신청팁", "마감관리"],
        "author_is_recipient": True,
        "view_count": 42,
    },
    {
        "title": "교내 장학금은 공지 확인 주기가 중요했습니다",
        "category": "story",
        "scholarship_name": "교내 성적우수 장학금",
        "content": (
            "교내 장학금은 모집 기간이 짧은 경우가 많아서 학교 공지와 학과 공지를 "
            "함께 보는 습관이 중요했습니다."
        ),
        "tags": ["교내장학금", "성적", "공지확인"],
        "author_is_recipient": True,
        "view_count": 31,
    },
    {
        "title": "추천 장학금 결과를 우선순위로 정리해봤어요",
        "category": "feed",
        "scholarship_name": "",
        "content": (
            "추천 결과를 볼 때 지원 가능성, 마감일, 제출 서류 난이도를 같이 비교하니 "
            "어떤 장학금부터 준비해야 할지 더 명확했습니다."
        ),
        "tags": ["추천", "우선순위", "비교"],
        "author_is_recipient": False,
        "view_count": 27,
    },
    {
        "title": "자기소개서 문항은 미리 모아두는 게 좋습니다",
        "category": "story",
        "scholarship_name": "민간재단 장학금",
        "content": (
            "재단마다 비슷한 자기소개서 문항이 반복되어서 지원 동기, 학업 계획, "
            "경제 상황 설명을 미리 정리해두면 여러 장학금에 재활용하기 좋았습니다."
        ),
        "tags": ["자기소개서", "민간재단", "지원동기"],
        "author_is_recipient": True,
        "view_count": 36,
    },
    {
        "title": "지역 장학금은 주소 기준을 꼭 확인하세요",
        "category": "feed",
        "scholarship_name": "지역인재 장학금",
        "content": (
            "지역 장학금은 본인 주소, 부모님 주소, 출신 고등학교 기준이 다를 수 있어 "
            "공고문을 꼼꼼히 읽는 것이 필요했습니다."
        ),
        "tags": ["지역장학금", "주소기준", "공고확인"],
        "author_is_recipient": False,
        "view_count": 24,
    },
    {
        "title": "장학금 마감일을 놓치지 않는 방법",
        "category": "story",
        "scholarship_name": "",
        "content": (
            "관심 장학금은 바로 저장하고 마감일 기준으로 일주일 전, 하루 전 알림을 "
            "설정해두면 제출 실수를 줄일 수 있었습니다."
        ),
        "tags": ["마감일", "캘린더", "알림"],
        "author_is_recipient": True,
        "view_count": 48,
    },
    {
        "title": "소득분위 서류 준비가 생각보다 오래 걸렸습니다",
        "category": "feed",
        "scholarship_name": "생활비 지원 장학금",
        "content": (
            "소득 관련 서류는 발급처와 기준일을 확인해야 해서 미리 준비하는 것이 "
            "좋았습니다. 가족관계증명서도 요구되는 경우가 있었습니다."
        ),
        "tags": ["소득분위", "서류", "생활비"],
        "author_is_recipient": False,
        "view_count": 22,
    },
    {
        "title": "면접형 장학금 준비 후기",
        "category": "story",
        "scholarship_name": "인재육성 장학금",
        "content": (
            "면접에서는 장학금이 필요한 이유보다 앞으로의 학업 계획과 사회 기여 계획을 "
            "구체적으로 설명하는 것이 중요했습니다."
        ),
        "tags": ["면접", "학업계획", "후기"],
        "author_is_recipient": True,
        "view_count": 39,
    },
    {
        "title": "전공 관련 장학금 찾는 팁",
        "category": "feed",
        "scholarship_name": "전공특화 장학금",
        "content": (
            "전공 키워드로 검색할 때 학과명뿐 아니라 산업 분야, 직무명, 관련 자격증도 "
            "함께 검색하면 더 많은 공고를 찾을 수 있었습니다."
        ),
        "tags": ["전공", "검색팁", "자격증"],
        "author_is_recipient": False,
        "view_count": 33,
    },
    {
        "title": "장학금 지원 기록을 남겨두면 다음 지원이 쉬워요",
        "category": "story",
        "scholarship_name": "",
        "content": (
            "지원했던 장학금, 제출 서류, 결과, 개선할 점을 기록해두면 다음 지원 때 "
            "준비 시간이 줄어듭니다."
        ),
        "tags": ["지원기록", "포트폴리오", "준비"],
        "author_is_recipient": True,
        "view_count": 29,
    },
]


class Command(BaseCommand):
    help = "Seed portfolio demo notices and community posts."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="portfolio_admin")
        parser.add_argument("--email", default="portfolio_admin@scholarmate.local")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        if options["dry_run"]:
            self.stdout.write(
                f"Would seed notices={len(NOTICE_ITEMS)}, posts={len(POST_ITEMS)}"
            )
            return

        User = get_user_model()
        author, _ = User.objects.get_or_create(
            username=options["username"],
            defaults={
                "email": options["email"],
                "is_staff": True,
                "is_superuser": False,
            },
        )

        notice_count = 0
        for item in NOTICE_ITEMS:
            _, created = Notice.objects.update_or_create(
                title=item["title"],
                defaults={
                    "content": item["content"],
                    "is_pinned": item["is_pinned"],
                    "is_published": True,
                },
            )
            if created:
                notice_count += 1

        post_count = 0
        for item in POST_ITEMS:
            _, created = Post.objects.update_or_create(
                title=item["title"],
                defaults={
                    **item,
                    "author": author,
                    "is_published": True,
                },
            )
            if created:
                post_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Portfolio content seeded: "
                f"notices={Notice.objects.count()} (+{notice_count}), "
                f"posts={Post.objects.count()} (+{post_count})"
            )
        )
