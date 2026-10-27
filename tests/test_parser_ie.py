# pyright: reportPrivateUsage=false
# -*- coding: utf-8 -*-

"""
Tests for Irish (Republic of Ireland) address parser.

Positive address examples include rows informed by the Companies
Registration Office company register (opendata.cro.ie, CC BY 4.0)
and layouts from An Post / UPU Ireland addressing guidance.
"""

import re
import time
import pytest
import itertools
from pyap import parser, utils, parse
import pyap.source_IE.data as data_ie


def execute_matching_test(input, expected, pattern):
    match = utils.match(pattern, input, re.VERBOSE)
    is_found = match is not None
    if expected:
        assert is_found == expected
        assert match.group(0) == input  # type: ignore
    else:
        assert (is_found == expected) or (match.group(0) != input)  # type: ignore


@pytest.mark.parametrize(
    "input,expected",
    [
        ("D6W FP23", True),
        ("T12XA97", True),
        ("t12 xa97", True),
        ("a65 f4e2", True),
        ("B65 F4E2", False),
        ("A65 F4B2", False),
        ("D6X 1234", False),
        ("1234567", False),
        ("XA65 F4E2", False),
    ],
)
def test_postal_code(input, expected):
    execute_matching_test(input, expected, data_ie.postal_code)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Co. Cork", True),
        ("County Kildare", True),
        ("Dublin 6W", True),
        ("Dublin 24", True),
        ("CORK", True),
        ("Dublin 19", False),
        ("Dublin 25", False),
        ("cork", False),
    ],
)
def test_region1(input, expected):
    execute_matching_test(input, expected, data_ie.region1)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("12", True),
        ("12A", True),
        ("12-14", True),
        ("63/64", True),
        ("12345", False),
    ],
)
def test_street_number(input, expected):
    execute_matching_test(input, expected, data_ie.street_number)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Road", True),
        ("St", True),
        ("Street", True),
        ("Rd", True),
        ("Notatype", False),
    ],
)
def test_street_type(input, expected):
    execute_matching_test(input, expected, data_ie.street_type)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Unit K4", True),
        ("Flat 2", True),
        ("Suite 100", True),
        ("Unit", False),
    ],
)
def test_occupancy(input, expected):
    execute_matching_test(input, expected, data_ie.occupancy)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("First Floor", True),
        ("Ground Floor", True),
        ("Floor 2", True),
        ("Level 3", True),
    ],
)
def test_floor(input, expected):
    execute_matching_test(input, expected, data_ie.floor)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Po Box 1234", True),
        ("P.O. Box 456", True),
        ("PO Box 99", True),
    ],
)
def test_po_box(input, expected):
    execute_matching_test(input, expected, data_ie.po_box)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Ireland", True),
        ("Republic of Ireland", True),
        ("Eire", True),
        ("United States", False),
    ],
)
def test_country(input, expected):
    execute_matching_test(input, expected, data_ie.country)


@pytest.mark.parametrize(
    "input,expected",
    [
        ('85 LATCHFORD SQUARE, DUBLIN 15, CLONSILLA,DUBLIN, D15Y585', True),
        ('Venture Hub, 136 Capel Street, Dublin 1, D01 T2C9', True),
        ('6 Fern Road, Sandyford, Dublin 18, D18 FP98', True),
        ('7 BALLENTREE AVENUE, DUBLIN,Dublin 15, D15 XR7N', True),
        ('MELROSE, 7 SAINT AGNES TERRACE, DUBLIN 12, D12NR2C', True),
        ("45 CRESTON AVENUE, ST. MARGARET'S ROAD, DUBLIN 11, D11NT38", True),
        ('24 Glendale Park, Terenure, Dublin 12, D12 EK1E', True),
        ('29 EARLSFORT TERRACE, DUBLIN 2, D02AY28', True),
        ('3 FITZWILLIAM COURT, PEMBROKE STREET UPPER, DUBLIN 2, D02WP99', True),
        ('UNIT 12, CLONDALKIN BUSINESS CENTRE, CLONDALKIN DUBLIN 22, CLONDALKIN,DUBLIN, D22YK16', True),
        ('24/26 CITY QUAY, DUBLIN 2., DUBLIN 2, D02NY19', True),
        ('11 FOYLE ROAD, DUBLIN,Dublin 3, D03 H6Y4', True),
        ('225 CLONTARF ROAD, DUBLIN 3, CLONTARF,DUBLIN, D03YP46', True),
        ('12 CLONTARF ROAD, DUBLIN 3, CLONTARF,DUBLIN, D03V3P4', True),
        ('49 VERNON AVENUE, DUBLIN 3., CLONTARF,DUBLIN, D03C3H4', True),
        ('60 North Strand Road, North Strand,Dublin 3, D03 HC96', True),
        ('22 NORTHUMBERLAND ROAD, BALLSBRIDGE,DUBLIN 4, D04ED73', True),
        ('74 NORTHUMBERLAND ROAD, DUBLIN 4, BALLSBRIDGE,DUBLIN, D04XF75', True),
        ('24A Baggot Street Upper, Dublin 4, D04 N528', True),
        ('21 SAINT ALBANS PARK, DUBLIN 4, SANDYMOUNT,DUBLIN, D04W6H3', True),
        ('3rd Floor, Mespil Road, ,Dublin 4, D04 C2N4', True),
        ('Unit 14, Greendale Shopping Centre, Kilbarrack, Dublin 5, D05Y0X2', True),
        ('1 WHITETHORN CRESCENT, DUBLIN 5, ARTANE,DUBLIN, D05H1F6', True),
        ('15 MAIN STREET, DUBLIN 5, RAHENY,DUBLIN, D05X006', True),
        ('64 CLANAWLEY ROAD, DONNYCARNEY, Dublin 5, Ireland, D05 WC65', True),
        ('APARTMENT 10, The Mews, Edenmore Avenue, Dublin 5, D05 DD76', True),
        ('127 BEAUVALE PARK, ARTANE, DUBLIN 5, D05 X5P2', True),
        ('85 PINEBROOK DRIVE ARTANE, DUBLIN 5, ARTANE,DUBLIN, D05N9Y4', True),
        ('59 Grosvenor Lodge, Rathmines, Dublin 6, D06T7E0', True),
        ('184 LOWER RATHMINES ROAD, DUBLIN 6, D06RX99', True),
        ("302 HAROLD'S CROSS ROAD, DUBLIN 6W,DUBLIN, D6WNV91", True),
        ('THE CARTRIDGE SHOP, 107 Rathmines Road Lower, Dublin 6, D06 CF40', True),
        ("31-32 GREENMOUNT OFFICE PARK, HAROLD'S CROSS BRIDGE, DUBLIN 6W,DUBLIN, D6WP289", True),
        ('APARTMENT 166, THE HARDWICKE, BRUNSWICK STREET NORTH DUBLIN 7, DUBLIN 7, D07TK20', True),
        ('APARTMENT 116, HAMPTON SQUARE, NAVAN ROAD DUBLIN 7, DUBLIN 7, D07KC8A', True),
        ('Grangegorman Court, 2C Grangegorman Lower, Dublin 7, D07 PW9N', True),
        ('Flat 3, 36 Goldsmith Street, Phibsborough, Dublin 7, D07 ET6R', True),
        ('140 PHIBSBOROUGH ROAD, DUBLIN 7, D07F8NE', True),
        ("THE BLACK CHURCH, ST. MARY'S PLACE, DUBLIN 7 D07P4AX IRELAND, DUBLIN 7, D07P4AX", True),
        ('149 Emmet Road, Inchicore, Dublin 8, D08 PR94', True),
        ('74 - 79 CORK STREET, DUBLIN 8, DUBLIN, D08Y2F8', True),
        ('APARTMENT 25, BLOCK B, THE BARLEY HOUSE, CORK STREET, DUBLIN,Dublin 8, D08 E522', True),
        ('2 Clanbrassil Street Upper, Dublin 8, D08 F785', True),
        ('UNIT 14, GOLDENBRIDGE INDUSTRIAL ESTATE, INCHICORE DUBLIN 8, INCHICORE,DUBLIN, D08R768', True),
        ('75 SOUTH CIRCULAR ROAD, DUBLIN 8., DUBLIN 8, D08E102', True),
        ('UNIT 2, THE BOOKEND, ESSEX QUAY DUBLIN 8, DUBLIN 8, D08CF83', True),
        ('30 BOTANIC AVENUE, DUBLIN 9, DRUMCONDRA,DUBLIN, D09CF85', True),
        ('UNIT A6, BLOCK A, SANTRY BUSINESS PARK SANTRY DUBLIN 9, SANTRY,DUBLIN, D09X651', True),
        ('54 GLASNEVIN HILL, DUBLIN 9, GLASNEVIN,DUBLIN, D09W659', True),
        ('2 DROMNANANE ROAD, DUBLIN 9, BEAUMONT,DUBLIN, D09DP86', True),
        ('UNIT 3, KYLEMORE INDUSTRIAL ESTATE, KILLEEN ROAD,Dublin 10, D10 TY20', True),
        ('UNIT 80, CHERRY ORCHARD INDUSTRIAL ESTATE, DUBLIN 10, D10NX96', True),
        ('MOTORCITY, KYLEMORE ROAD, DUBLIN 10, D12TFR7', True),
        ('92 ORANMORE ROAD, DUBLIN 10, BALLYFERMOT,DUBLIN, D10PC67', True),
        ('UNIT 2A, ALLIED INDUSTRIAL ESTATE, KYLEMORE ROAD BALLYFERMOT DUBLIN 10, BALLYFERMOT,DUBLIN, D10X229', True),
        ('Kylemore Road, Ballyfermot, DUBLIN,Dublin 10, D10 EW77', True),
        ('44 Cherry Orchard Parade, Ballyfermot, Dublin 10, D10 C970', True),
        ("9 HAMPTON WOOD DRIVE, SAINT MARGARET'S ROAD, DUBLIN 11, D11A027", True),
        ('UNIT 47, DUBLIN INDUSTRIAL ESTATE, FINGLAS ROAD DUBLIN 11., DUBLIN, D11X376', True),
        ('38 CLAREMONT CRESCENT, DUBLIN 11, GLASNEVIN,DUBLIN, D11Y9W0', True),
        ('Unit C1, NORTH CITY BUSINESS PARK, FINGLAS DUBLIN 11., FINGLAS,DUBLIN, D11RW30', True),
        ('48 Casement Green, Finglas West, Dublin 11, D11 N2P8', True),
        ('71 A MOYLE ROAD, DUBLIN IND ESTATE, DUBLIN 11, D11FF29', True),
        ('UNIT 6A, STADIUM BUSINESS PARK, BALLYCOOLIN ROAD, DUBLIN 11, DUBLIN, D11 NYP8', True),
        ('165 CROMWELLSFORT ROAD, WALKINSTOWN, DUBLIN 12, D12XV77', True),
        ('90 ROCKFIELD AVENUE, PERRYSTOWN, DUBLIN 12, D12Y974', True),
        ('39 BALFE AVENUE, WALKINSTOWN, DUBLIN 12, D12X5Y4', True),
        ('Unit 61 Parkwest Enterprise Centre, Lavery Avenue, Parkwest, Dublin 12, D12VP46', True),
        ('UNIT B7 RIVERVIEW BUSINESS PARK, NANGOR ROAD, DUBLIN 12, D12Y7C2', True),
        ('PARKVIEW HOUSE, 188A KIMMAGE ROAD WEST, DUBLIN 12, D12DT32', True),
        ('75 GLENCARRAIG, SUTTON, DUBLIN 13, DUBLIN, D13X2Y3', True),
        ('Unit 82, Grange Way, Baldoyle Industrial Estate, ,Dublin 13, D13 VE29', True),
        ('8 WARREN GREEN, DUBLIN 13, BALDOYLE,DUBLIN, D13K2W8', True),
        ('75 GLENCARRAIG, DUBLIN 13, SUTTON,DUBLIN, D13X2Y3', True),
        ('PAROCHIAL HOUSE, DUBLIN 13, BALDOYLE,DUBLIN, D13K8K8', True),
        ('15 HARCOURT STREET, DUBLIN 2, D02 XY47', True),
        ('38 Rathclune, Kiltimagh,MAYO, F12 E034', True),
        ("1 LENNON'S COTTAGES, MERRION ROAD, DUBLIN 4, D04 Y3X2", True),
        ('ARD NA LEE HOUSE, LOWER ROAD, CROSSHAVEN CORK IRELAND, CROSSHAVEN,CORK, P43 CP08', True),
        ('INNER RING ROAD, WATERFORD, X91 H959', True),
        ('58 KENILWORTH PARK, DUBLIN,Dublin 6W, D6W WK68', True),
        ('THE TECHNOLOGY CENTRE, BLESSINGTON INDUSTRIAL ESTATE, BLESSINGTON,WICKLOW, W91 P52A', True),
        ('APARTMENT 43, GLOUCESTER SQUARE, RAILWAY STREET, DUBLIN,Dublin 1, D01 K640', True),
        ('12 CHURCH VIEW GARDENS, WATERGRASSHILL,CORK, T56 PK71', True),
        ('TARA COURT, DUBLIN ROAD, NAAS KILDARE W91 R620, NAAS,KILDARE, W91 R620', True),
        ('LYNNDERRY HOUSE, LYNN ROAD, MULLINGAR CO. WESTMEATH, MULLINGAR,WESTMEATH, N91 R2F2', True),
        ('58 WESTON CRESCENT, LUCAN,DUBLIN, K78 H220', True),
        ("APARTMENT 12, PARK HOUSE, WILLAN'S DRIVE, DUBLIN,Dublin 15, D15 PK81", True),
        ('109 STRAND ROAD, DUBLIN 4, SANDYMOUNT,DUBLIN, D04 YH01', True),
        ('11 Whitfield Grove, Dublin 6, D06 F2C5', True),
        ('JASONIA CENTER, 76 DAME STREET, DUBLIN 2, D02 YY54', True),
        ('FIRST FLOOR FITZWILTON HOUSE, WILTON PLACE DUBLIN 2, DUBLIN, D02 FX04', True),
        ('2 DYSART WOOD, DRIPSEY,CORK, P12 XV83', True),
        ('6 FOXROCK COURT, DUBLIN 18., FOXROCK,DUBLIN, D18 Y3X8', True),
        ('UNIT K23 DRINAN ENTERPRISE CENTRE, SWORDS ENTERPRISE PARK, FELTRIM ROAD SWORDS CO. DUBLIN, SWORDS,DUBLIN, K67 PX76', True),
        ('UNIT 1A, LIOSBAN BUSINESS PARK, TUAM ROAD GALWAY, CO. GALWAY,GALWAY, H91 FX5V', True),
        ('35 CARYSFORT AVENUE, BLACKROCK,DUBLIN, A94 XE98', True),
        ('West Pier, Dun Laoghaire, ,DUBLIN, A96 N6T7', True),
        ('20 WAINSFORT MANOR DRIVE, DUBLIN 6W,DUBLIN, D6W EP94', True),
        ('Unit 20, Danville Business Park, Kilkenny, Ireland, R95 K282', True),
        ('56 Broomfield, Macroom, Co. Cork, T37 F8HK', True),
        ('56 Broomfield, Macroom, Co. Cork', True),
        ('21 Stonewall Drive, Dublin 24, D24 TF12', True),
        ('21 Stonewall Drive, Dublin 24, D24 TF12, Ireland', True),
        ('Ballinroamin, Thurles, Co. Tipperary, A65 TF12', True),
        ('Ballinroamin, Thurles, Co. Tipperary', True),
        ('37 George Street, Kinsale, Co. Cork, P17 F4E2', True),
        ('37 George Street, Kinsale, Co. Cork, P17 F4E2, Ireland', True),
        ('Po Box 1234, Galway, Co. Galway, H91 X0X0', True),
        ('P.O. Box 456, Main Street, Sligo, Co. Sligo, F91 F4E2', True),
        ('First Floor, 2 Grand Canal Square, Dublin 2, D02 A342', True),
        ('Apartment 4, The Mall, Riverside Way, Midleton, Co. Cork, P25 PR28', True),
        ('2-4 Main Street, Letterkenny, Co. Donegal, F92 E8X7', True),
        ("12A O'Connell Street, Limerick, Co. Limerick, V94 H9X0", True),
        ('Level 3, Custom House Plaza, Harcourt Road, Dublin 2, D02 T292', True),
        ('63/64 Grafton Street, Dublin 2, D02 VX62', True),
        ("St. Mary's Road, Dundalk, Co. Louth, A91 P0X0", True),
        ('Industrial Estate, Nenagh, Co. Tipperary, E45 A0X0', True),
        ('Main Street, Ardmore, Youghal, Co. Cork, P36 A0X0', True),
        ('43 fitzwilliam square, dublin 2, d02 k792', True),
        ('12 main street, macroom, co. cork', True),
        ('Ard na Gréine, Ballina, Co. Mayo, F26 X2Y3', True),
        ('Bóthar na Trá, Galway, H91 X0X0', True),
        ('Óstán Na Coille, Sráid Mhór, Co. Galway', True),
        ('SRÁID MHÓR, CO. GALWAY, H91 X0X0', True),
        ('Thanks, Kerry', False),
        ('Regards, John, Meath', False),
        ('Attendees: John Murphy, Mary Kelly, Clare', False),
        ('In 2020 Kerry won the final, Clare', False),
        ('12 Main Street, Macroom, Cork', False),
        ('+353 1 633 1500', False),
        ('087 123 4567', False),
        ('(021) 455 1234', False),
        ('IE1234567T', False),
        ('IE 9S99999L', False),
        ('moved to Cork last year', False),
        ('Dublin 2026', False),
        ('Dublin 19', False),
        ('Dublin 25', False),
        ('Main Street', False),
        ('12 High Street without county', False),
        ('55 Glenfada Park, Londonderry BT48 9DR', False),
        ('Product code A65 F4E2 batch 12', False),
        ('IBAN IE29 AIBK 9311 5212 3456 78', False),
        ('Company number 123456', False),
        ('Call us on 01-633-1500 today', False),
        ('B65 F4E2', False),
        ('A65 F4B2', False),
        ('D6X 1234', False),
        ('4060 AUTOMATIC STRAPPING MACHINE KZB-II STRAPPING MA', False),
        ('130 AUTOMATIC STRAPPING MACHINE CO', False),
        ('ONE FOR ANY DIRECT, INDIRECT, IN', False),
        ('23 ELECTRICAL COLOURED-TAPE PR', False),
        ('7901 SILVER CONDUCTIVE HOLE FILL MA', False),
        ('3 THIRD PARTY LIST IN', False),
    ],
)
def test_full_address(input, expected):
    execute_matching_test(input, expected, data_ie.full_address)


def test_full_address_parts():
    example_addresses = [
        {
            "full_address": "43 Fitzwilliam Square, Dublin 2, D02 K792",
            "street_name": "Fitzwilliam Square",
            "street_number": "43",
            "region1": "Dublin 2",
            "postal_code": "D02 K792",
        },
        {
            "full_address": "Unit K4 Marina Commercial Park, Centre Park Road, Co. Cork, T12 XA97",
            "occupancy": "Unit K4",
            "street_name": "Marina Commercial Park",
            "city": "Centre Park Road",
            "region1": "Co. Cork",
            "postal_code": "T12 XA97",
        },
        {
            "full_address": "Ballyboggan, Barntown, Co. Wexford, Y35 K0EE",
            "street_name": "Ballyboggan",
            "city": "Barntown",
            "region1": "Co. Wexford",
            "postal_code": "Y35 K0EE",
        },
    ]
    filler_text = (
        "This is filler text that can be inserted both before and after addresses"
    )
    punctuation = ["\n", ", ", ". ", " "]

    for address_parts in example_addresses:
        for filler_before, filler_after in itertools.product(
            [False, True], [False, True]
        ):
            for join_string in punctuation:
                filler_text_before = (
                    (filler_text + join_string) if filler_before else ""
                )
                filler_text_after = (join_string + filler_text) if filler_after else ""
                address_text = (
                    filler_text_before
                    + address_parts["full_address"]
                    + filler_text_after
                )
                parsed = parse(address_text, country="IE")
                assert len(parsed) == 1
                for k, v in address_parts.items():
                    if k == "full_address":
                        assert parsed[0].full_address == parser.AddressParser._normalize_string(v)
                    else:
                        assert parsed[0].__getattribute__(k) == v


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Our Office Moved To 43 Fitzwilliam Square, Dublin 2, D02 K792",
            ["43 Fitzwilliam Square, Dublin 2, D02 K792"],
        ),
        (
            "See you at 21 Stonewall Drive, Dublin 24 tomorrow",
            ["21 Stonewall Drive, Dublin 24"],
        ),
        ("Thanks, Kerry", []),
        ("Please contact Sean O'Brien, Kerry", []),
        ("Attendees: John Murphy, Mary Kelly, Clare", []),
        ("moved to dublin last year", []),
        ("I live in Dublin", []),
    ],
)
def test_parse_in_running_text(text, expected):
    assert [a.full_address for a in parse(text, country="IE")] == expected


def test_parse_long_text_is_fast():
    paragraph = (
        "The Quarterly Report For The Board Of Directors Was Circulated To All "
        "Members, Including The Finance Committee And The Audit Group, Before "
        "The Meeting. "
    )
    text = paragraph * 200
    start = time.perf_counter()
    parsed = parse(text, country="IE")
    elapsed = time.perf_counter() - start
    assert parsed == []
    assert elapsed < 5
