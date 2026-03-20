# counselog - 고등학교 카운슬로그 프로그램

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
- 자동 백업(하루 1회) + 수동 백업 생성/다운로드 (백업 암호 설정 시 자동백업도 암호화)
- 학생별 상담요약 인쇄/PDF 출력(기간 필터 지원)
- 상담 통계(월간/년간) 조회 + 나이스 월간 업로드 양식 엑셀 내보내기/불러오기
- 상담일지의 다음 상담일 입력 시 일정 달력에 자동 연동
- 상담일지 확인 페이지 20건 단위 페이지네이션
- 잠금화면에서 담임교사 페이지 접속(초기 비밀번호 1234, 첫 로그인 후 즉시 변경)
- 담임교사 페이지에서 자기 반 미인정결석 등록/복귀처리/상담의뢰서 제출 + 상담교사 알림 연동
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
처음 사용자(파이썬 미설치 가능성)라면 아래를 먼저 실행하세요.
```bat
scripts\first_run_windows.bat
```

이미 파이썬이 설치되어 있다면 기존처럼 아래만 실행해도 됩니다.
```bat
scripts\run.bat
```

Windows에서 트레이(시계 옆 아이콘)로 실행하고 싶다면 아래를 사용하세요.
```bat
scripts\run_tray.bat
```

위 스크립트가 자동으로 아래를 처리합니다.
1. 가상환경 생성 (`.venv`)
2. 의존성 설치
3. DB 초기화 확인
4. 서버 실행 (`http://localhost:5000`)
5. (Windows `run.bat`) 기본 브라우저 자동 열기

`run_tray.bat`은 콘솔창 대신 트레이 아이콘으로 실행되며, 아이콘 우클릭으로 브라우저 열기/종료를 선택할 수 있습니다.
트레이 실행 중 서버가 중간 종료되면 `data/run_tray.log`에 원인이 기록됩니다.

---

## Google Form 연동 (Pull 방식)

`localhost` 환경에서는 Pull 방식으로 Google Form 응답을 가져와 상담신청 알림을 만들 수 있습니다.

1. Google Form 응답이 쌓이는 Google Sheets를 열고 `파일 > 공유 > 웹에 게시`에서 CSV 링크를 생성합니다.
2. 앱 `설정 > 학교 설정`의 **Google Form 연동(Pull)** 영역에 CSV URL을 저장합니다.
   - 권장 Form 문항(컬럼명): `이름, 학년, 반, 상담희망일, 상담희망시간, 상담내용` (+ 선택: `학번, 전화번호, 상담제목`)
3. 같은 화면에서 자동 동기화 사용 여부와 간격(분)을 저장합니다. 자동 사용 시 설정된 간격마다 백그라운드 동기화가 실행됩니다.
4. 즉시 반영이 필요하면 `지금 Pull 동기화 실행` 버튼을 눌러 수동 동기화할 수 있습니다.
5. 상단 `알림` 메뉴에서 항목을 열면 상담 일정 등록 화면으로 이동하고, 신청 내용이 자동 입력됩니다.

> 자동 동기화는 앱 요청이 발생할 때 간격 조건을 확인해 실행됩니다.

---


### Windows 게시자(Publisher) 표시 안내
- `run.bat`를 직접 실행할 때 뜨는 **파일 열기 보안 경고**는 배치 파일 특성상 게시자 정보를 넣을 수 없습니다.
- 게시자 이름(예: `전문상담교사 박재현`)을 보이게 하려면, 실행 파일(`.exe`/설치파일)에 **코드 서명(디지털 인증서)** 이 필요합니다.
- 본 프로젝트는 설치 메타데이터 게시자를 `전문상담교사 박재현`으로 설정해 두었고, 아래 환경변수로 서명도 자동화할 수 있습니다.

```bat
set SIGN_PFX=C:\path\to\publisher_cert.pfx
set SIGN_PFX_PASSWORD=인증서암호
scripts\build_setup_windows.bat
```

> 서명 인증서가 없으면 Windows에는 계속 `알 수 없는 게시자`로 표시됩니다.

### Windows에서 VS Code 터미널 실행 팁
- **프로젝트 루트 폴더**(`...\counselog`)에서 `scripts\run.bat` 를 실행하세요.
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



### 아이콘 적용(웹/실행파일/설치파일)

원하는 아이콘을 다음 경로에 두면 자동으로 반영됩니다.

- `assets/counselog.ico`: Windows EXE / Setup 아이콘
- `static/counselog.ico` (또는 `static/favicon.ico`): 웹 브라우저 탭 파비콘 + 트레이 아이콘
- `static/logo.png` (또는 `logo.svg`, `logo.webp`, `logo.jpg`, `logo.jpeg`): 웹사이트 상단 헤더 로고

`build_setup_windows.bat` 실행 시 `assets/counselog.ico`가 있으면 자동으로 PyInstaller `--icon` 옵션을 사용합니다.

## Windows 설치 파일(Setup.exe) 만들기
Windows 사용자 배포가 필요하면 설치 파일도 만들 수 있습니다.

1. (권장) Inno Setup 6 설치: https://jrsoftware.org/isinfo.php
2. 아래 스크립트 실행:
```bat
scripts\build_setup_windows.bat
```

스크립트가 자동으로 수행하는 작업:
- `.venv` 확인(없으면 실행 환경 부트스트랩)
- `pyinstaller` 설치
- 실행 파일 폴더 빌드 (`dist\counselog`)
- Inno Setup이 설치된 경우 설치 파일 생성 (`dist\counselog_setup.exe`)

`build_setup_windows.bat`는 빌드 중 웹앱 서버를 띄우지 않고, 빌드용 가상환경만 생성해 바로 패키징을 진행합니다.

> 설치본에서도 한국 공휴일 자동 계산(대체공휴일 포함)이 유지되도록 `holidays` 모듈을 PyInstaller에 함께 포함합니다.

앱 홈의 **자동 백업 관리**에서 아래 작업을 할 수 있습니다.
- `지금 백업 생성`: 현재 DB/첨부파일을 ZIP으로 저장
- `백업 복원`: 기존 백업 ZIP 업로드 후 데이터 복원 (복원 전 상태는 `pre_restore` 백업으로 자동 보관)
  - 암호화된 `.zip.enc`는 복원 폼의 **백업 암호** 입력란에 암호를 직접 넣거나, 기존 설정 암호를 사용해 복원할 수 있습니다.
- 백업 파일은 최신 10개만 유지되고, 오래된 파일은 자동 삭제됩니다.

백업 해독을 어렵게 하려면 실행 전에 환경변수 `COUNSELOG_BACKUP_PASSPHRASE`를 설정하세요.
- 설정 시 백업은 일반 `.zip` 대신 암호화된 `.zip.enc`로 저장됩니다. (설정 > 백업 암호화 탭 또는 환경변수)
- 복원 시에도 같은 환경변수 값을 유지해야 복원할 수 있습니다.
- 암호를 잊어버리면 복원이 불가능하므로 안전한 위치(비밀번호 관리자 등)에 보관해 주세요.

설정 > 임시공휴일 설정에서 연도를 지정해 **대한민국 공휴일(대체공휴일 포함) 불러오기**를 실행할 수 있습니다.

> Inno Setup이 없는 경우에도 `dist\counselog` 폴더로 포터블 실행은 가능합니다.

설치본(`Program Files\counselog`)에서 실행할 때 사용자 데이터(DB/첨부/백업)는 쓰기 권한이 있는 아래 경로를 사용합니다.
- `%LOCALAPPDATA%\counselog\data`

원하면 실행 전에 환경변수 `COUNSELOG_DATA_DIR`로 데이터 폴더를 직접 지정할 수 있습니다.

설치본 `counselog.exe` 실행 시에는 기본적으로 브라우저가 자동으로 `http://localhost:5000`을 엽니다.
- 자동 열기를 끄려면: `COUNSELOG_OPEN_BROWSER=0`
- 시작 URL을 바꾸려면: `COUNSELOG_START_URL=http://localhost:5000`

---

## AI 사례개념화 보조 사용법 (선택)

학생 상세 화면(`students/<id>`)에서 **사례개념화 초안 생성** 버튼을 사용할 수 있습니다.

1. OpenAI 또는 Gemini 키를 준비
   - OpenAI (macOS/Linux)
   ```bash
   export OPENAI_API_KEY="여기에_키"
   export OPENAI_MODEL="gpt-4.1-mini"   # 선택(미설정 시 기본값 사용)
   ```
   - Gemini (macOS/Linux)
   ```bash
   export GEMINI_API_KEY="여기에_키"
   export GEMINI_MODEL="gemini-2.0-flash"   # 선택(미설정 시 자동 fallback)
   ```
   - Windows(CMD)
   ```bat
   set OPENAI_API_KEY=여기에_키
   set OPENAI_MODEL=gpt-4.1-mini
   set GEMINI_API_KEY=여기에_키
   set GEMINI_MODEL=gemini-2.0-flash
   ```
2. `scripts/run.sh` 또는 `scripts\run.bat`로 앱 실행
3. 상단 메뉴의 `AI 설정`에서 기본 제공자(OpenAI/Gemini)와 API 키를 등록(또는 환경변수 사용)
4. `AI 키 활성화 테스트` 버튼으로 선택된 제공자의 키 활성화 여부 확인
5. 학생 상세 페이지에서 사례개념화 이론 기반(통합/CBT/해결중심 등)을 선택 후 초안 생성

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
