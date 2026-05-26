from html import escape
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.models import ScanRun


def generate_html_report(scan: ScanRun) -> str:
    findings = scan.findings or []
    rows = []
    for finding in findings:
        endpoint = finding.endpoint
        evidence = "<br>".join(escape(ev.title) for ev in finding.evidence_items)
        rows.append(
            f"<tr><td>{escape(finding.severity)}</td><td>{escape(finding.status)}</td><td>{escape(finding.title)}</td>"
            f"<td>{escape(endpoint.method + ' ' + endpoint.path if endpoint else 'n/a')}</td><td>{finding.risk_score:.1f}</td><td>{evidence}</td></tr>"
        )
    return f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>AppSec Pilot Report {escape(scan.id)}</title>
<style>body{{font-family:Inter,Arial,sans-serif;margin:32px;color:#17202a}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #d8dee9;padding:8px;text-align:left}}th{{background:#eef2f7}}.badge{{display:inline-block;padding:3px 8px;border-radius:12px;background:#e8f5e9}}</style></head>
<body>
<h1>AppSec Pilot Security Report</h1>
<p><b>Scan:</b> {escape(scan.id)} <span class=\"badge\">{escape(scan.status)}</span></p>
<p><b>Total endpoints:</b> {scan.total_endpoints} | <b>Findings:</b> {scan.total_findings} | <b>Confirmed:</b> {scan.confirmed_findings} | <b>Needs review:</b> {scan.needs_review_findings}</p>
<h2>Findings</h2>
<table><thead><tr><th>Severity</th><th>Status</th><th>Title</th><th>Endpoint</th><th>Risk</th><th>Evidence</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Verifier and Safety Notes</h2>
<p>All checks were constrained by scope policy, request limits, blocked categories, and redaction rules. Findings are valid only for the authorized local or staging target used by this scan.</p>
</body></html>"""


def generate_pdf_report(scan: ScanRun, path: Path) -> None:
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(48, y, "AppSec Pilot Security Report")
    y -= 28
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, y, f"Scan: {scan.id} | Status: {scan.status}")
    y -= 18
    pdf.drawString(48, y, f"Endpoints: {scan.total_endpoints} | Findings: {scan.total_findings} | Confirmed: {scan.confirmed_findings}")
    y -= 32
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(48, y, "Findings")
    y -= 20
    pdf.setFont("Helvetica", 9)
    for finding in scan.findings:
        endpoint = finding.endpoint
        line = f"{finding.severity.upper()} {finding.status}: {finding.title} ({endpoint.method + ' ' + endpoint.path if endpoint else 'n/a'})"
        for chunk in [line[i:i+100] for i in range(0, len(line), 100)]:
            pdf.drawString(48, y, chunk)
            y -= 14
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)
        y -= 6
    pdf.save()
