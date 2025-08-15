# BeMoreLog Backend

만다라트 + 해빗트랙커 웹 애플리케이션을 위한 백엔드 API 서버

## 🎯 프로젝트 개요

BeMoreLog는 만다라트 차트를 활용한 목표 설정과 해빗트랙커를 결합한 웹 애플리케이션입니다. 사용자가 장기 목표를 설정하고, 이를 단계별로 나누어 추적하며, 일상적인 습관을 형성할 수 있도록 도와줍니다.

## 🏗️ 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (개발) / PostgreSQL (운영)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Validation**: Pydantic
- **Testing**: pytest

## 📋 백엔드 기능 요구사항

### 1. 사용자 관리 (User Management)
- [ ] 사용자 회원가입/로그인
- [ ] JWT 기반 인증
- [ ] 사용자 프로필 관리
- [ ] 비밀번호 재설정

### 2. 만다라트 관리 (Mandala Management)
- [x] Epic 생성/수정/삭제
- [x] Epic 계층 구조 (core_epic_id, depth)
- [x] Epic 상태 관리 (todo, running, completed)
- [x] Epic 간 관계 설정
- [ ] 만다라트 차트 시각화 데이터 제공
- [ ] Epic 진행률 계산

### 3. 해빗트랙커 (Habit Tracker)
- [ ] 습관 정의 및 관리
- [ ] 일일 습관 체크인
- [ ] 습관 연속 달성 기록
- [ ] 습관 통계 및 분석
- [ ] 습관과 Epic 연결

### 4. 목표 추적 (Goal Tracking)
- [ ] 목표 설정 및 관리
- [ ] 목표 진행률 추적
- [ ] 목표 달성 축하 및 리워드
- [ ] 목표 히스토리 관리

### 5. 알림 및 리마인더 (Notifications)
- [ ] 습관 체크인 리마인더
- [ ] 목표 진행 상황 알림
- [ ] 성취 달성 축하 메시지
- [ ] 이메일/푸시 알림

### 6. 데이터 분석 및 리포트 (Analytics)
- [ ] 사용자 활동 통계
- [ ] 습관 형성 패턴 분석
- [ ] 목표 달성 성공률 분석
- [ ] 개인화된 인사이트 제공

### 7. 소셜 기능 (Social Features)
- [ ] 친구 추가 및 팔로우
- [ ] 목표 공유 및 응원
- [ ] 성취 인증 및 공유
- [ ] 커뮤니티 챌린지

## 🗄️ 데이터베이스 스키마

### Epic (에픽)
- [x] 기본 정보 (id, title, description, status)
- [x] 계층 구조 (core_epic_id, depth)
- [x] 시간 정보 (created_at, updated_at)
- [x] 관계 설정 (subs, core_epic)

### EpicRelation (에픽 관계)
- [x] 관계 정의 (core_epic_id, sub_epic_id)
- [x] 위치 정보 (position_row, position_col)
- [x] 깊이 정보 (depth)

### User (사용자)
- [ ] 기본 정보 (id, username, email, password_hash)
- [ ] 프로필 정보 (nickname, avatar, bio)
- [ ] 설정 정보 (timezone, notification_preferences)

### Habit (습관)
- [ ] 습관 정의 (id, user_id, name, description, frequency)
- [ ] 습관 설정 (target_count, reminder_time, category)

### HabitLog (습관 기록)
- [ ] 일일 기록 (id, habit_id, user_id, date, completed)
- [ ] 추가 정보 (notes, mood, duration)

### Goal (목표)
- [ ] 목표 정의 (id, user_id, title, description, target_date)
- [ ] 목표 설정 (priority, category, status)

## ✅ 작업 내용

### Epic 모델 및 API 구현
- [x] Epic SQLAlchemy 모델 생성
- [x] EpicResponse Pydantic 모델 생성
- [x] Epic 관리 API 구현
  - [x] 생성
  - [x] 조회
  - [x] 수정
  - [ ] 삭제
- [x] Epic 계층 구조 relationship 설정
- [x] depth, core_epic_id 필드 추가
- [x] subs 정보 포함한 Epic 조회 구현
- [x] to_epic_response 함수로 안전한 데이터 변환


### 해결된 문제들
- [x] SQLAlchemy relationship 설정 오류 수정
- [x] Epic 조회 시 subs 정보 누락 문제 해결
- [x] depth, core_epic_id 필드 응답에 포함
- [x] self-referential relationship 설정 완료

## 🚧 현재 진행 중인 작업

### Epic Relationship 최적화
- [ ] Epic 조회 시 subs 자동 로딩 최적화
- [ ] Epic 계층 구조 쿼리 성능 개선
- [ ] Epic 상태 변경 시 연관 Epic 업데이트

## 📝 다음 작업 예정

### 1. 사용자 인증 시스템
- [ ] User 모델 생성
- [ ] JWT 인증 구현
- [ ] 로그인/회원가입 API

### 2. 습관 트래킹 시스템
- [ ] Habit 모델 생성
- [ ] HabitLog 모델 생성
- [ ] 습관 체크인 API

### 3. 목표 관리 시스템
- [ ] Goal 모델 생성
- [ ] 목표 진행률 추적 API
- [ ] 목표 달성 체크 API

## 🚀 실행 방법

### 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 데이터베이스 초기화
```bash
./init_db.sh
```

### 서버 실행
```bash
uvicorn app.main:app --reload
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_api/test_epic.py
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
