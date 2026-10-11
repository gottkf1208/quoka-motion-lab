# 쿼카 모션랩 · AI용 목록 (catalog)

클로드 같은 AI가 모션랩에서 **모션을 골라 쓰기** 위한 폴더입니다. 사람은 사이트(https://gottkf1208.github.io/quoka-motion-lab/)를 쓰면 됩니다.

| 파일 | 내용 |
|---|---|
| `motions.json` | 모든 모션 목록. 모션마다 id·이름·종류·작은 묶음·쓰임새(role)·층(layer)·설명·기본 비율·밝기(tone)·한 바퀴 길이(loop)·고칠 칸(fields)·특징 |
| `sheets/*.jpg` | 작은 묶음별 썸네일 판(이름 + id). **고르기 전에 눈으로 볼 것** |
| `sheets.json` | 어느 판에 어느 id가 있는지 |
| `pick.py` | 찾기·장면별 후보 뽑기 (`python3 catalog/pick.py --help`) |
| `render.py` | 모션 하나(또는 여러 장면)를 mp4·투명 webm·투명 mov로 뽑기 (Playwright + ffmpeg) |

## 받는 법

```bash
git clone --depth 1 https://github.com/gottkf1208/quoka-motion-lab.git
cd quoka-motion-lab
python3 catalog/pick.py roles
```

## motions.json의 칸

- `role`: 쓰임새. 숏폼 자막 · 자막·이름표 · 강조·주석 · 오프닝·타이틀 · 큰 문구(키네틱) · 문구 등장 · 화면 시연 · 알림·대화 · 화면 전환 · 차트·데이터 · 숫자·차트 · 사진 쇼케이스 · 수업·기록(문구류) · 배경 장면 · 히어로 배경 · 첫 문장 · 워드클라우드 · 틀·배경 · UI 조각 · 랜딩 조각 · 스크롤 연출
- `layer`: `overlay` = 투명으로 뽑아 영상 위에 얹는 것(자막·강조) · `full` = 화면 전체 장면 · `web` = 웹페이지 조각(영상에는 잘 안 맞음)
- `ratio`: 처음 만든 비율. 다른 비율로도 돌아가지만 이 비율이 가장 예쁨
- `tone`: 바탕이 `dark`/`light`. 한 작품 안에서는 한쪽으로 맞추는 게 좋음
- `loop`: 한 바퀴 길이(초). 영상 장면 길이의 기본값
- `fields`: 고칠 수 있는 대문자 상수. `{name, label, items:[{key, kind, value}]}` — 바꿀 때는 상수 이름으로 (`{"TITLE": "…", "LINES": ["…", "…"]}`), 배열은 원래 칸 수만큼만
- `fresh`: 새로 다듬은 것(사이트에서 ★)
- `images`(내 사진을 넣는 모션) · `words`(낱말 목록으로 바꾸는 모션) · `mouse` · `scroll` · `once` · `webgl` · `threeui`(외부 원본, 코드 뽑기 안 됨)

## 사이트 안의 손잡이 (브라우저에서)

- `quokaLab.catalog()` → motions.json과 같은 목록
- `await quokaLab.html(id, { set, words, ratio: '9 / 16', font, point: '#rrggbb', bg, transparent, player })` → 그 파일 하나로 돌아가는 HTML (`player: true`면 `window.qmPlayer.seek(초)`로 한 장씩 찍을 수 있음)
- `await quokaLab.code(id, opts)` → 내 페이지에 붙일 코드 조각
- `quokaBasket.load(seed)` · `quokaBasket.get()` · `quokaBasket.waitConfirm(ms)` · `quokaBasket.link()` → 바구니(선생님이 사이트에서 모아 한꺼번에 받기). seed = `{ title, note, by: 'claude', ratio, slots: [{ label, mode, dur, options: [{ id, why, words, set, scrim }] }] }`

## 고를 때 지킬 것 (요약)

1. 장면 구성(훅 → 본문 → 강조·데이터 → 마무리)을 먼저 정하고, 장면마다 쓰임새를 정한다.
2. 장면마다 후보 2~3개를 뽑아 **썸네일 판으로 직접 보고** 고른다.
3. 같은 작은 묶음은 한 작품에 한 번(장면이 8개 넘으면 두 번까지), 같은 종류가 연달아 나오지 않게, 한 종류는 전체의 절반을 넘지 않게.
4. 밝기(tone)·포인트 색·글꼴은 한 작품 안에서 맞춘다. 비율은 작품 비율과 같은 것을 앞세운다.
5. 자막·강조처럼 영상 위에 얹는 것(`overlay`)은 투명으로 뽑고, 장면 전체(`full`)는 배경까지 뽑는다.
6. 색: 흰색·네이비(#1f3460)·버건디(#6e1a2f)·검정·종이색. 오렌지·청록·보라·네온·무지개 금지. 한글이 든 글줄은 한글 글꼴 하나로.
