#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume-forge:简历 HTML → 一页 A4 PDF 导出工具

用法:
  python export_autofit.py A.html B.html [目录...]      # 每个 HTML 导出同名 PDF
  python export_autofit.py --chrome PATH A.html         # 指定 Chrome 可执行文件
  python export_autofit.py --no-zoom A.html             # 不做 zoom 压页(仅导出)

特性(全部来自实战踩坑):
  1. 中文路径 URL 百分号编码——不编码时 Chrome 会把 ERR_FILE_NOT_FOUND 错误页
     打印进 PDF(约 39KB 的"假简历"),且错误页也是 1 页,仅查页数无法发现
  2. 输出先写 ASCII 临时文件再替换,避免目标被 PDF 查看器占用导致写入失败
  3. 独立临时 --user-data-dir(Windows 风格路径),避免吸附已运行的 Chrome(0x5 错误)
  4. 溢出自动压页:向 </style> 前注入 /*AUTO-FIT*/ .resume{zoom:X},
     X 从 0.97 逐级下探到 0.85,直到恰好一页(已有 AUTO-FIT 标记则原位替换)
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ZOOMS = [0.97, 0.95, 0.93, 0.91, 0.89, 0.87, 0.85]
MARKER = '/*AUTO-FIT*/'


def find_chrome(explicit):
    if explicit:
        return explicit
    import os
    if os.environ.get('CHROME_PATH'):
        return os.environ['CHROME_PATH']
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chrome')


def pdf_pages(pdf: Path):
    """无依赖解析 PDF 页数(读取 /Type /Pages ... /Count N)。"""
    b = pdf.read_bytes()
    counts = [int(x) for x in re.findall(rb'/Type\s*/Pages.{0,200}?/Count\s+(\d+)', b, re.S)]
    if counts:
        return max(counts)
    return len(re.findall(rb'/Type\s*/Page\b(?!s)', b))


def export(chrome: str, html: Path, out: Path):
    """无头 Chrome 打印;URL 必须编码;独立临时 user-data-dir。"""
    html = html.resolve()
    out = out.resolve()
    url = 'file:///' + urllib.parse.quote(str(html).replace('\\', '/'))
    with tempfile.TemporaryDirectory() as ud:
        subprocess.run(
            [chrome, '--headless=new', '--disable-gpu', '--no-sandbox',
             '--no-pdf-header-footer', '--virtual-time-budget=15000',
             f'--user-data-dir={ud}',
             f'--print-to-pdf={out}', url],
            capture_output=True, timeout=180)


def set_zoom(html: Path, zoom: float):
    t = html.read_text(encoding='utf-8')
    rule = f'{MARKER} .resume{{zoom:{zoom}}}'
    if MARKER in t:
        t = re.sub(re.escape(MARKER) + r'[^}]*\}', rule, t)
    else:
        if '</style>' not in t:
            return False
        t = t.replace('</style>', '    ' + rule + '\n    </style>', 1)
    html.write_text(t, encoding='utf-8')
    return True


def process(chrome: str, html: Path, use_zoom: bool):
    html = html.resolve()  # 相对路径必须转绝对:Chrome 把相对输出路径解析到自身安装目录
    pdf = html.with_suffix('.pdf')
    tmp = html.parent / '_export_tmp.pdf'
    export(chrome, html, tmp)
    if not tmp.exists():
        print(f'FAIL {html.name}: 导出失败(Chrome 未产出文件)')
        return False
    if pdf_pages(tmp) == 1 or not use_zoom:
        tmp.replace(pdf)
        print(f'OK   {html.name}: {pdf_pages(pdf)} 页 ({pdf.stat().st_size // 1024}KB)')
        return True
    for z in ZOOMS:
        if not set_zoom(html, z):
            break
        export(chrome, html, tmp)
        if tmp.exists() and pdf_pages(tmp) == 1:
            tmp.replace(pdf)
            print(f'OK   {html.name}: zoom={z} 压回 1 页 ({pdf.stat().st_size // 1024}KB)')
            return True
    print(f'FAIL {html.name}: zoom=0.85 仍多页——建议精简内容或收紧行距/页边距')
    tmp.unlink(missing_ok=True)
    return False


def main():
    ap = argparse.ArgumentParser(description='简历 HTML → 一页 A4 PDF(自动压页)')
    ap.add_argument('targets', nargs='+', help='HTML 文件或目录')
    ap.add_argument('--chrome', help='Chrome 可执行文件路径(默认自动探测/CHROME_PATH 环境变量)')
    ap.add_argument('--no-zoom', action='store_true', help='不做 zoom 压页')
    args = ap.parse_args()

    chrome = find_chrome(args.chrome)
    if not chrome:
        sys.exit('未找到 Chrome,请用 --chrome 或设置 CHROME_PATH')
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    htmls = []
    for t in args.targets:
        p = Path(t)
        if p.is_dir():
            htmls += sorted(p.glob('*.html'))
        else:
            htmls.append(p)
    ok = all([process(chrome, h, not args.no_zoom) for h in htmls])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
