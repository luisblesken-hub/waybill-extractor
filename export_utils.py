"""
DocExtract Pro — Export utilities
Supports: CSV, JSON, Excel (XLSX)
"""
import io
import json
import csv
from typing import List
from schemas import WaybillData


def to_flat_dict(data: WaybillData, filename: str = "") -> dict:
    """Flatten nested schema to a single dict for tabular export."""
    d = {}
    raw = data.model_dump()

    d["filename"]         = filename
    d["document_type"]    = raw["document_type"]
    d["document_number"]  = raw["document_number"]
    d["issue_date"]       = raw["issue_date"]
    d["place_of_issue"]   = raw["place_of_issue"]

    # Parties — flatten
    for party_name in ["shipper", "consignee", "notify_party"]:
        party = raw.get(party_name) or {}
        d[f"{party_name}_name"]    = party.get("name")
        d[f"{party_name}_address"] = party.get("address")
        d[f"{party_name}_country"] = party.get("country")

    d["carrier"]           = raw["carrier"]
    d["vessel_name"]       = raw["vessel_name"]
    d["imo_number"]        = raw["imo_number"]
    d["voyage_number"]     = raw["voyage_number"]
    d["port_of_loading"]   = raw["port_of_loading"]
    d["port_of_discharge"] = raw["port_of_discharge"]
    d["place_of_receipt"]  = raw["place_of_receipt"]
    d["place_of_delivery"] = raw["place_of_delivery"]
    d["etd"]               = raw["etd"]
    d["eta"]               = raw["eta"]
    d["on_board_date"]     = raw["on_board_date"]
    d["service_type"]      = raw["service_type"]

    # Containers — join as string
    containers = raw.get("containers") or []
    d["container_numbers"] = " | ".join(c.get("container_number") or "" for c in containers if c.get("container_number"))
    d["container_types"]   = " | ".join(c.get("container_type") or "" for c in containers if c.get("container_type"))
    d["container_seals"]   = " | ".join(c.get("seal_number") or "" for c in containers if c.get("seal_number"))
    d["container_count"]   = len(containers)

    d["cargo_description"]  = raw["cargo_description"]
    d["number_of_packages"] = raw["number_of_packages"]
    d["package_type"]       = raw["package_type"]
    d["gross_weight_kg"]    = raw["gross_weight_kg"]
    d["net_weight_kg"]      = raw["net_weight_kg"]
    d["measurement_cbm"]    = raw["measurement_cbm"]
    d["hs_codes"]           = " | ".join(raw.get("hs_codes") or [])
    d["dangerous_goods"]    = raw["dangerous_goods"]
    d["freight_terms"]      = raw["freight_terms"]
    d["incoterms"]          = raw["incoterms"]
    d["currency"]           = raw["currency"]
    d["invoice_value"]      = raw["invoice_value"]
    d["booking_number"]     = raw["booking_number"]
    d["purchase_order"]     = raw["purchase_order"]
    d["remarks"]            = raw["remarks"]

    return d


def export_csv(results: List[dict]) -> str:
    """Export list of flat dicts to CSV string."""
    if not results:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
    return buf.getvalue()


def export_json(results: List[dict]) -> str:
    """Export list of flat dicts to JSON string."""
    return json.dumps(results, ensure_ascii=False, indent=2, default=str)


def export_excel(results: List[dict]) -> bytes:
    """Export list of flat dicts to Excel bytes."""
    try:
        import xlsxwriter
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True})
        ws = wb.add_worksheet("DocExtract Pro")

        # Formats
        header_fmt = wb.add_format({
            "bold": True, "bg_color": "#1d4ed8", "font_color": "white",
            "border": 1, "text_wrap": True
        })
        cell_fmt = wb.add_format({"border": 1, "text_wrap": True})
        alt_fmt  = wb.add_format({"border": 1, "bg_color": "#f9fafb", "text_wrap": True})

        if not results:
            wb.close()
            return buf.getvalue()

        headers = list(results[0].keys())
        for col, h in enumerate(headers):
            ws.write(0, col, h.replace("_", " ").title(), header_fmt)
            ws.set_column(col, col, 18)

        for row, record in enumerate(results, 1):
            fmt = cell_fmt if row % 2 == 0 else alt_fmt
            for col, key in enumerate(headers):
                val = record.get(key)
                ws.write(row, col, str(val) if val is not None else "", fmt)

        ws.freeze_panes(1, 0)
        wb.close()
        return buf.getvalue()
    except ImportError:
        # Fallback: return CSV as bytes if xlsxwriter not available
        return export_csv(results).encode("utf-8")
