# 🎓 ScholarMate Backend

ScholarMate는 AI 기반 개인 맞춤형 장학금 추천 서비스입니다.  
이 저장소는 ScholarMate의 **백엔드 (Django + MySQL)** 프로젝트를 포함하고 있습니다.

## ⚙️ 개발 환경 

- **OS**: Ubuntu 24.04.2 LTS
- **Programming Language**: Python 3.12.3
- **Framework**: TBD
- **Database**:  TBD
- **Package Manager**: pip 24.0
- **Web Server**: Nginx 1.26.3
- **Application Server**: Gunicorn 23.0.0
- **Containerization**: Docker 28.0.1


## 📌 프로젝트 개요
- **프로젝트명:** ScholarMate Backend
- **기술 스택:** Django, Django REST Framework, MySQL, AWS
- **주요 기능:** 
  - 사용자 로그인/회원가입 (JWT 인증)
  - 장학금 데이터 크롤링 및 저장
  - AI 기반 장학금 추천 시스템
  - 사용자 맞춤형 필터링 기능

---

## 🛠️ 사용 기술
| 기술 | 설명 |
|------------|-----------------------------|
| **Django** | Python 기반 웹 프레임워크 |
| **Django REST Framework** | RESTful API 구축을 위한 도구 |
| **MySQL** | 데이터베이스 |
| **JWT (Simple JWT)** | 사용자 인증 및 보안 |
| **Celery & Redis** | 비동기 작업 처리 |

---

## 💻 로컬 실행

배포용 `.env`가 없으면 기본으로 SQLite DB와 메모리 캐시를 사용합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_local
python manage.py runserver 127.0.0.1:8000
```

실행 후 아래 주소에서 서버 상태를 확인할 수 있습니다.

```text
http://127.0.0.1:8000/
```

MySQL/Redis를 사용하려면 `.env`에 `DATABASE_NAME`, `DATABASE_USER`,
`DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `REDIS_CACHE_URL`을
설정하면 됩니다.

`python manage.py setup_local`은 로컬 확인용 관리자 계정과 샘플 공지/커뮤니티 글을 생성합니다.

- 관리자 아이디: `admin`
- 관리자 비밀번호: `Admin12345!`

SMTP 설정이 없으면 인증/문의 메일은 실제 발송 대신 `local_emails/` 폴더에 파일로 저장됩니다.

---

## 🚀 Railway 배포

이 프로젝트는 `Dockerfile` 기준으로 Railway에 배포할 수 있습니다.
컨테이너 시작 시 `python manage.py migrate --noinput`을 실행한 뒤,
Railway가 주입하는 `PORT` 값으로 Gunicorn을 실행합니다.

### 1. Railway 서비스 구성

1. Railway에서 이 백엔드 저장소를 연결합니다.
2. MySQL 플러그인을 추가합니다.
3. 백엔드 서비스에 필요한 환경변수를 설정합니다.
4. 배포 후 생성된 Railway 도메인을 프론트엔드 API 주소로 사용합니다.

### 2. 필수 환경변수

| 이름 | 예시/설명 |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django 운영용 secret key |
| `DJANGO_DEBUG` | `False` |
| `OPENAI_API_KEY` | 장학금 추천 기능용 OpenAI API key |
| `SERVICE_KEY` | 장학금 API/service key |
| `FRONTEND_DOMAIN` | `scholar-mate-chi.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | `https://scholar-mate-chi.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://scholar-mate-chi.vercel.app,https://<railway-domain>` |

`DJANGO_ALLOWED_HOSTS`는 Railway가 제공하는 `RAILWAY_PUBLIC_DOMAIN`을 자동으로 추가합니다.
커스텀 도메인을 붙이면 `DJANGO_ALLOWED_HOSTS`에 해당 도메인을 쉼표로 추가하세요.

### 3. 데이터베이스 환경변수

Railway MySQL 플러그인의 기본 변수명을 그대로 사용할 수 있습니다.

| Railway 변수 | Django에서 사용하는 값 |
| --- | --- |
| `MYSQLDATABASE` | DB 이름 |
| `MYSQLUSER` | DB 사용자 |
| `MYSQLPASSWORD` | DB 비밀번호 |
| `MYSQLHOST` | DB 호스트 |
| `MYSQLPORT` | DB 포트 |

기존 `.env` 방식의 `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`,
`DATABASE_HOST`, `DATABASE_PORT`도 계속 지원합니다. `DATABASE_URL` 또는
`MYSQL_URL`이 있으면 해당 URL을 우선 사용합니다.

### 4. 선택 환경변수

| 이름 | 설명 |
| --- | --- |
| `REDIS_URL` 또는 `REDIS_CACHE_URL` | Redis 캐시/Celery broker |
| `EMAIL_HOST` | SMTP 호스트 |
| `EMAIL_PORT` | SMTP 포트 |
| `EMAIL_HOST_USER` | SMTP 사용자 |
| `EMAIL_HOST_PASSWORD` | SMTP 비밀번호 |
| `DEFAULT_FROM_EMAIL` | 발신 이메일 |
| `EMAIL_PROVIDER` | `smtp` 또는 `resend` |
| `RESEND_API_KEY` | Resend HTTPS API 발송용 API key |
| `RESEND_FROM_EMAIL` | Resend 발신자, 예: `ScholarMate <onboarding@resend.dev>` |
| `CONTACT_ADMIN_EMAILS` | 문의 수신 이메일, 쉼표 구분 |
| `DJANGO_SECURE_HSTS_SECONDS` | 예: `31536000`, HTTPS 전용 운영 시 설정 |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | 모든 하위 도메인이 HTTPS일 때만 `True` |
| `DJANGO_SECURE_HSTS_PRELOAD` | HSTS preload 제출 조건을 만족할 때만 `True` |

Redis를 붙이지 않으면 캐시는 메모리 캐시를 사용합니다. 다만 Celery worker를 별도
서비스로 운영하려면 Redis를 추가하고 `CELERY_BROKER_URL` 또는 `REDIS_URL`을
설정해야 합니다.
