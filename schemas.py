"""
DocExtract Pro — Pydantic v2 schemas
Covers: Sea Waybills, Bills of Lading, Commercial Invoices, Packing Lists
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field


class Container(BaseModel):
    container_number: Optional[str] = Field(None, description="ISO 6346 container number")
    container_type:   Optional[str] = Field(None, description="e.g. 20GP, 40HC, 45HC, 20RF")
    seal_number:      Optional[str] = None
    teu:              Optional[float] = None
    gross_weight_kg:  Optional[float] = None
    net_weight_kg:    Optional[float] = None
    cbm:              Optional[float] = None


class Party(BaseModel):
    name:    Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    tax_id:  Optional[str] = None


class InvoiceLineItem(BaseModel):
    description: str
    quantity:    Optional[float] = None
    unit:        Optional[str]   = None
    unit_price:  Optional[float] = None
    total:       Optional[float] = None
    hs_code:     Optional[str]   = None
    country_of_origin: Optional[str] = None


class WaybillData(BaseModel):
    # ── Document Identity ──────────────────────────────────────────────────
    document_type:   str           = Field(description="sea_waybill | bill_of_lading | invoice | packing_list | certificate | generic")
    document_number: Optional[str] = Field(None, description="Primary document reference number")
    issue_date:      Optional[str] = Field(None, description="Document issue date ISO-8601")
    place_of_issue:  Optional[str] = None

    # ── Parties ────────────────────────────────────────────────────────────
    shipper:      Optional[Party] = Field(None, description="Shipper/exporter/seller")
    consignee:    Optional[Party] = Field(None, description="Consignee/importer/buyer")
    notify_party: Optional[Party] = None
    carrier:      Optional[str]   = None
    freight_forwarder: Optional[str] = None

    # ── Transport ──────────────────────────────────────────────────────────
    vessel_name:       Optional[str] = None
    imo_number:        Optional[str] = None
    voyage_number:     Optional[str] = None
    port_of_loading:   Optional[str] = Field(None, description="Full name or LOCODE")
    port_of_discharge: Optional[str] = None
    place_of_receipt:  Optional[str] = None
    place_of_delivery: Optional[str] = None
    etd:               Optional[str] = Field(None, description="Estimated/actual departure ISO-8601")
    eta:               Optional[str] = Field(None, description="Estimated/actual arrival ISO-8601")
    on_board_date:     Optional[str] = None
    service_type:      Optional[str] = Field(None, description="FCL, LCL, RORO, BULK, etc.")

    # ── Cargo ──────────────────────────────────────────────────────────────
    containers:        List[Container]      = Field(default_factory=list)
    cargo_description: Optional[str]        = None
    number_of_packages: Optional[int]       = None
    package_type:      Optional[str]        = None
    gross_weight_kg:   Optional[float]      = None
    net_weight_kg:     Optional[float]      = None
    measurement_cbm:   Optional[float]      = None
    marks_and_numbers: Optional[str]        = None
    hs_codes:          List[str]            = Field(default_factory=list)
    dangerous_goods:   Optional[bool]       = Field(None, description="True if DG cargo")
    un_number:         Optional[str]        = None
    temperature:       Optional[str]        = Field(None, description="For reefer cargo")

    # ── Commercial ─────────────────────────────────────────────────────────
    freight_terms:     Optional[str]        = Field(None, description="PREPAID or COLLECT")
    incoterms:         Optional[str]        = Field(None, description="e.g. FOB, CIF, DAP")
    currency:          Optional[str]        = None
    invoice_value:     Optional[float]      = None
    freight_amount:    Optional[float]      = None
    line_items:        List[InvoiceLineItem] = Field(default_factory=list)

    # ── References ─────────────────────────────────────────────────────────
    booking_number:    Optional[str]        = None
    purchase_order:    Optional[str]        = None
    letter_of_credit:  Optional[str]        = None
    customs_ref:       Optional[str]        = None

    # ── Remarks ────────────────────────────────────────────────────────────
    clauses:           List[str]            = Field(default_factory=list)
    remarks:           Optional[str]        = None
