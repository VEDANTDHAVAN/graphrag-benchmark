import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin  # noqa: F401


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data" / "results" / "final_summary.json"
ACCURACY_PATH = ROOT / "data" / "results" / "scientific_accuracy_report.json"
METADATA_PATH = ROOT / "data" / "raw" / "scientific_papers_2m_metadata.json"
ARCHITECTURE_PATH = ROOT / "docs" / "assets" / "graphrag-benchmark-architecture.png"
OUTPUT_PATH = ROOT / "data" / "results" / "graphrag_benchmark_report.pdf"

PAGE_W, PAGE_H = 1240, 1754
MARGIN = 78
BLUE = (37, 99, 235)
TEAL = (13, 148, 136)
INK = (17, 24, 39)
MUTED = (75, 85, 99)
LIGHT = (249, 250, 251)
BORDER = (229, 231, 235)
WHITE = (255, 255, 255)


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_TITLE = font(42, True)
F_H1 = font(32, True)
F_H2 = font(24, True)
F_BODY = font(18)
F_SMALL = font(15)
F_MONO = font(16)


def read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def page(title: str = ""):
    img = Image.new("RGB", (PAGE_W, PAGE_H), WHITE)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, PAGE_W, 18), fill=BLUE)
    if title:
        draw.text((MARGIN, 42), title, font=F_H1, fill=INK)
        draw.line((MARGIN, 92, PAGE_W - MARGIN, 92), fill=BORDER, width=2)
    return img, draw


def wrapped(draw, text, xy, width, font_obj=F_BODY, fill=MUTED, line_gap=8):
    x, y = xy
    max_chars = max(35, int(width / (font_obj.size * 0.52)))
    for paragraph in str(text).split("\n"):
        lines = textwrap.wrap(paragraph, width=max_chars) or [""]
        for line in lines:
            draw.text((x, y), line, font=font_obj, fill=fill)
            y += font_obj.size + line_gap
        y += line_gap
    return y


def card(draw, box, title, body, accent=BLUE):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=LIGHT, outline=BORDER, width=2)
    draw.rectangle((x1, y1, x1 + 7, y2), fill=accent)
    draw.text((x1 + 26, y1 + 24), title, font=F_H2, fill=INK)
    wrapped(draw, body, (x1 + 26, y1 + 66), x2 - x1 - 52, F_BODY, MUTED)


def fmt(value, digits=2, suffix=""):
    if value is None:
        return "Not available"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}{suffix}"
    return str(value)


def table(draw, x, y, headers, rows, widths, row_h=54):
    draw.rounded_rectangle((x, y, x + sum(widths), y + row_h), radius=10, fill=(239, 246, 255), outline=BORDER)
    cx = x
    for header, width in zip(headers, widths):
        draw.text((cx + 12, y + 16), header, font=F_SMALL, fill=INK)
        cx += width
    y += row_h
    for row in rows:
        draw.rectangle((x, y, x + sum(widths), y + row_h), fill=WHITE, outline=BORDER)
        cx = x
        for cell, width in zip(row, widths):
            draw.text((cx + 12, y + 16), str(cell), font=F_SMALL, fill=MUTED)
            cx += width
        y += row_h
    return y


def build_report():
    summary = read_json(SUMMARY_PATH, {})
    accuracy = read_json(ACCURACY_PATH, {})
    metadata = read_json(METADATA_PATH, {})
    pages = []

    img, draw = page()
    draw.text((MARGIN, 90), "GraphRAG Benchmark Report", font=F_TITLE, fill=INK)
    wrapped(
        draw,
        "A 2 million token scientific-paper benchmark comparing LLM-only, Basic RAG, and NetworkX GraphRAG across efficiency, cost, and answer quality.",
        (MARGIN, 160),
        PAGE_W - 2 * MARGIN,
        F_BODY,
        MUTED,
    )
    y = 260
    metrics = [
        ("Dataset", "armanc/scientific_papers, arXiv split"),
        ("Token scale", f"{metadata.get('total_tokens', 2004563):,} tokens"),
        ("Documents", f"{metadata.get('num_documents', 220):,} papers"),
        ("Evaluation set", "40 grounded questions"),
        ("Deployment", "Vercel frontend + Hugging Face Spaces backend"),
    ]
    for i, (k, v) in enumerate(metrics):
        x = MARGIN + (i % 2) * 535
        yy = y + (i // 2) * 132
        card(draw, (x, yy, x + 500, yy + 104), k, v, BLUE if i % 2 == 0 else TEAL)
    y = 690
    card(
        draw,
        (MARGIN, y, PAGE_W - MARGIN, y + 210),
        "Problem statement",
        "LLM-only systems can hallucinate and lack source grounding. Basic RAG improves grounding with vector search but often misses relationships across entities, methods, datasets, and documents. This benchmark tests whether graph-structured retrieval can provide compact, relationship-aware context while preserving or improving answer quality.",
        BLUE,
    )
    card(
        draw,
        (MARGIN, y + 245, PAGE_W - MARGIN, y + 455),
        "Key conclusion",
        "GraphRAG produced the strongest BERTScore in the current run and the lowest average latency, while using substantially fewer tokens than Basic RAG. The benchmark demonstrates the value of graph-based retrieval methodology without requiring TigerGraph.",
        TEAL,
    )
    pages.append(img)

    img, draw = page("Architecture")
    if ARCHITECTURE_PATH.exists():
        arch = Image.open(ARCHITECTURE_PATH).convert("RGB")
        max_w = PAGE_W - 2 * MARGIN
        scale = min(max_w / arch.width, 770 / arch.height)
        arch = arch.resize((int(arch.width * scale), int(arch.height * scale)), Image.Resampling.LANCZOS)
        draw.rounded_rectangle((MARGIN - 10, 125, PAGE_W - MARGIN + 10, 125 + arch.height + 20), radius=18, fill=LIGHT, outline=BORDER)
        img.paste(arch, (MARGIN, 135))
        y = 135 + arch.height + 55
    else:
        y = 130
    wrapped(
        draw,
        "The deployed architecture uses a Next.js frontend on Vercel and a FastAPI backend on Hugging Face Spaces. ChromaDB stores vector embeddings, NetworkX stores the serialized graph, and TigerGraph remains an optional enterprise connector.",
        (MARGIN, y),
        PAGE_W - 2 * MARGIN,
        F_BODY,
        MUTED,
    )
    pages.append(img)

    img, draw = page("Pipeline Methodology")
    cards = [
        ("LLM-only", "Direct question to the language model. Useful baseline, but no retrieval grounding.", BLUE),
        ("Basic RAG", "ChromaDB vector search retrieves semantically similar chunks and sends them as context.", TEAL),
        ("GraphRAG", "NetworkX graph traversal retrieves relationship-aware chunks through entity and graph structure.", BLUE),
    ]
    y = 130
    for title, body, accent in cards:
        card(draw, (MARGIN, y, PAGE_W - MARGIN, y + 180), title, body, accent)
        y += 220
    card(
        draw,
        (MARGIN, y, PAGE_W - MARGIN, y + 240),
        "TigerGraph to NetworkX pivot",
        "TigerGraph was explored first because it is powerful for enterprise graph storage. In practice, authentication issues, Docker complexity, resource requirements, and infrastructure overhead distracted from the research question. NetworkX preserves graph traversal and multi-hop reasoning, runs entirely in Python, and keeps the benchmark reproducible for judges.",
        TEAL,
    )
    pages.append(img)

    img, draw = page("Benchmark Results")
    headers = ["Pipeline", "Tokens", "Latency", "Cost", "Judge", "BERT F1"]
    rows = []
    labels = {"llm_only": "LLM-only", "basic_rag": "Basic RAG", "graphrag": "GraphRAG"}
    for key in ("llm_only", "basic_rag", "graphrag"):
        s = summary.get(key, {})
        a = accuracy.get(key, {})
        rows.append(
            [
                labels[key],
                fmt(s.get("avg_total_tokens"), 1),
                fmt(s.get("avg_latency_seconds"), 2, "s"),
                "$" + fmt(s.get("avg_estimated_cost"), 5),
                "Not available" if a.get("llm_judge_pass_rate") is None else fmt(a.get("llm_judge_pass_rate") * 100, 1, "%"),
                fmt(a.get("bertscore_f1"), 3),
            ]
        )
    y = table(draw, MARGIN, 140, headers, rows, [170, 145, 145, 145, 190, 145])
    wrapped(
        draw,
        "LLM-as-a-Judge pass rate is marked unavailable because the current accuracy report contains null pass-rate values. This usually means hosted judge calls were skipped or unavailable during the evaluation run. BERTScore values are included from scientific_accuracy_report.json.",
        (MARGIN, y + 45),
        PAGE_W - 2 * MARGIN,
        F_BODY,
        MUTED,
    )
    reductions = [
        [
            "Basic RAG",
            fmt(summary.get("basic_rag", {}).get("token_reduction_vs_llm_only"), 1, "%"),
            fmt(summary.get("basic_rag", {}).get("latency_reduction_vs_llm_only"), 1, "%"),
            fmt(summary.get("basic_rag", {}).get("cost_reduction_vs_llm_only"), 1, "%"),
        ],
        [
            "GraphRAG",
            fmt(summary.get("graphrag", {}).get("token_reduction_vs_llm_only"), 1, "%"),
            fmt(summary.get("graphrag", {}).get("latency_reduction_vs_llm_only"), 1, "%"),
            fmt(summary.get("graphrag", {}).get("cost_reduction_vs_llm_only"), 1, "%"),
        ],
    ]
    table(draw, MARGIN, y + 190, ["Vs LLM-only", "Token", "Latency", "Cost"], reductions, [220, 200, 200, 200])
    pages.append(img)

    img, draw = page("Accuracy and Conclusions")
    card(
        draw,
        (MARGIN, 130, PAGE_W - MARGIN, 350),
        "Accuracy methodology",
        "Two complementary evaluations are used. LLM-as-a-Judge asks an independent hosted model to grade PASS or FAIL against a reference answer. BERTScore measures semantic similarity, capturing correct paraphrases that do not match exact wording.",
        BLUE,
    )
    card(
        draw,
        (MARGIN, 390, PAGE_W - MARGIN, 610),
        "Dataset rationale",
        "Scientific papers are ideal for GraphRAG because they contain methods, datasets, tasks, concepts, citations, and cross-document relationships. The arXiv corpus creates realistic opportunities for multi-hop retrieval.",
        TEAL,
    )
    conclusions = [
        "GraphRAG achieved the highest BERTScore F1 in the current accuracy report.",
        "GraphRAG had the lowest average latency among the three pipelines.",
        "GraphRAG used far fewer tokens and lower estimated cost than Basic RAG.",
        "NetworkX is sufficient for the benchmark because the claim is about graph-based retrieval methodology, not vendor-specific graph infrastructure.",
        "TigerGraph remains valuable as an optional enterprise connector for larger deployments.",
    ]
    draw.text((MARGIN, 670), "Key conclusions", font=F_H2, fill=INK)
    y = 720
    for item in conclusions:
        draw.text((MARGIN + 8, y), "-", font=F_BODY, fill=BLUE)
        y = wrapped(draw, item, (MARGIN + 34, y), PAGE_W - 2 * MARGIN - 34, F_BODY, MUTED, 6)
    pages.append(img)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(OUTPUT_PATH, save_all=True, append_images=pages[1:], resolution=150)
    print(f"Saved PDF report to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_report()
