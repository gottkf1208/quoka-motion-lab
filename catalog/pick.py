#!/usr/bin/env python3
"""쿼카 모션랩 목록(catalog/motions.json)에서 모션을 찾고, 장면 구성에 맞춰 '골고루' 후보를 뽑는 도구.

  python3 catalog/pick.py roles                          # 쓰임새(역할) 목록과 개수
  python3 catalog/pick.py list --role 숏폼 자막 --ratio 9:16 --tone dark
  python3 catalog/pick.py list --q 타이핑                  # 이름·설명에서 찾기
  python3 catalog/pick.py show sf-travel-box              # 한 모션의 설명·고칠 칸·썸네일 판
  python3 catalog/pick.py plan "훅,자막,강조,데이터,전환,엔딩" --ratio 9:16 --tone dark --k 3
      → 장면마다 후보 k개. 같은 작은 묶음·같은 모션이 겹치지 않게, 새로 다듬은 것(★)을 조금 앞세워 뽑습니다.
      --avoid id,id  (최근에 쓴 것 빼기)   --seed 7 (같은 결과 다시 보기)   --layer overlay|full
"""
import argparse, json, os, random, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))

# 장면 낱말 → 찾아볼 쓰임새(역할)와 거르는 말. 역할 이름은 motions.json의 role 값
BEATS = {
    '훅': (['오프닝·타이틀', '큰 문구(키네틱)', '첫 문장', '숏폼 자막'], r'훅|첫|시작|오프닝|쾅|질문|타이틀|제목'),
    '오프닝': (['오프닝·타이틀', '큰 문구(키네틱)', '첫 문장', '히어로 배경'], ''),
    '타이틀': (['오프닝·타이틀', '큰 문구(키네틱)', '첫 문장'], ''),
    '자막': (['숏폼 자막', '자막·이름표'], ''),
    '이름표': (['자막·이름표'], r'이름|화자|발표|소개'),
    '강조': (['강조·주석', '문구 등장', '큰 문구(키네틱)'], ''),
    '문구': (['문구 등장', '큰 문구(키네틱)'], ''),
    '인용': (['문구 등장', '오프닝·타이틀', '수업·기록(문구류)'], r'인용|말|문장|따옴'),
    '데이터': (['차트·데이터', '숫자·차트'], ''),
    '숫자': (['숫자·차트', '차트·데이터'], r'숫자|세|카운트|굴러'),
    '목록': (['차트·데이터', '수업·기록(문구류)', '숏폼 자막'], r'목록|순서|단계|체크|표|리스트'),
    '시연': (['화면 시연', '알림·대화'], ''),
    '대화': (['알림·대화'], ''),
    '사진': (['사진 쇼케이스'], ''),
    '전환': (['화면 전환'], ''),
    '배경': (['배경 장면', '히어로 배경', '틀·배경'], ''),
    '수업': (['수업·기록(문구류)'], ''),
    '엔딩': (['오프닝·타이틀', '큰 문구(키네틱)', '첫 문장'], r'끝|엔딩|마무리|구독|다음|end|CTA|단추'),
    'CTA': (['오프닝·타이틀', 'UI 조각', '첫 문장'], r'단추|버튼|구독|신청|시작|함께'),
}

def load():
    path = os.path.join(HERE, 'motions.json')
    if not os.path.exists(path):
        sys.exit('motions.json이 없어요. 저장소 catalog/ 폴더에서 실행하세요.')
    data = json.load(open(path, encoding='utf-8'))
    sheets = {}
    sp = os.path.join(HERE, 'sheets.json')
    if os.path.exists(sp):
        for s in json.load(open(sp, encoding='utf-8')):
            for i in s['ids']: sheets[i] = s['file']
    return data['motions'], sheets

def norm_ratio(r):
    if not r: return ''
    r = r.replace(' ', '').replace(':', '/')
    return {'9/16': '9 / 16', '16/9': '16 / 9', '1/1': '1 / 1', '4/5': '4 / 5'}.get(r, r)

def fields_short(m):
    out = []
    for g in m['fields']:
        if g['name'] == 'LOOP': continue
        n = len(g['items'])
        out.append(g['name'] + (f'×{n}' if n > 1 else ''))
    return ' '.join(out)

def row(m, sheets):
    star = '★' if m['fresh'] else ' '
    return f"{star} {m['id']:<28} {m['ko']:<12} {m['catKo']}›{m['subKo'] or '-':<8} {m['role']:<10} {m['layer']:<7} {m['ratio'].replace(' ', ''):<5} {m['tone']:<5} {m['loop']:>4}s  [{fields_short(m)}]  {sheets.get(m['id'], '')}"

def matches(m, a):
    if a.cat and m['cat'] != a.cat and m['catKo'] != a.cat: return False
    if a.role and a.role not in m['role']: return False
    if a.layer and m['layer'] != a.layer: return False
    if a.tone and m['tone'] != a.tone: return False
    if getattr(a, 'no_threeui', True) and m['threeui']: return False
    if a.q and not re.search(a.q, m['ko'] + ' ' + m['en'] + ' ' + m['desc'] + ' ' + m['subKo'], re.I): return False
    return True

def cmd_roles(ms, sheets, a):
    from collections import Counter
    c = Counter((m['role'], m['layer']) for m in ms if not m['threeui'])
    for (r, l), n in sorted(c.items(), key=lambda x: -x[1]): print(f'{r:<14} {l:<8} {n}')
    print('\n장면 낱말(plan에 쓰는 말):', ', '.join(BEATS))

def cmd_list(ms, sheets, a):
    got = [m for m in ms if matches(m, a)]
    r = norm_ratio(a.ratio)
    if r: got.sort(key=lambda m: (m['ratio'] != r,))
    for m in got[:a.n]: print(row(m, sheets))
    print(f'\n{len(got)}개 중 {min(len(got), a.n)}개. ★ = 새로 다듬은 것. 마지막 칸 = 눈으로 볼 썸네일 판(catalog/ 기준)')

def cmd_show(ms, sheets, a):
    m = next((x for x in ms if x['id'] == a.id), None)
    if not m: sys.exit('없는 id: ' + a.id)
    print(row(m, sheets)); print('\n' + m['desc'])
    print(f"\n비율 {m['ratio']} · 바탕 {m['bg']} ({m['tone']}) · 한 바퀴 {m['loop']}초 · 썸네일 순간 {m['at']}초 · 글꼴 {', '.join(m['fonts']) or '-'}")
    flags = [k for k in ('images', 'words', 'mouse', 'scroll', 'once', 'webgl') if m[k]]
    if flags: print('특징:', ', '.join(flags))
    print('\n고칠 칸 (render.py --set / quokaLab.html의 set에 상수 이름으로):')
    for g in m['fields']:
        vals = [it['value'] for it in g['items']]
        print(f"  {g['name']:<12} {g['label'] or ''}  = {json.dumps(vals if len(vals) > 1 else vals[0], ensure_ascii=False)}")

def cmd_plan(ms, sheets, a):
    beats = [b.strip() for b in re.split(r'[,\n]', a.beats) if b.strip()]
    r = norm_ratio(a.ratio)
    avoid = set(x for x in (a.avoid or '').split(',') if x)
    rnd = random.Random(a.seed if a.seed is not None else int(time.time()))
    used_subs, used_cats, used_ids = [], [], set()
    pool = [m for m in ms if not m['threeui'] and m['layer'] != 'web' or m['role'] in ('히어로 배경', '첫 문장')]
    print(f'장면 {len(beats)}개 · 비율 {r or "자유"} · 톤 {a.tone or "자유"}' + (f' · 층 {a.layer}' if a.layer else '') + '\n')
    for i, b in enumerate(beats):
        key = next((k for k in BEATS if k in b), None)
        roles, kw = BEATS[key] if key else ([], b)
        def score(m):
            s = 0.0
            if roles and m['role'] in roles: s += 3 - roles.index(m['role']) * 0.4
            elif roles: return -99
            if kw and re.search(kw, m['ko'] + ' ' + m['desc']): s += 1.2
            if not roles and not (kw and re.search(kw, m['ko'] + ' ' + m['desc'] + ' ' + m['role'])): return -99
            if r: s += 1.0 if m['ratio'] == r else 0
            if a.tone: s += 0.8 if m['tone'] == a.tone else -0.6
            if a.layer and m['layer'] != a.layer: s -= 2
            if m['fresh']: s += 0.6
            if m['sub'] and (m['cat'], m['sub']) in used_subs: s -= 2.5            # 같은 작은 묶음은 한 번만
            if used_cats[-1:] == [m['cat']]: s -= 1.2                               # 바로 앞 장면과 같은 종류 피하기
            s -= 0.5 * used_cats.count(m['cat'])
            if m['id'] in used_ids or m['id'] in avoid: return -99
            return s + rnd.random() * 1.6                                          # 매번 같은 것만 나오지 않게
        cands = sorted((m for m in pool), key=score, reverse=True)
        cands = [m for m in cands if score(m) > -50]
        picks, seen_sub = [], set()
        for m in cands:
            k = (m['cat'], m['sub'])
            if k in seen_sub: continue
            picks.append(m); seen_sub.add(k)
            if len(picks) >= a.k: break
        for m in cands:                                                            # 작은 묶음이 모자라면 같은 묶음에서 채움
            if len(picks) >= a.k: break
            if m not in picks: picks.append(m)
        print(f'[{i + 1}] {b}')
        for m in picks: print('   ' + row(m, sheets))
        if not picks: print('   (맞는 후보 없음: 장면 낱말을 바꿔 보세요)')
        else:
            top = picks[0]; used_ids.add(top['id']); used_subs.append((top['cat'], top['sub'])); used_cats.append(top['cat'])
        print()
    print('맨 위 후보를 기본으로 골라 겹치지 않게 다음 장면을 뽑았어요. 썸네일 판을 눈으로 보고 바꿔도 됩니다.')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd')
    sp.add_parser('roles')
    l = sp.add_parser('list')
    for p in (l,):
        p.add_argument('--cat'); p.add_argument('--role'); p.add_argument('--layer'); p.add_argument('--tone', choices=['dark', 'light'])
        p.add_argument('--ratio'); p.add_argument('--q'); p.add_argument('-n', type=int, default=40)
    s = sp.add_parser('show'); s.add_argument('id')
    pl = sp.add_parser('plan'); pl.add_argument('beats'); pl.add_argument('--ratio'); pl.add_argument('--tone', choices=['dark', 'light'])
    pl.add_argument('--layer', choices=['overlay', 'full']); pl.add_argument('--k', type=int, default=3); pl.add_argument('--avoid'); pl.add_argument('--seed', type=int)
    a = ap.parse_args()
    ms, sheets = load()
    if a.cmd == 'list': cmd_list(ms, sheets, a)
    elif a.cmd == 'show': cmd_show(ms, sheets, a)
    elif a.cmd == 'plan': cmd_plan(ms, sheets, a)
    elif a.cmd == 'roles': cmd_roles(ms, sheets, a)
    else: ap.print_help()

if __name__ == '__main__':
    main()
