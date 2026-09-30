#!/usr/bin/env python3
"""Render ilya_fomin_cv.md to build/ilya_fomin_cv.pdf.

Two ways in, one way out. Both produce the pandoc-goodies GitHub.html5 page, pass it through
`finish()` below (the print CSS and the page-break blocks — the only place they live), and
print it with headless Chrome:

  render.py               on this Mac: GitHub's own /markdown API renders the GFM (it is the
                          renderer the repo page uses, and the resume is public anyway);
                          needs `gh` logged in and Google Chrome.
  render.py --finish IN OUT
                          in Cloud Build (cloudbuild.yaml): pandoc has already rendered the
                          page with the template; this step only finishes it, and a Chrome
                          container prints it.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
NAME = "ilya_fomin_cv"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BUILD = ROOT / "build"

# ZOOM is the largest value that still prints on two Letter pages; re-tune it when the text
# changes noticeably (page count printed below).
ZOOM = 0.71


def finish(html):
    """The print CSS and the page-break blocks, applied to a full GitHub.html5 page."""
    # Each role (a paragraph starting with its dates) and each section heading with what
    # follows it becomes one block that never splits across pages, so a page break falls
    # between roles. Only the article body is wrapped; pandoc and the /markdown API both put
    # it inside <article class="markdown-body">.
    head, article, tail = re.split(r"(?<=<article class=\"markdown-body\">)|(?=</article>)", html)
    article = "".join(f'<div class="block">{chunk}</div>'
                      for chunk in re.split(r"(?=<h4)|(?=<p>\d\d/\d{4})", article) if chunk.strip())
    html = head + article + tail
    # The template pads the article by 45px on every side; the @page margin already frames the
    # page, so the padding goes and the margin takes its place.
    return html.replace("</head>", "<style>@page { size: Letter; margin: 12mm 18mm; } html { zoom: %s; }"
                        " .markdown-body { padding: 0 !important; }"
                        " .block { break-inside: avoid; } h4 { break-after: avoid; }</style></head>" % ZOOM)


def pages(pdf):
    return len(re.findall(rb"/Type\s*/Page[^s]", pathlib.Path(pdf).read_bytes()))


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def local():
    BUILD.mkdir(exist_ok=True)
    template = gh("api", "repos/tajmone/pandoc-goodies/contents/templates/html5/github/GitHub.html5",
                  "-H", "Accept: application/vnd.github.raw")
    # Keep only what pandoc would emit with no metadata: drop $if…$endif$ / $for…$endfor$ blocks
    # (none of them hold the CSS or $body$), then the remaining $var$ placeholders.
    template = re.sub(r"\$--.*", "", template)  # pandoc comments run to the end of the line
    # Blocks nest ($if(subtitle)$ inside $if(title)$), so strip innermost-first until none are left.
    innermost = re.compile(r"\$(if|for)\([^)]*\)\$(?:(?!\$(?:if|for)\().)*?\$end\1\$", re.S)
    while innermost.search(template):
        template = innermost.sub("", template)
    body = gh("api", "/markdown", "-f", f"text={(ROOT / f'{NAME}.md').read_text()}", "-f", "mode=gfm")
    html = re.sub(r"\$[a-z-]+\$", "", template.replace("$body$", body))
    page = BUILD / f"{NAME}.html"
    page.write_text(finish(html))
    pdf = BUILD / f"{NAME}.pdf"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True)
    print(pdf, "pages:", pages(pdf))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--finish"]:
        src, dst = sys.argv[2:4]
        pathlib.Path(dst).write_text(finish(pathlib.Path(src).read_text()))
    elif sys.argv[1:2] == ["--pages"]:
        print(pages(sys.argv[2]))
    else:
        local()
