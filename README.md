# counsel - 고등학교 상담일지 관리 프로그램

로컬 드라이브(PC)에서 실행하는 **상담일지 저장 및 관리 웹앱**입니다.

## 주요 기능
- 학생 등록/검색
- 상담일지 작성(유형, 내용, 조치/추후계획)
- 학생별 상담이력 조회
- 달력 기반 상담 일정 등록/조회/완료처리
- 자동 백업(하루 1회) + 수동 백업 생성/다운로드
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
