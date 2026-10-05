# 쿼카 모션랩

눌러서 화면으로 보고, 프롬프트나 코드를 복사해 가는 모션 라이브러리입니다. 쿼카연구회(Q.U.O.K.A) 웹앱과 코드로 만드는 영상에 쓰려고 모았습니다.

- 라이브: https://gottkf1208.github.io/quoka-motion-lab/
- 모션 284종: 카드 쇼케이스, 알림·대화, 버튼·입력, 숫자·차트, 글자, 키네틱 타이포, 수업·기록, 영상 소스, 3D·배경
- 정적 페이지 하나(`index.html`)와 `threeui/` 폴더의 HTML 파일들로 이루어져 있습니다.

## 쓰는 법

1. 왼쪽에서 종류를 고르고 썸네일을 누르면 화면과 복사 창이 열립니다.
2. 비율·글자·이미지를 맞춥니다.
3. "프롬프트 복사"를 눌러 AI(클로드 코드 등)에게 붙여 넣습니다. 직접 붙일 때는 "코드"나 "HTML 파일"을 복사합니다.

## 영상으로 뽑기

직접 만든 모션은 전부 `t초일 때의 한 장면`을 그리는 함수라서 한 장씩 찍어 mp4로 묶을 수 있습니다.
복사한 코드의 `qmEngine(…)`이 돌려주는 값에 `seek(초)`가 있습니다. CONFIG에 `autoplay: false`를 넣고, Playwright로 프레임마다 `seek(i / 30)`을 부르며 화면을 저장한 뒤 ffmpeg로 묶습니다.

```
ffmpeg -framerate 30 -i frames/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart out.mp4
```

## 출처와 라이선스

- 카드 쇼케이스, UI 모션, 글자, 키네틱 타이포, 수업·기록, 영상 소스, 3D 장면 158종은 이 저장소에서 직접 만든 것입니다.
- `threeui/` 폴더의 126종(버튼, 글자, 배경·3D)은 [ThreeUI Community](https://github.com/MengTo/threeui) 원본입니다. MIT License, Copyright (c) 2026 Meng To. 라이선스 전문은 `threeui/LICENSE`에 있고, 파일마다 맨 위에 저작권 고지와 원본에서 달라진 점을 적어 두었습니다.
- 3D 모션은 [three.js](https://threejs.org) (MIT)를 씁니다.
- 글꼴은 Google Fonts에서 불러옵니다: Inter, Noto Sans KR, Noto Serif KR, Instrument Serif, JetBrains Mono, Anton, Black Han Sans, Archivo (모두 SIL Open Font License).
- 일부 아이콘은 Solar (CC BY 4.0, 480 Design)입니다.
- "AI 바로 가기"의 아이콘은 각 서비스의 공식 파비콘을 불러와 보여 주는 것이며, 이 저장소에 들어 있지 않습니다.
