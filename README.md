# 쿼카 모션랩

눌러서 화면으로 보고, 프롬프트나 코드를 복사해 가는 모션 라이브러리입니다. 쿼카연구회(Q.U.O.K.A) 웹앱과 코드로 만드는 영상에 쓰려고 모았습니다.

- 라이브: https://gottkf1208.github.io/quoka-motion-lab/
- 모션 578종: 카드 쇼케이스(40), 알림·대화, 버튼·입력, 숫자·차트, 글자, 키네틱 타이포, 수업·기록, 영상 소스, 숏폼 자막, 3D·배경
- 정적 페이지 하나(`index.html`)와 `threeui/` 폴더의 HTML 파일들로 이루어져 있습니다.

## 쓰는 법

1. 왼쪽에서 종류를 고르고 썸네일을 누르면 화면과 복사 창이 열립니다.
2. 비율·이미지를 맞추고, 창 오른쪽 "문구"에서 장면의 글자를 고칩니다. "설정"에서 글꼴(눈누 한글 글꼴 24종)과 포인트 색도 바꿀 수 있습니다. 고친 내용은 복사되는 코드에도 들어갑니다.
3. "프롬프트 복사"를 눌러 AI(클로드 코드 등)에게 붙여 넣습니다. 직접 붙일 때는 "코드"나 "HTML 파일"을 복사합니다.

## 영상으로 뽑기

가장 쉬운 방법은 창의 "영상으로 저장" 단추입니다. 고른 비율대로(1:1 1080×1080, 16:9 1920×1080, 4:5 1080×1350, 9:16 1080×1920) 30fps 영상을 브라우저에서 바로 만들어 내려받습니다. 컴퓨터의 크롬·엣지에서 됩니다(소리 없음).

저장 형식은 다섯 가지입니다.

- MP4: 배경까지 담은 영상 (H.264, WebCodecs)
- WebM 투명: VP9 + 알파. 색과 투명도를 VP9로 따로 압축해 WebM 표준 방식(BlockAdditional)으로 짝지어 담습니다
- MOV 투명: PNG 코덱 QuickTime. 프리미어·파이널컷·다빈치 리졸브·애프터이펙트가 알파를 그대로 읽습니다
- PNG 묶음: 투명 PNG 낱장 zip
- GIF 투명: 절반 크기, 15fps, 1비트 투명

투명 형식을 고르면 엔진에 `bg: 'transparent'`가 들어가고(`api.clear`), 미리보기 바탕이 체크무늬로 바뀝니다.

직접 뽑을 때는 아래 방식을 씁니다.
직접 만든 모션은 전부 `t초일 때의 한 장면`을 그리는 함수라서 한 장씩 찍어 mp4로 묶을 수 있습니다.
복사한 코드의 `qmEngine(…)`이 돌려주는 값에 `seek(초)`가 있습니다. CONFIG에 `autoplay: false`를 넣고, Playwright로 프레임마다 `seek(i / 30)`을 부르며 화면을 저장한 뒤 ffmpeg로 묶습니다.

```
ffmpeg -framerate 30 -i frames/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart out.mp4
```

## 출처와 라이선스

- 카드 쇼케이스, UI 모션, 글자, 키네틱 타이포, 수업·기록, 영상 소스, 숏폼 자막, 3D 장면 471종은 이 저장소에서 직접 만든 것입니다.
- `threeui/` 폴더의 107종(버튼, 글자, 배경·3D)은 [ThreeUI Community](https://github.com/MengTo/threeui) 원본입니다. MIT License, Copyright (c) 2026 Meng To. 라이선스 전문은 `threeui/LICENSE`에 있고, 파일마다 맨 위에 저작권 고지와 원본에서 달라진 점을 적어 두었습니다.
- 3D 모션은 [three.js](https://threejs.org) (MIT)를 씁니다.
- 영상 저장은 [mp4-muxer](https://github.com/Vanilagy/mp4-muxer) (MIT), GIF는 [gifenc](https://github.com/mattdesl/gifenc) (MIT)를 저장할 때만 불러 씁니다. WebM·MOV·zip은 직접 짠 코드로 묶습니다.
- 한글 글꼴은 [눈누](https://noonnu.cc)에 있는 무료 글꼴을 jsDelivr(눈누 배포 주소)와 Google Fonts에서 불러옵니다. 한글이 든 글줄은 영문·숫자까지 한글 글꼴 하나로 찍습니다.
  - SIL Open Font License: 페이퍼로지, G마켓 산스, 하다 콘덴스드, 프리텐다드, 원티드 산스, 함렛, 가석체, 검은고딕, 동글, 갈무리, 마루 부리, D2Coding, 학교안심 알림장, 나눔손글씨 펜·붓, 개구쟁이, 동해 독도
  - 제작사 무료 글꼴: 에이투지체, SB 어그로체(샌드박스), 여기어때 잘난체(여기어때), 배민 도현·한나 Pro·주아(우아한형제들), 카페24 써라운드(카페24)
- 영문 글꼴(영문만 있는 글줄): Inter, Instrument Serif, JetBrains Mono, Anton, Archivo (Google Fonts, SIL Open Font License).
- 일부 아이콘은 Solar (CC BY 4.0, 480 Design)입니다.
- "AI 바로 가기"의 아이콘은 각 서비스의 공식 파비콘을 불러와 보여 주는 것이며, 이 저장소에 들어 있지 않습니다.
