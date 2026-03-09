# counsel - 고등학교 상담일지 관리 프로그램

로컬 드라이브(PC)에서 실행하는 **상담일지 저장 및 관리 웹앱**입니다.

## 주요 기능
- 학생 등록/검색
- 학생 페이지에서 연락처/보호자 정보 수정
- 명렬표 엑셀(.xlsx) 일괄등록(시트 탭 전체 순회, 학년/반/담임 자동 반영)
- 상담일지 작성(유형, 내용, 조치/추후계획)
- 상담유형 추가/수정/삭제 관리
- 작성된 상담일지 수정/삭제
- 상담 예약/일지 작성 시 학년·반 선택 후 학생 필터링
- 학생별 상담이력 조회
- 월간 달력(한 달 전체 날짜 표시) 기반 상담 일정 등록/조회/수정 (교시 선택/직접입력 지원, 상담일지 등록 시 일정 자동 완료)
- 자동 백업(하루 1회) + 수동 백업 생성/다운로드
- 학생별 상담요약 인쇄/PDF 출력(기간 필터 지원)
- 상담 통계(월간/년간) 조회
- 상담일지의 다음 상담일 입력 시 일정 달력에 자동 연동
- ChatGPT 기반 사례개념화 초안 생성(선택 기능, API 키 필요, 학생별 누적 상담일지 종합)
- 학생 페이지에서 사례개념화 저장/재열람
- 첨부파일 로컬 저장(`data/uploads`)
- SQLite 로컬 DB 저장(`data/counsel.db`)

---

## 가장 쉬운 실행 방법

### macOS / Linux
```bash
./scripts/run.sh
```

### Windows
```bat
scripts\run.bat
```

위 스크립트가 자동으로 아래를 처리합니다.
1. 가상환경 생성 (`.venv`)
2. 의존성 설치
3. DB 초기화 확인
4. 서버 실행 (`http://localhost:5000`)
5. (Windows `run.bat`) 기본 브라우저 자동 열기

---


### Windows에서 VS Code 터미널 실행 팁
- **프로젝트 루트 폴더**(`...\counsel`)에서 `scripts\run.bat` 를 실행하세요.
- 경로 인식 오류가 나면 아래처럼 현재 위치를 먼저 확인하세요.
```bat
cd
dir
```
- PowerShell에서 실행 중이면 아래처럼 호출해도 됩니다.
```powershell
cmd /c scripts\run.bat
```

- `scripts` 폴더에서 직접 실행해도 동작하도록 `run.bat`가 루트 경로를 자동 계산합니다.
- 실행 중 오류가 나면 창이 바로 닫히지 않고, 오류 메시지를 확인할 수 있도록 일시정지됩니다.
- 바로 꺼지면 `cmd /k scripts\run.bat` 로 실행하면 오류 로그를 유지한 채 확인할 수 있습니다.
- `TemplateNotFound: index.html` 오류가 나오면, **압축을 풀 때 폴더 구조가 유지되었는지** 확인하세요.  
  `templates/index.html`, `templates/base.html`, `static/style.css` 파일이 프로젝트 내부에 있어야 합니다.

- 아래 명령으로 템플릿 파일 존재를 빠르게 확인할 수 있습니다.
```bat
dir templates
```

- **중요:** 오류 화면의 경로가 `...\templates\app.py`처럼 나오면, 잘못된 위치의 `app.py`를 실행한 것입니다.  
  반드시 `c:\프로젝트폴더\app.py` 형태(루트)에 있어야 하며, `templates` 폴더 안에 `app.py`가 있으면 안 됩니다.

## AI 사례개념화 보조 사용법 (선택)

학생 상세 화면(`students/<id>`)에서 **사례개념화 초안 생성** 버튼을 사용할 수 있습니다.

1. OpenAI API 키를 환경변수로 설정
   - macOS/Linux
   ```bash
   export OPENAI_API_KEY="여기에_키"
   export OPENAI_MODEL="gpt-4.1-mini"   # 선택(미설정 시 기본값 사용)
   ```
   - Windows(CMD)
   ```bat
   set OPENAI_API_KEY=여기에_키
   set OPENAI_MODEL=gpt-4.1-mini
   ```
2. `scripts/run.sh` 또는 `scripts\run.bat`로 앱 실행
3. 상단 메뉴의 `AI 설정`에서 API 키를 등록(또는 환경변수 사용)
4. `AI 키 활성화 테스트` 버튼으로 키 활성화 여부 확인
5. 학생 상세 페이지에서 사례개념화 초안 생성

> 웹앱 저장 키는 로컬 SQLite(`app_settings`)에 저장됩니다. 공용 PC에서는 사용을 권장하지 않습니다.
> 개인정보 보호를 위해 앱에서 일부 패턴(전화번호/숫자정보/호칭 포함 이름)을 마스킹해 전송합니다.
> 생성 결과는 반드시 상담교사가 검토/수정 후 사용하세요.

---

## 수동 실행 방법
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## 개발 편의 명령(Makefile)
```bash
make setup   # venv + 의존성 설치
make run     # DB 확인 후 실행
```

---

## 참고
- 첫 실행 시 DB 테이블이 자동 생성됩니다.
- `data/` 폴더는 `.gitignore` 처리되어 실제 상담 데이터가 Git에 올라가지 않습니다.
