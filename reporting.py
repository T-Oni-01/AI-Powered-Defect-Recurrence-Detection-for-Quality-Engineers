import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def clip(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"

def wrap2(s: str, n: int) -> tuple[str, str]:
    s = (s or "").replace("\n", " ").strip()
    if len(s) <= n:
        return s, ""
    return s[:n], s[n: 2*n]

def export_qe_pdf(
    output_dir: str,
    query_text: str,
    threshold: float,
    recurring: bool,
    top_category: str | None,
    top_sub_category: str | None,
    matches_df,   # pandas DF
    section_filter: str | None
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"QE_Report_{ts}.pdf"
    path = os.path.join(output_dir, filename)

    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "QE Defect Recurrence Report")
    y -= 25

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 15
    c.drawString(50, y, f"Threshold: {threshold:.2f}")
    y -= 15
    c.drawString(50, y, f"Section filter: {section_filter or 'All'}")
    y -= 15
    c.drawString(50, y, f"Recurring: {'YES' if recurring else 'NO'}")
    y -= 15
    if recurring:
        c.drawString(50, y, f"Top category: {top_category or '-'}")
        y -= 15
        c.drawString(50, y, f"Top sub-category: {top_sub_category or '-'}")
        y -= 20
    else:
        y -= 10

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "User-entered defect:")
    y -= 15
    c.setFont("Helvetica", 10)

    # Wrap query text
    max_chars = 95
    for i in range(0, len(query_text), max_chars):
        c.drawString(50, y, query_text[i:i+max_chars])
        y -= 12
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, f"Top matches (showing up to 25):")
    y -= 15

    # Table header
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "sim")
    c.drawString(85, y, "date")
    c.drawString(170, y, "section")
    c.drawString(220, y, "jc_number")
    c.drawString(310, y, "category/sub")
    c.drawString(420, y, "description")
    y -= 12

    c.setFont("Helvetica", 8)

    if matches_df is not None and not matches_df.empty:
        top = matches_df.head(25)
        for _, row in top.iterrows():
            sim = f"{row.get('similarity_score', 0):.3f}"
            date = str(row.get("date", ""))[:10]
            section = str(row.get("section", ""))
            jc = clip(str(row.get("jc_number", "")), 14)
            cat = clip(str(row.get("category", "")), 12)
            sub = clip(str(row.get("sub_category", "")), 14)
            desc = str(row.get("description", ""))

            cat_sub = clip(f"{cat}/{sub}", 22)  # <= key: limit this column
            line1, line2 = wrap2(desc, 45)  # wrap description into 2 lines

            c.drawString(50, y, sim)
            c.drawString(85, y, date)
            c.drawString(170, y, section)
            c.drawString(220, y, jc)
            c.drawString(310, y, cat_sub)

            c.drawString(420, y, line1)
            y -= 10
            if line2:
                c.drawString(420, y, line2)
                y -= 10
            else:
                y -= 1  # keep spacing similar

            if y < 70:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 8)

    c.save()
    return path