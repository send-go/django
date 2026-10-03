# sendgo-django

> **Django에서 카카오 알림톡, 브랜드메시지, SMS를 가장 쉽게 발송하는 공식 Django 확장 패키지**

[![PyPI](https://img.shields.io/pypi/v/sendgo-django)](https://pypi.org/project/sendgo-django/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-092E20?logo=django)](https://www.djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

`sendgo-django`는 [`sendgo-python`](https://github.com/send-go/python) 코어를 확장한 **Django 전용 패키지**입니다.
`settings.SENDGO` 설정 기반의 클라이언트 생성, 지연 로딩 프록시(`client`), AppConfig 통합을 제공합니다.

---

## 목차

- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [프록시 사용법](#프록시-사용법)
- [상세 사용법](#상세-사용법)
  - [알림톡](#알림톡)
  - [친구톡](#친구톡)
  - [SMS / LMS / MMS](#sms--lms--mms)
- [서비스 클래스 패턴](#서비스-클래스-패턴)
- [예외 처리](#예외-처리)
- [설정 옵션](#설정-옵션)
- [자주 묻는 질문](#자주-묻는-질문-faq)

---

## 설치

```bash
pip install sendgo-django
```

`sendgo-python` 코어는 의존성으로 자동 설치됩니다.

---

## 빠른 시작

### 1단계 — `INSTALLED_APPS` 등록 (`settings.py`)

```python
INSTALLED_APPS += ["sendgo_django"]
```

### 2단계 — `SENDGO` 설정 추가 (`settings.py`)

```python
import os

SENDGO = {
    "ACCESS_KEY": os.environ["SENDGO_ACCESS_KEY"],
    "SECRET_KEY": os.environ["SENDGO_SECRET_KEY"],
    "KAKAO_SENDER_KEY": os.environ.get("SENDGO_KAKAO_SENDER_KEY"),
    "SMS_SENDER_KEY": os.environ.get("SENDGO_SMS_SENDER_KEY"),
    "API_VERSION": "v2",
    # "BASE_URL": "https://sendgo.io",  # 기본값
}
```

### 3단계 — 뷰에서 알림톡 전송

```python
# views.py
from django.http import JsonResponse
from sendgo_django import client


def confirm_order(request, order_id):
    order = get_order(order_id)

    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[
            {
                "contact": order.phone,
                "name": order.name,
                "var1": order.number,
                "var2": f"{order.total:,}원",
            },
        ],
    )

    return JsonResponse({"success": True})
```

---

## 프록시 사용법

`sendgo_django.client`는 `SimpleLazyObject` 기반 **지연 로딩 프록시**입니다.
패키지를 임포트하는 시점에는 클라이언트를 생성하지 않고, 실제로 속성에 접근할 때
`get_client()`를 호출합니다. 따라서 설정이 없어도 임포트만으로는 오류가 나지 않습니다.

```python
from sendgo_django import client

# 알림톡 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
)

# SMS 발송
client.sms.send_sms(
    content="[인증] 인증번호: 123456",
    contacts=[{"contact": "01012345678"}],
)
```

명시적으로 인스턴스를 얻고 싶다면 `get_client()`를 직접 호출할 수 있습니다.

```python
from sendgo_django import get_client

sendgo = get_client()
sendgo.friendtalk.send(content="안녕하세요!", contacts=[{"contact": "01012345678"}])
```

---

## 상세 사용법

### 알림톡

```python
from sendgo_django import client

# 다건 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[
        {"contact": "01011111111", "name": "홍길동", "var1": "ORD-001", "var2": "29,000원"},
        {"contact": "01022222222", "name": "김철수", "var1": "ORD-002", "var2": "15,000원"},
    ],
)
```

### 친구톡

> ⚠️ **Deprecated — 친구톡은 카카오 정책에 따라 2025-12-31 종료되었습니다.**
> 2026-01-01 부터 친구톡 발송 요청은 카카오 측에서 **브랜드메시지(자유형)** 로 자동 대체 발송됩니다.
> 호출은 계속 성공하며, 자유 본문 타입(`FT`/`FI`/`FW`)을 개별 수신자에게 보내는 경로는
> 현재 이것뿐이므로 기존 코드를 당장 바꿀 필요는 없습니다.
>
> 다음의 경우에는 **브랜드메시지**를 사용하세요.
> - 템플릿 기반 리치 타입 (`FL`/`FC`/`FM`/`FP`/`FA`)
> - 채널 친구가 **아닌** 수신자 (`targeting` = `N` / `I`)
> - 수신 동의한 전체 채널 친구 동보 (`targeting` = `F`)
>
> 메시지 타입은 1:1 대응되며 변환은 서버가 처리합니다 — `FT`→`BT`, `FI`→`BI`, `FW`→`BW`,
> `FL`→`BL`, `FC`→`BC`, `FM`→`BM`, `FP`→`BP`, `FA`→`BA`.

```python
from sendgo_django import client

# 텍스트형
client.friendtalk.send(
    content="안녕하세요! 7월 한정 특가 이벤트를 확인해보세요.",
    contacts=[{"contact": "01012345678"}],
)
```

### SMS / LMS / MMS

```python
from sendgo_django import client

# SMS (90자 이하)
client.sms.send_sms(
    content="[Sendgo] 인증번호: 123456 (5분 이내 입력)",
    contacts=[{"contact": "01012345678"}],
)
```

---

## 서비스 클래스 패턴

```python
# app/services.py
import logging

from sendgo import SendgoError
from sendgo_django import client

logger = logging.getLogger(__name__)


class NotificationService:
    """알림 발송 로직을 캡슐화한 서비스 클래스."""

    def send_order_confirm(self, phone: str, order_no: str, amount: int) -> None:
        client.alimtalk.send(
            template_code="ORDER_CONFIRM_001",
            contacts=[{"contact": phone, "var1": order_no, "var2": f"{amount:,}원"}],
        )

    def send_verification_code(self, phone: str, code: str) -> None:
        try:
            client.alimtalk.send(
                template_code="VERIFY_CODE_001",
                contacts=[{"contact": phone, "var1": code}],
            )
        except SendgoError:
            logger.exception("Sendgo 인증번호 발송 실패")
            raise
```

---

## 예외 처리

```python
from sendgo import SendgoError
from sendgo_django import client

try:
    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
    )
except SendgoError as e:
    logger.error("Sendgo 발송 실패: %s", e)
```

---

## 설정 옵션

`settings.SENDGO` 딕셔너리 키:

| 키 | 필수 | 기본값 | 설명 |
|----|------|--------|------|
| `ACCESS_KEY` | ✅ | — | Sendgo 액세스 키 |
| `SECRET_KEY` | ✅ | — | Sendgo 시크릿 키 |
| `KAKAO_SENDER_KEY` | | `None` | 카카오 발신프로필 키 |
| `SMS_SENDER_KEY` | | `None` | SMS 발신자 키 |
| `API_VERSION` | | `"v2"` | API 버전 |
| `BASE_URL` | | `"https://sendgo.io"` | API 기본 URL |

`ACCESS_KEY` 또는 `SECRET_KEY`가 없으면 클라이언트 생성 시 `django.core.exceptions.ImproperlyConfigured`가 발생합니다.

---

## 자주 묻는 질문 (FAQ)

**Q. `sendgo-python`과의 차이는 무엇인가요?**
A. `sendgo-python`은 프레임워크 독립적인 순수 Python 코어 패키지입니다. `sendgo-django`는 이를 확장해 `settings.SENDGO` 설정 바인딩, 지연 로딩 프록시, AppConfig 통합을 추가합니다.

**Q. 설정 없이 임포트하면 오류가 나나요?**
A. 아니요. `client`는 지연 프록시이므로 임포트만으로는 오류가 없고, 실제 사용(속성 접근) 시점에 설정을 검증합니다.

**Q. 테스트 시 클라이언트를 초기화하려면?**
A. `sendgo_django.conf.reset()`을 호출하면 메모이즈된 클라이언트가 초기화됩니다.

**Q. Django 4.2, 5.x를 지원하나요?**
A. 네, `Django>=4.2`를 지원합니다.

---

## 관련 패키지

| 언어/프레임워크 | 패키지 | GitHub |
|----------------|--------|--------|
| Python (순수) | `sendgo-python` | [python](https://github.com/send-go/python) |
| Laravel | `sendgo/laravel` | [laravel](https://github.com/send-go/laravel) |
| Spring Boot | `io.sendgo:sendgo-spring` | [spring](https://github.com/send-go/spring) |
| Node.js | `@sendgo/node` | [node](https://github.com/send-go/node) |
| 전체 목록 | — | [send-go GitHub 조직](https://github.com/send-go) |

---

## 브랜드메시지 · 짧은 URL

이 패키지는 코어(`sendgo-python`)의 클라이언트를 그대로 노출하므로, 코어에 있는 채널이
모두 그대로 쓸 수 있습니다. 두 기능 모두 **v2 전용**입니다.

| 기능 | 접근 |
|------|------|
| 카카오 브랜드메시지 (친구톡의 후속 채널) | `client.brand_message` |
| 짧은 URL (단축 + 클릭 반응 분석) | `client.short_url` |

브랜드메시지는 채널 친구가 아닌 수신자에게도 보낼 수 있고(`targeting` = `N`),
수신 동의한 전체 채널 친구에게 동보 발송할 수도 있습니다(`targeting` = `F`).

짧은 URL 은 메시지 본문의 링크를 줄이고 클릭 반응(일별 추이·디바이스·유입경로·국가)을
집계합니다.

사용 예시와 파라미터는 [코어 README](https://github.com/send-go) 와
[SDK 가이드](https://sendgo.io/ko/sdk) 를 참고하세요.

## 관리 API — 채널·템플릿·발신번호 등록 (v2 전용)

코어(`sendgo-python`)의 관리 서비스가 `client` 프록시에 그대로 붙어 있습니다.
콘솔에서만 되던 등록·심사를 뷰나 관리 명령에서 처리할 수 있습니다.

| 접근 | 하는 일 | 계정 |
| --- | --- | --- |
| `.kakao_senders` | 카카오 채널 인증·등록·동기화, 브랜드메시지 M/N 신청 | 기업 |
| `.notice_templates` | 알림톡 템플릿 CRUD, 검수 요청·취소, 승인 취소, 휴면 해제 | 기업 |
| `.brand_templates` | 브랜드메시지 템플릿 CRUD, 동기화, 가져오기 | 기업 |
| `.sender_registration` | 발신번호 등록 신청, 중복 확인, 유형 안내 | 개인·기업 |
| `.message_templates` | 문자 상용구 템플릿 CRUD | 개인·기업 |
| `.kakao_images` | 카카오 이미지 업로드 — 템플릿용 URL 발급 | 기업 |
| `.rejected_numbers` | 수신거부(080) 번호 조회 | 개인·기업 |
| `.webhook` | 이벤트 웹훅 구독 — 심사 결과 수신 | 개인·기업 |

> **sendgo.io 콘솔에 들어올 일이 없습니다.** 휴대폰 발신번호는 PASS 대신
> 신분증 사본을 받아 sendgo 운영자가 대신 심사합니다. 사람이 개입하는 지점은
> 카카오 채널 인증번호 하나뿐이고, 그것도 여러분 화면에서 입력받으면 됩니다.
> 심사가 붙는 것들은 비동기라 웹훅으로 결과를 받으세요.

```python
# views.py — 카카오 채널 등록 2단계
from sendgo_django import client


def request_channel_code(request):
    # 카카오가 관리자 휴대폰으로 인증번호를 SMS 발송한다 (응답에 번호는 없다)
    client.kakao_senders.request_token(
        request.POST["yellow_id"],
        request.POST["phone"],
    )
    return JsonResponse({"message": "인증번호를 발송했습니다."})


def complete_channel(request):
    created = client.kakao_senders.create(
        token=request.POST["code"],            # 사용자가 문자로 받은 인증번호
        yellow_id=request.POST["yellow_id"],
        phone_number=request.POST["phone"],
        category_code="001001",
    )
    return JsonResponse(created["data"]["sender"])
```

```python
# management/commands/provision_templates.py
from django.core.management.base import BaseCommand
from sendgo_django import client


class Command(BaseCommand):
    help = "표준 알림톡 템플릿을 등록하고 검수를 요청한다"

    def handle(self, *args, **options):
        created = client.notice_templates.create(
            kakao_sender_key=options["kakao_sender_key"],
            template_name="주문 접수 안내",
            template_content="#{name}님, 주문 #{orderNo}이 접수되었습니다.",
            template_message_type="BA",
            template_emphasize_type="NONE",
            category_code="001001",
            message_purpose="order_delivery",
            legal_basis="transaction",
            benefit_origin="none",
            expiry_type="none",
        )

        code = created["data"]["template"]["templateCode"]
        client.notice_templates.request_inspection(code)

        # 검수는 30분~1영업일 걸린다. 여기서 기다리지 말고 Celery beat 나
        # cron 으로 sync() 를 돌려 inspectionStatus 가 APR 이 되는지 확인한다.
        self.stdout.write(self.style.SUCCESS(f"검수 요청 완료: {code}"))
```

전체 파라미터는 [sendgo-python README](https://github.com/send-go/python) 를 참고하세요.

---

## 변경 사항

### 1.3.0 (2026-09-11)

- **관리 API 노출** — 코어 1.3.0 의 `kakao_senders` · `notice_templates` ·
  `brand_templates` · `sender_registration` · `message_templates` 를
  `sendgo_django.client` 에서 그대로 쓸 수 있습니다. 콘솔에서만 되던 채널 등록,
  알림톡 템플릿 검수 요청, 발신번호 심사 접수를 뷰나 관리 명령에서 처리합니다.
- **`__version__` 이 `1.0.0` 에 멈춰 있던 것을 고쳤습니다.** 이제 설치된 패키지
  메타데이터에서 읽으므로 pyproject.toml 이 단일 출처입니다.
- `sendgo-python` 을 `>=1.3` 으로 올렸습니다.
- **이벤트 웹훅** 추가 — 발신번호 승인, 알림톡 검수 결과, 채널 차단,
  브랜드메시지 타겟팅 결과를 구독해 받습니다. 서명은 받은 원본 바이트로
  검증합니다(SDK 에 검증 헬퍼 포함).
- **카카오 이미지 업로드** 추가 — 브랜드메시지 템플릿의 `imageUrl` 은 카카오가
  호스팅하는 URL 이어야 하는데, 그 URL 을 얻는 길이 콘솔에만 있었습니다.
- **수신거부(080) 조회** 추가 — 자기 DB 의 수신 상태를 맞출 수 있습니다.

### 1.2.1 (2026-08-14)

- 레지스트리 목록에 노출되는 패키지 설명에서 친구톡을 브랜드메시지로 교체했습니다.
  npm/PyPI/Packagist/Maven/NuGet/RubyGems 검색 결과에 그대로 찍히는 문자열이라
  종료된 채널을 계속 홍보하고 있었습니다.
- 검색 키워드에 `brand-message` 를 추가했습니다 (`friendtalk` 은 유입 검색어라 유지).

### 1.2.0 (2026-08-14)

- **친구톡 Deprecated 표기** — 친구톡은 카카오 정책에 따라 2025-12-31 종료되었고,
  2026-01-01 부터 발송 요청이 브랜드메시지(자유형)로 자동 대체 발송됩니다.
  관련 API 에 각 언어의 표준 deprecation 표기를 달았습니다.
- 자유 본문 타입(`FT`/`FI`/`FW`)의 개별 발송 경로는 아직 친구톡 API 뿐이라는 점을
  문서에 명시했습니다 — 브랜드메시지 API 는 그 조합에 `NOT_A_BRAND_MESSAGE` 를 반환합니다.
- 브랜드메시지 전환 안내와 메시지 타입 1:1 대응표를 README 에 추가했습니다.
- 짧은 URL 지원 (1.1.0 릴리스 누락분 포함).

### 1.1.0 (2026-08-11)

- 브랜드메시지·짧은 URL 접근 방법 문서화 (코어를 그대로 노출)

## 라이선스

MIT License © 2026 [Sendgo](https://sendgo.io)

---

*키워드: 카카오 알림톡 Django, 카카오 친구톡 Django, SMS 발송 Django, 알림톡 Django 패키지, Django 카카오 API 연동, Sendgo Django SDK*

## 계정 API (1.6.0)

코어 1.6.0의 계정·조직·API 키·허용 IP 관리 12개 API를 사용할 수 있습니다.
발송용 키 없이 에이전트 토큰만으로 구성할 수 있습니다.

발송용 `accessKey`/`secretKey`가 없는 단계에서 사용하는 **별도 계정 클라이언트**입니다.
콘솔에서 발급받은 에이전트 토큰(`SENDGO_AGENT_TOKEN`)으로 `/api/v2/account`를 호출합니다.
계정 조회에는 `account:read`, 키·허용 IP 변경에는 `keys:write` 권한이 필요합니다.
토큰 만료나 권한 부족(401/403)은 그대로 예외로 반환하며 자동 갱신·재시도하지 않습니다.

조직 선택은 서버에 저장되는 **사용자 계정의 현재 조직**을 바꿉니다. 같은 사용자로
여러 조직의 설정을 동시에 변경하지 마세요. 개인 계정으로 돌아가려면 조직 ID에
`null`(Python `None`, Ruby `nil`, Go `nil`) 또는 `personal`을 전달합니다.
키 발급 응답의 `data.apiKey.secretKey`는 한 번만 반환되므로 서버의 비밀 저장소에 보관하세요.
허용 IP가 하나라도 등록되면 목록 밖의 IP는 차단됩니다.
에이전트 토큰과 키는 브라우저·모바일 앱에 포함하거나 응답·로그에 출력하지 않습니다.

```python
# settings.py
SENDGO = {'AGENT_TOKEN': os.environ['SENDGO_AGENT_TOKEN']}

from sendgo_django import get_account_client
status = get_account_client().me()
```

## 템플릿 폴더 (1.6.0)

기업 계정의 발송용 API 키와 `apiVersion=v2` 설정으로 사용하는 서버 전용 API입니다.
폴더는 알림톡·브랜드메시지가 공유하며, 목록의 `templateType`은 `notice` 또는 `brand`입니다.
목록은 `data.folders` 트리와 `total`, `uncategorised` 개수를 반환합니다.
`templateCount`는 하위 폴더를 제외한 해당 폴더의 템플릿 수입니다.

- 생성: `name`, 선택 `parentUuid`. 최대 5단계이며 같은 부모 아래 이름 중복은 409입니다.
- 이동: 동일 발신프로필의 `templateCodes` 1~100개. `folderUuid`는 필수이며 `null`이면 미분류로 이동합니다.
- 템플릿 목록: `folderUuid=none`은 미분류, UUID는 해당 폴더, 생략은 전체입니다.
- 템플릿 등록: 선택 필드 `folderUuid`로 폴더를 지정합니다. 기존 템플릿 수정 API 대신 폴더 이동 API를 사용하세요.

승인되지 않은 키의 `403 ACCESS_KEY_NOT_APPROVED`는 토큰 재발급·재시도 없이 반환합니다.
계정 API의 `autoApprove`는 서버 설정의 실제 승인 정책을 나타냅니다.

```python
from sendgo_django import client
client.template_folders.list(template_type="notice")
```

코어 1.6.0 이상이 필요합니다. 전체 메서드는 [코어 문서](https://github.com/send-go/python#템플릿-폴더-150)를 참고하세요.

## 1.6 이메일 API와 브랜드 타기팅

이메일은 서버 전용이며 클라이언트 설정에서 API 버전을 `v2`로 지정합니다.
브랜드 타기팅은 `M`(친구+비친구), `N`(비친구), `I`(친구교집합),
`O`(친구만), `F`(동보)를 지원합니다. `O`는 SDK에서 바꾸지 않고 서버로 전달합니다.

이메일 발송·견적·조회·취소, 발신자·도메인 인증, 자격증명, 수신함·원본 EML,
템플릿·주소록·연락처·발신자 프로필·캠페인 API를 지원합니다.
일반 API는 기존 앱 Bearer 인증을 사용합니다. `EmailService`의
`withCredentials` / `with_credentials` / `WithCredentials` / Go `NewEmailWithCredentials`는
별도로 발급된 이메일 credential ID/password를 사용하며 `/api/v2/email-service`로 호출합니다.
이 인증은 auth, 발송·견적·조회·취소와 도메인 API에만 사용할 수 있습니다.
내부 email-gateway, 공개 서명 수신거부 URL은 SDK 관리 API가 아닙니다.

단건 `to`는 이메일 주소 하나입니다. `send`에는 `idempotency_key`를 반드시 지정하고
같은 발송의 재시도에는 같은 키를 재사용하세요. 캠페인 발송에는 견적 응답의
`quote_hash`와 `idempotency_key`가 필요합니다. SDK가 키를 임의 생성하거나
네트워크 오류·429·5xx를 자동 재시도하지 않습니다. Bearer 401만 최대 한 번
갱신하며, 이메일 권한 거부 403 및 Basic 인증 실패는 그대로 반환합니다.
마케팅 발송에는 `sender_name`, `sender_address`, `sender_contact`도 필요합니다.
첨부는 `attachments: [{name, type, content}]`이며 content는 base64입니다.

응답은 서버 JSON 객체 또는 배열을 그대로 반환하며 204는 null/nil/None입니다.
원본 EML은 바이트(PHP/Ruby는 바이트 문자열)로 반환합니다. Java/Go/.NET/Dart는
여러 응답 형태를 담는 Object/any/object/dynamic을 사용합니다(.NET JSON은 JsonElement).
모든 관리 요청 본문은 서버 필드명(snake_case)을 그대로 사용합니다.

접근 방법: `get_client().email`. 코어 최소 버전은 1.6.0입니다.
