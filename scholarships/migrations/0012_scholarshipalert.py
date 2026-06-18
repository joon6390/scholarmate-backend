from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("scholarships", "0011_rawscholarship_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScholarshipAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("remind_days_before", models.PositiveSmallIntegerField(default=1, verbose_name="마감 전 알림일")),
                ("last_sent_for_date", models.DateField(blank=True, null=True, verbose_name="마지막 발송 대상일")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="등록일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="사용자")),
                ("wishlist", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="scholarships.wishlist", verbose_name="찜 목록")),
            ],
            options={
                "verbose_name": "장학금 알림",
                "verbose_name_plural": "장학금 알림 목록",
            },
        ),
    ]
