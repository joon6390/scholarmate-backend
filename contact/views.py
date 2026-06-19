from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from accounts.email_utils import send_service_mail
from .models import Contact
from .serializers import ContactSerializer

class ContactCreateView(CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()  # DB 저장

        # ----- f-string 내부에 백슬래시가 없도록 미리 전처리 -----
        created_at_str = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")

        subject = "[문의 알림] 새 문의가 도착했습니다"
        text_body = (
            f"이름: {instance.name}\n"
            f"이메일: {instance.email}\n\n"
            f"메시지:\n{instance.message}\n\n"
            f"접수시각: {created_at_str}"
        )

        to_emails = getattr(settings, "CONTACT_ADMIN_EMAILS", [])
        if to_emails:
            try:
                send_service_mail(subject, text_body, to_emails)
            except Exception as exc:
                # 메일 실패는 서비스에 영향 없게 무시(로그만 남기는 정도)
                print(f"[ContactCreateView] Mail send failed: {exc}")

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"ok": True}, status=status.HTTP_201_CREATED)
