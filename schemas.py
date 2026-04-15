from pydantic import BaseModel, Field
from typing import Optional, List

class Container(BaseModel):
    container_number: Optional[str] = None
    container_type: Optional[str] = None
    seal_number: Optional[str] = None

class WaybillData(BaseModel):
    document_type: str = Field(description="Art des Dokuments: sea_waybill, bill_of_lading, invoice, sonstige")
    document_number: Optional[str] = Field(None, description="Dokumentnummer")
    shipper: Optional[str] = Field(None, description="Absender/Verlader")
    consignee: Optional[str] = Field(None, description="Empfänger")
    notify_party: Optional[str] = Field(None, description="Benachrichtigungspartei")
    vessel_name: Optional[str] = Field(None, description="Schiffsname")
    voyage_number: Optional[str] = Field(None, description="Reisenummer")
    port_of_loading: Optional[str] = Field(None, description="Verladehafen")
    port_of_discharge: Optional[str] = Field(None, description="Löschhafen")
    etd: Optional[str] = Field(None, description="Abfahrtsdatum")
    eta: Optional[str] = Field(None, description="Ankunftsdatum")
    containers: List[Container] = Field(default_factory=list)
    cargo_description: Optional[str] = Field(None, description="Warenbeschreibung")
    gross_weight_kg: Optional[float] = Field(None, description="Bruttogewicht in kg")
    measurement_cbm: Optional[float] = Field(None, description="Volumen in CBM")
    freight_terms: Optional[str] = Field(None, description="PREPAID oder COLLECT")
    hs_codes: List[str] = Field(default_factory=list, description="HS-Codes")
