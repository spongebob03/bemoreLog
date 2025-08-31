# BeMoreLog Product

만다라트 + 해빗트랙커 웹 애플리케이션

## 🎯 프로젝트 개요

BeMoreLog는 만다라트 차트를 활용한 목표 설정과 해빗트랙커를 결합한 웹 애플리케이션입니다. 사용자가 장기 목표를 설정하고, 이를 단계별로 나누어 추적하며, 일상적인 습관을 형성할 수 있도록 도와줍니다.

## 🏗️ 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite (개발) / PostgreSQL (운영)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Validation**: Pydantic

## 필수 기능
### 만다라트 구현
- [x] Epic(핵심목표/세부목표) CRUD
	- [x] 핵심목표 추가/조회/수정/삭제
	- [x] 세부목표 추가/조회/수정/삭제
    - [x] 실천목표 추가/조회/수정/삭제
    - [x] Epic 계층 구조 (core_epic_id, depth)
### habit-tracker 구현
- [ ] commit CRUD
	- [x] 추가
	- [x] 조회
	- [ ] 수정
	- [ ] 삭제

## 부가 기능
- [x] 실천 시각화
  - [x] 잔디 뷰
  - [x] 칭찬 스티커 - 포도송이 뷰
- [ ] 목표 진행률 트랙킹
- [ ] 목표 달성 축하 및 리워드
- [ ] 다중 사용자 지원
    - [ ] 사용자 회원가입/로그인
    - [ ] JWT 기반 인증
    - [ ] 사용자 프로필 관리
    - [ ] 비밀번호 재설정
- [ ] 소셜 기능
    - [ ] 친구 추가 및 팔로우
    - [ ] 목표 공유 및 응원
    - [ ] 성취 인증 및 공유
- [ ] 알림 및 리마인더
    - [ ] 습관 체크인 리마인더
    - [ ] 목표 진행 상황 알림
    - [ ] 이메일/푸시 알림
- [ ] 데이터 분석 및 리포트
    - [ ] 목표 관리, 실천 관리 요청시 로그 추가
    - [ ] 사용자 활동 통계
    - [ ] 습관 형성 패턴 분석
    - [ ] 목표 달성 성공률 분석

## 구현 작업 기록

### 해결된 문제들
- [x] SQLAlchemy relationship 설정 오류 수정
- [x] Epic 조회 시 subs 정보 누락 문제 해결
- [x] depth, core_epic_id 필드 응답에 포함
- [x] self-referential relationship 설정 완료


## Backend Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

