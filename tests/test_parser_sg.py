# pyright: reportPrivateUsage=false
# -*- coding: utf-8 -*-

"""Tests for Singapore address parser.

Positive examples follow SingPost / UPU layout: a street or P.O. Box,
then the word Singapore and a 6-digit postcode. The block examples are
the UPU Singapore sheet (16 Sandilands Road; Blk 35 Mandalay Road).
"""

import itertools
import re

import pytest

from pyap import parse, parse_single_street, parser, utils
import pyap.source_SG.data as data_sg


def execute_matching_test(input, expected, pattern):
    match = utils.match(pattern, input, re.VERBOSE)
    is_found = match is not None
    if expected:
        assert is_found == expected
        assert match.group(0) == input  # type: ignore
    else:
        assert (is_found == expected) or (match.group(0) != input)  # type: ignore


UPU_BLOCK = "\n".join(
    [
        "Blk 35 Mandalay Road",
        "#13-37 Mandalay Towers",
        "SINGAPORE 308215",
        "REP. OF SINGAPORE",
    ]
)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("546080", True),
        ("018990", True),
        ("308215", True),
        ("54608", False),
        ("5460801", False),
        ("S546080", False),
        ("12345", False),
    ],
)
def test_postal_code(input, expected):
    execute_matching_test(input, expected, data_sg.postal_code)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("SINGAPORE", True),
        ("Singapore", True),
        ("singapore", True),
        ("Singaporean", False),
        ("REP. OF SINGAPORE", False),
    ],
)
def test_city(input, expected):
    execute_matching_test(input, expected, data_sg.city)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("REP. OF SINGAPORE", True),
        ("Rep of Singapore", True),
        ("Republic of Singapore", True),
        ("Singapore", False),
        ("United States", False),
    ],
)
def test_country(input, expected):
    execute_matching_test(input, expected, data_sg.country)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("16", True),
        ("35", True),
        ("776A", True),
        ("10", True),
        ("123456", False),
    ],
)
def test_street_number(input, expected):
    execute_matching_test(input, expected, data_sg.street_number)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Road", True),
        ("Avenue", True),
        ("Street", True),
        ("Lorong", True),
        ("Jalan", True),
        ("Rd", True),
        ("Ave", True),
        ("St", True),
        ("St.", True),
        ("Lor", True),
        ("Jln", True),
        ("Notatype", False),
    ],
)
def test_street_type(input, expected):
    execute_matching_test(input, expected, data_sg.street_type)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("#13-37", True),
        ("# 13-37", True),
        ("#06-20", True),
        ("#B1-15", True),
        ("#01-23A", True),
        ("#13-01/02", True),
        ("13-37", False),
        ("#13", False),
    ],
)
def test_occupancy(input, expected):
    execute_matching_test(input, expected, data_sg.occupancy)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("P.O. Box 123", True),
        ("PO Box 456", True),
        ("P.O.Box 12", True),
        ("Box 123", False),
    ],
)
def test_po_box(input, expected):
    execute_matching_test(input, expected, data_sg.po_box)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("16 Sandilands Road", True),
        ("Blk 35 Mandalay Road", True),
        ("Block 35 Mandalay Road", True),
        ("10 Eunos Road 8", True),
        ("53 Ang Mo Kio Avenue 3", True),
        ("776A Dunearn Road", True),
        ("Blk 145 Lorong 2 Toa Payoh", True),
        ("Lorong 24A Geylang", True),
        ("Jalan Besar", True),
        ("1 Jalan Besar", True),
        ("No. 16 Sandilands Road", True),
        ("12 St. Andrew's Road", True),
        ("#13-37 Mandalay Towers, Blk 35 Mandalay Road", True),
        ("10 Eunos Road 8, #06-20 Singapore Post Centre", True),
        ("P.O. Box 123", True),
        ("Blk 123 Ang Mo Kio Ave 3", True),
        ("Blk 201 Tampines St 21", True),
        ("Blk 1 Lor 2 Toa Payoh", True),
        ("12 Jln Besar", True),
        ("6 Raffles Boulevard, Marina Square, #02-01", True),
        ("3 Temasek Boulevard, Suntec City Mall", True),
        ("Mandalay", False),
    ],
)
def test_full_street(input, expected):
    execute_matching_test(input, expected, data_sg.full_street)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("16 Sandilands Road, SINGAPORE 546080", True),
        ("16 Sandilands Road SINGAPORE 546080", True),
        ("16 sandilands road, singapore 546080", True),
        (
            "Blk 35 Mandalay Road, #13-37 Mandalay Towers, SINGAPORE 308215",
            True,
        ),
        (UPU_BLOCK, True),
        (
            "10 Eunos Road 8, #06-20 Singapore Post Centre, Singapore 408600",
            True,
        ),
        (
            "10 Eunos Road 8 #06-20 Singapore Post Centre Singapore 408600",
            True,
        ),
        ("776A Dunearn Road, Singapore 289663", True),
        ("Blk 145 Lorong 2 Toa Payoh, Singapore 310145", True),
        ("Blk 145 Lorong 2 Toa Payoh Singapore 310145", True),
        ("53 Ang Mo Kio Avenue 3, Singapore 569933", True),
        ("1 Jalan Besar, Singapore 209001", True),
        ("Jalan Besar, Singapore 208878", True),
        ("Lorong 24A Geylang, Singapore 398614", True),
        ("No. 16 Sandilands Road, Singapore 546080", True),
        ("12 St. Andrew's Road, Singapore 178905", True),
        ("12 Upper Cross Street, Singapore 050002", True),
        ("P.O. Box 123, SINGAPORE 911234", True),
        ("PO Box 456\nSINGAPORE 912345", True),
        (
            "#13-37 Mandalay Towers, Blk 35 Mandalay Road, SINGAPORE 308215",
            True,
        ),
        (
            "10 Eunos Road 8, #06-20 Singapore Post Centre, "
            "Singapore 408600, REP. OF SINGAPORE",
            True,
        ),
        (
            "16 Sandilands Road, SINGAPORE 546080, Republic of Singapore",
            True,
        ),
        ("Blk 123 Ang Mo Kio Ave 3 #05-123 Singapore 560123", True),
        ("Blk 461 Clementi Ave 3, #01-123, Singapore 120461", True),
        ("30 Raffles Ave, Singapore 039803", True),
        ("Blk 35 Mandalay Rd, Singapore 308215", True),
        ("Blk 201 Tampines St 21, #03-45, Singapore 521201", True),
        ("Blk 1 Lor 2 Toa Payoh, Singapore 310001", True),
        ("12 Jln Besar, Singapore 208790", True),
        (
            "1 North Bridge Rd, #01-01 High Street Centre, Singapore 179094",
            True,
        ),
        (
            "238 Thomson Road, #13-01/02 Novena Square, Singapore 307683",
            True,
        ),
        (
            "8 Marina Boulevard, #05-02 Marina Bay Financial Centre Tower 1, "
            "Singapore 018981",
            True,
        ),
        ("6 Raffles Boulevard, Marina Square, #02-01, Singapore 039594", True),
        ("3 Temasek Boulevard, Suntec City Mall, Singapore 038983", True),
        ("260 Orchard Rd, The Heeren, #04-01, Singapore 238855", True),
        ("Singapore 2024", False),
        ("Singapore 546080", False),
        ("16 Sandilands Road, which we visited in Singapore 546080", False),
        ("16 Sandilands Road is near Singapore 546080", False),
        ("moved to Singapore last year", False),
        ("+65 6841 2000", False),
        ("Company number 123456", False),
        ("Blk 35 Mandalay Road", False),
        ("Jalan Besar is in Singapore 208878", False),
        ("Call 10 High Road about Singapore 123456", False),
        ("32 London Bridge St, London SE1 9SG", False),
        (
            "225 E. John Carpenter Freeway, Suite 1500 Irving, Texas 75062",
            False,
        ),
    ],
)
def test_full_address(input, expected):
    execute_matching_test(input, expected, data_sg.full_address)


def test_full_address_parts():
    example_addresses = [
        {
            "full_address": "16 Sandilands Road, SINGAPORE 546080",
            "street_number": "16",
            "street_name": "Sandilands",
            "street_type": "Road",
            "city": "SINGAPORE",
            "postal_code": "546080",
        },
        {
            "full_address": (
                "Blk 35 Mandalay Road, #13-37 Mandalay Towers, "
                "SINGAPORE 308215, REP. OF SINGAPORE"
            ),
            "street_number": "35",
            "street_name": "Mandalay",
            "street_type": "Road",
            "occupancy": "#13-37",
            "building_id": "Mandalay Towers",
            "city": "SINGAPORE",
            "postal_code": "308215",
            "country": "REP. OF SINGAPORE",
        },
        {
            "full_address": (
                "10 Eunos Road 8, #06-20 Singapore Post Centre, Singapore 408600"
            ),
            "street_number": "10",
            "street_name": "Eunos",
            "street_type": "Road",
            "route_id": "8",
            "occupancy": "#06-20",
            "building_id": "Singapore Post Centre",
            "city": "Singapore",
            "postal_code": "408600",
        },
        {
            "full_address": "776A Dunearn Road, Singapore 289663",
            "street_number": "776A",
            "street_name": "Dunearn",
            "street_type": "Road",
            "postal_code": "289663",
            "city": "Singapore",
        },
        {
            "full_address": "Blk 145 Lorong 2 Toa Payoh, Singapore 310145",
            "street_number": "145",
            "street_name": "Toa Payoh",
            "street_type": "Lorong",
            "route_id": "2",
            "city": "Singapore",
            "postal_code": "310145",
        },
        {
            "full_address": "53 Ang Mo Kio Avenue 3, Singapore 569933",
            "street_number": "53",
            "street_name": "Ang Mo Kio",
            "street_type": "Avenue",
            "route_id": "3",
            "city": "Singapore",
            "postal_code": "569933",
        },
        {
            "full_address": "Jalan Besar, Singapore 208878",
            "street_number": None,
            "street_name": "Besar",
            "street_type": "Jalan",
            "city": "Singapore",
            "postal_code": "208878",
        },
        {
            "full_address": "P.O. Box 123, SINGAPORE 911234",
            "po_box": "P.O. Box 123",
            "city": "SINGAPORE",
            "postal_code": "911234",
        },
        {
            "full_address": "Blk 123 Ang Mo Kio Ave 3 #05-123 Singapore 560123",
            "street_number": "123",
            "street_name": "Ang Mo Kio",
            "street_type": "Ave",
            "route_id": "3",
            "occupancy": "#05-123",
            "postal_code": "560123",
        },
        {
            "full_address": (
                "10 Anson Rd, #05-01 International Plaza, Singapore 079903"
            ),
            "street_number": "10",
            "street_name": "Anson",
            "street_type": "Rd",
            "occupancy": "#05-01",
            "building_id": "International Plaza",
            "postal_code": "079903",
        },
        {
            "full_address": (
                "6 Raffles Boulevard, Marina Square, #02-01, Singapore 039594"
            ),
            "street_number": "6",
            "street_name": "Raffles",
            "street_type": "Boulevard",
            "line2": "Marina Square, #02-01",
            "occupancy": "#02-01",
            "building_id": "Marina Square",
            "postal_code": "039594",
        },
        {
            "full_address": "3 Temasek Boulevard, Suntec City Mall, Singapore 038983",
            "street_number": "3",
            "street_type": "Boulevard",
            "occupancy": None,
            "building_id": "Suntec City Mall",
            "postal_code": "038983",
        },
        {
            "full_address": (
                "238 Thomson Road, #13-01/02 Novena Square, Singapore 307683"
            ),
            "street_number": "238",
            "occupancy": "#13-01/02",
            "building_id": "Novena Square",
            "postal_code": "307683",
        },
    ]
    filler_text = (
        "This is filler text that can be inserted both before and after addresses"
    )
    punctuation = ["\n", ", ", " "]

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
                parsed = parse(address_text, country="SG")
                assert len(parsed) == 1
                assert parsed[0].country_id == "SG"
                for key, value in address_parts.items():
                    if key == "full_address":
                        normalized = parser.AddressParser._normalize_string(value)
                        assert parsed[0].full_address == normalized
                    else:
                        assert parsed[0].__getattribute__(key) == value


def test_en_dash_unit_is_normalized():
    text = "Blk 35 Mandalay Road\n# 13\u201337 Mandalay Towers\nSINGAPORE 308215"
    parsed = parse(text, country="SG")
    assert len(parsed) == 1
    assert parsed[0].occupancy == "# 13-37"
    assert parsed[0].building_id == "Mandalay Towers"
    assert parsed[0].postal_code == "308215"
    assert parsed[0].street_number == "35"


@pytest.mark.parametrize(
    "text",
    [
        "10 Anson Xyz, #05-01 International Plaza, Singapore 079903",
        "238 Thomson Xyz, #13-01/02 Novena Square, Singapore 307683",
        "#05-01 International Plaza, Singapore 079903",
    ],
)
def test_no_match_starting_inside_unit_number(text):
    assert parse(text, country="SG") == []


def test_two_addresses_in_one_text():
    text = "16 Sandilands Road, SINGAPORE 546080\n" "10 Eunos Road 8, Singapore 408600"
    parsed = parse(text, country="SG")
    assert [item.postal_code for item in parsed] == ["546080", "408600"]


def test_parse_single_street():
    parsed = parse_single_street("Blk 35 Mandalay Road", country="SG")
    assert len(parsed) == 1
    assert parsed[0].full_street == "Blk 35 Mandalay Road"
    assert parsed[0].street_number == "35"
    assert parsed[0].street_name == "Mandalay"
    assert parsed[0].street_type == "Road"
    assert parsed[0].full_address == "Blk 35 Mandalay Road"


def test_no_address():
    assert parse("no address here", country="SG") == []
