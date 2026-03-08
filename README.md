# counsel - 고등학교 상담일지 관리 프로그램

로컬 드라이브(PC)에서 실행하는 **상담일지 저장 및 관리 웹앱**입니다.

## 기능
- 학생 등록/검색
- 상담일지 작성(유형, 내용, 조치/추후계획)
- 학생별 상담이력 조회
- 첨부파일 로컬 저장(`data/uploads`)
- SQLite 로컬 DB 저장(`data/counsel.db`)

## 실행 방법
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 참고
- 첫 실행 시 DB 테이블이 자동 생성됩니다.
- `data/` 폴더는 `.gitignore` 처리되어 실제 상담 데이터가 Git에 올라가지 않습니다.
