"""
DocExtract Pro — Demo-Daten
Realistische Sea Waybill Demo ohne PDF-Upload
"""

DEMO_WAYBILL_TEXT = """
SEA WAYBILL

SHIPPER:
SHANGHAI PACIFIC TRADING CO., LTD.
Building 8, Pudong New Area
200120 Shanghai, P.R. China
Tel: +86 21 5888 7654

CONSIGNEE:
EUROPA LOGISTICS GMBH
Hafenstraße 42
20459 Hamburg, Germany
Tel: +49 40 3600 1234

NOTIFY PARTY:
SAME AS CONSIGNEE

SEA WAYBILL NUMBER: ARKS240415001
DATE OF ISSUE: 15.04.2024
PLACE OF ISSUE: Shanghai

OCEAN VESSEL: EVER GOLDEN
VOYAGE NO.: 0241W
PORT OF LOADING: SHANGHAI (CNSHA)
PORT OF DISCHARGE: HAMBURG (DEHAM)
PLACE OF DELIVERY: HAMBURG CFS

DATE OF DEPARTURE (ETD): 2024-04-18
ESTIMATED ARRIVAL (ETA): 2024-05-22

CONTAINER INFORMATION:
TCKU3456789  |  40HC  |  SEAL: SH987654
MSCU1234567  |  20GP  |  SEAL: SH123456

DESCRIPTION OF GOODS:
Electronic Components and Spare Parts
HS Code: 8542.31.00, 8473.30.00

NUMBER OF PACKAGES: 245 CARTONS
GROSS WEIGHT: 18,750 KG
NET WEIGHT: 17,200 KG
MEASUREMENT: 62.5 CBM

FREIGHT: PREPAID
INCOTERMS: FOB SHANGHAI

BOOKING NO.: BKG-2024-00891
PURCHASE ORDER: PO-EUR-2024-0055
"""

DEMO_RESULT = {
    "document_type": "sea_waybill",
    "document_number": "ARKS240415001",
    "issue_date": "2024-04-15",
    "place_of_issue": "Shanghai",
    "shipper": {
        "name": "SHANGHAI PACIFIC TRADING CO., LTD.",
        "address": "Building 8, Pudong New Area, 200120 Shanghai",
        "country": "China"
    },
    "consignee": {
        "name": "EUROPA LOGISTICS GMBH",
        "address": "Hafenstraße 42, 20459 Hamburg",
        "country": "Germany"
    },
    "notify_party": {"name": "SAME AS CONSIGNEE", "address": None, "country": None},
    "vessel_name": "EVER GOLDEN",
    "voyage_number": "0241W",
    "port_of_loading": "SHANGHAI (CNSHA)",
    "port_of_discharge": "HAMBURG (DEHAM)",
    "place_of_delivery": "HAMBURG CFS",
    "etd": "2024-04-18",
    "eta": "2024-05-22",
    "service_type": "FCL",
    "containers": [
        {"container_number": "TCKU3456789", "container_type": "40HC", "seal_number": "SH987654"},
        {"container_number": "MSCU1234567", "container_type": "20GP", "seal_number": "SH123456"},
    ],
    "cargo_description": "Electronic Components and Spare Parts",
    "hs_codes": ["8542.31.00", "8473.30.00"],
    "number_of_packages": 245,
    "package_type": "CARTONS",
    "gross_weight_kg": 18750.0,
    "net_weight_kg": 17200.0,
    "measurement_cbm": 62.5,
    "freight_terms": "PREPAID",
    "incoterms": "FOB",
    "booking_number": "BKG-2024-00891",
    "purchase_order": "PO-EUR-2024-0055",
}
