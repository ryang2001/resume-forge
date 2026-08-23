#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume-forge:PDF 内容级验证(无第三方依赖)

用法:
  python verify_pdf.py A.pdf B.pdf [--min-kb 150]

为什么必须"内容级"验证(2026-08-22 事故):
  Chrome 加载本地 HTML 失败时(如中文路径 URL 未编码),会把
  ERR_FILE_NOT_FOUND 错误页打印成 PDF——错误页同样"恰好 1 页"、同样带字体,
  只查页数/字体会得到"验证通过"的假象。判别标准:
    真实简历: 通常 ≥ min-kb(默认 150;无照片英文版可传 --min-kb 80)且含嵌入图片
    错误页:   恒 ≈ 39KB、无嵌入照片
"""
import argparse
import re
import sys
from pathlib import Path


def check(pdf: Path, min_kb: int):
    b = pdf.read_bytes()
    kb = len(b) // 1024
    counts = [int(x) for x in re.findall(rb'/Type\s*/Pages.{0,200}?/Count\s+(\d+)', b, re.S)]
    pages = max(counts) if counts else len(re.findall(rb'/Type\s*/Page\b(?!s)', b))
    images = len(re.findall(rb'/Subtype\s*/Image', b))
    problems = []
    if pages != 1:
        problems.append(f'页数={pages}(应为 1)')
    if kb < min_kb:
        problems.append(f'体积={kb}KB(< {min_kb}KB,疑似错误页/空白页)')
    if not b.startswith(b'%PDF'):
        problems.append('非 PDF 文件头(可能导出失败)')
    return pages, kb, images, problems


def main():
    ap = argparse.ArgumentParser(description='简历 PDF 内容级验证')
    ap.add_argument('pdfs', nargs='+', type=Path)
    ap.add_argument('--min-kb', type=int, default=150, help='最小体积阈值 KB(默认 150;无照片版建议 80)')
    args = ap.parse_args()
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    bad = 0
    for p in args.pdfs:
        pages, kb, images, problems = check(p, args.min_kb)
        status = 'OK  ' if not problems else 'BAD '
        print(f'{status} {p.name}: {pages} 页 | {kb}KB | 嵌入图片 {images}')
        for pr in problems:
            print(f'      ⚠️ {pr}')
        bad += bool(problems)
    if bad:
        print(f'\n{bad} 个文件未通过(若为错误页:检查 HTML 路径 URL 是否已百分号编码)')
        sys.exit(1)
    print('\n全部通过 ✓')


if __name__ == '__main__':
    main()
