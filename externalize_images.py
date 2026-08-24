#!/usr/bin/env python3
"""
index.html 안의 모든 base64(data:image) 이미지를 외부 파일로 분리한다.
- 동일 이미지는 해시로 중복 제거(한 파일만 생성)
- HTML/JS 어디에 있든 data URI 문자열을 상대경로로 치환
사용: python3 externalize_images.py <입력 html> <출력 html> <img 출력폴더> <경로 prefix>
"""
import re, sys, base64, hashlib, os

src, dst, imgdir, prefix = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
os.makedirs(imgdir, exist_ok=True)
html = open(src, 'r', encoding='utf-8').read()
before = len(html.encode())

pat = re.compile(r'data:image/([a-zA-Z0-9.+-]+);base64,([A-Za-z0-9+/=]+)')
seen = {}   # hash -> relpath
count = 0
def repl(m):
    global count
    fmt, b64 = m.group(1), m.group(2)
    try:
        data = base64.b64decode(b64)
    except Exception:
        return m.group(0)
    h = hashlib.sha1(data).hexdigest()[:10]
    ext = {'jpeg':'jpg','svg+xml':'svg'}.get(fmt, fmt)
    if h not in seen:
        fn = f'asset-{h}.{ext}'
        open(os.path.join(imgdir, fn), 'wb').write(data)
        seen[h] = f'{prefix}{fn}'
    count += 1
    return seen[h]

html = pat.sub(repl, html)
open(dst, 'w', encoding='utf-8').write(html)
after = len(html.encode())
total_img = sum(os.path.getsize(os.path.join(imgdir,f)) for f in os.listdir(imgdir))
print(f"치환한 data URI: {count}개  |  고유 이미지 파일: {len(seen)}개")
print(f"HTML: {before/1024/1024:.2f} MB -> {after/1024:.0f} KB")
print(f"분리된 이미지 총량: {total_img/1024/1024:.2f} MB (외부, 지연로딩 대상)")
