# pyright: reportPrivateUsage=false
# -*- coding: utf-8 -*-

"""
Tests for New Zealand address parser.

Address layouts follow the NZ Charities Register (odata.charities.govt.nz,
CC BY 3.0 NZ). Some fixtures are register rows; others are composed from real
New Zealand street, suburb and town names in the same layouts.
"""

import re
import time
import pytest
import itertools
from pyap import parser, utils, parse
import pyap.source_NZ.data as data_nz


def execute_matching_test(input, expected, pattern):
    match = utils.match(pattern, input, re.VERBOSE)
    is_found = match is not None
    if expected:
        assert is_found == expected
        assert match.group(0) == input  # type: ignore
    else:
        assert (is_found == expected) or (match.group(0) != input)  # type: ignore


unit_slash_pattern = r"(?P<slash>{})".format(data_nz.unit_slash)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("127A", True),
        ("7-13", True),
        ("114 - 118", True),
        ("5106", True),
        ("51066", True),
        ("510666", False),
    ],
)
def test_street_number(input, expected):
    execute_matching_test(input, expected, data_nz.street_number)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("2B/", True),
        ("13/", True),
    ],
)
def test_unit_slash(input, expected):
    execute_matching_test(input, expected, unit_slash_pattern)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Street", True),
        ("St", True),
        ("Road", True),
        ("Rd", True),
        ("Terrace", True),
        ("Tce", True),
        ("Quay", True),
        ("Line", True),
        ("Belt", True),
        ("Octagon", True),
        ("Xyz", False),
    ],
)
def test_street_type(input, expected):
    execute_matching_test(input, expected, data_nz.street_type)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Flat 12", True),
        ("Unit 10", True),
        ("Suite 406", True),
        ("Studio 5", True),
        ("FLAT 2", True),
    ],
)
def test_occupancy(input, expected):
    execute_matching_test(input, expected, data_nz.occupancy)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("Level 14", True),
        ("First Floor", True),
        ("L 5", True),
        ("1st Floor", True),
        ("LEVEL 3", True),
    ],
)
def test_floor(input, expected):
    execute_matching_test(input, expected, data_nz.floor)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("PO Box 13678", True),
        ("P.O. Box 292", True),
        ("P O Box 237", True),
        ("Private Bag 5902", True),
        ("CMB B19", True),
        ("Counter Delivery", True),
        ("Response Bag 97002", True),
        ("Poste Restante", True),
        ("PRIVATE BAG 5902", True),
        ("Private Bag 300 995", True),
    ],
)
def test_po_box(input, expected):
    execute_matching_test(input, expected, data_nz.po_box)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("RD 5", True),
        ("R.D.3", True),
        ("RD5", True),
    ],
)
def test_rural_delivery(input, expected):
    execute_matching_test(input, expected, data_nz.rural_delivery)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("6011", True),
        ("601", False),
        ("60111", False),
    ],
)
def test_postal_code(input, expected):
    match = utils.match(data_nz.postal_code, input, re.VERBOSE)
    if expected:
        assert match is not None
        assert match.group("postal_code") == input  # type: ignore
    else:
        assert match is None or match.group("postal_code") != input  # type: ignore


@pytest.mark.parametrize(
    "input,expected",
    [
        ("New Zealand", True),
        ("NZ", True),
        ("Aotearoa", True),
        ("Aotearoa New Zealand", True),
        ("Australia", False),
    ],
)
def test_country(input, expected):
    execute_matching_test(input, expected, data_nz.country)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("127A Abel Smith Street, Aro Valley, Wellington 6011", True),
        ("550A Finnis Road, RD 5, Pohangina, Feilding 4775", True),
        ("PO Box 13678, Armagh, Christchurch 8141", True),
        ("Private Bag 5902, Wellington Central, Wellington 6140", True),
        ("Level 14, 45 Johnston Street, Wellington Central, Wellington 6011", True),
        ("Flat 2, 184 Hastings Street East, Waltham, Christchurch 8023", True),
        ("13/143 Quay Street, Auckland Central, Auckland 1010", True),
        ("89 The Terrace, Wellington Central, Wellington 6011", True),
        ("296 State Highway 1, RD 12, Levin 5572", True),
        ("309 Durham Street North, Christchurch Central, Christchurch 8013", True),
        ("7-13 Pilkington Road, Panmure, Auckland 1072", True),
        ("30 Hilltop Road, Flat Bush, Auckland 2023", True),
        ("First Floor, 4 Canning Place, Whakatāne 3120", True),
        ("182 The Runway, Wigram, Christchurch 8042", True),
        ("203-271 Victoria Street West, Auckland Central, Auckland 1010", True),
        ("9541/17B Great South Road, Manukau, Auckland 2104", True),
        ("Ground Floor, 55 Shortland Street, Auckland Central, Auckland 1010", True),
        ("Shop 2, 123 Queen Street, Auckland Central, Auckland 1010", True),
        ("Response Bag 97002, South Dunedin, Dunedin 9044", True),
        ("Poste Restante, Wellington Central, Wellington 6011", True),
        ("Counter Delivery, Christchurch Central, Christchurch 8011", True),
        ("Private Bag 300 995, Shortland Street, Auckland 1140", True),
        ("5106 Danseys Pass Road, Omarama 9448", True),
        ("45 Victoria Street West, Lower Hutt 5010", True),
        ("123 Main Road, Upper Hutt 5018", True),
        (
            "127A Abel Smith Street, Aro Valley, Wellington 6011, New Zealand",
            True,
        ),
        ("127A Abel Smith Street, Aro Valley, Wellington 6011, Aotearoa", True),
        ("127A Abel Smith Street, Aro Valley, Wellington 6011, NZ", True),
        ("2B/54 Dominion Road, Mount Eden, Auckland 1024", True),
        ("Apartment 5, 10 Albert Street, Auckland Central, Auckland 1010", True),
        ("Level 3, 50 Manners Street, Wellington Central, Wellington 6011", True),
        ("CMB B19, Wellington Central, Wellington 6011", True),
        ("59 Beach Road, Parnell, Auckland 1052", True),
        ("1 George Street, Dunedin Central, Dunedin 9016", True),
        ("100 Clyde Street, Balclutha 9230", True),
        ("15 State Highway 2, Waihi 3610", True),
        ("1/2 Lambie Drive, Manukau, Auckland 2104", True),
        ("Suite 406, 85 The Terrace, Wellington Central, Wellington 6011", True),
        ("Building 2, 72 Taharoto Road, Takapuna, Auckland 0622", True),
        ("Unit 10, 14 Kent Street, Newmarket, Auckland 1023", True),
        ("L 5, 88 The Terrace, Wellington Central, Wellington 6011", True),
        ("PO Box 292, Wellington 6140", True),
        (
            "Private Bag 39997, Wellington Mail Centre, Wellington 5045",
            True,
        ),
        ("5 Ghuznee Street, Te Aro, Wellington 6011", True),
        ("10 Customhouse Quay, Wellington Central, Wellington 6011", True),
        ("550A Finnis Road, Pohangina, RD 5, Feilding 4775", True),
        ("296 State Highway 1, Levin 5572", True),
        ("114 - 118 Victoria Street West, Auckland Central, Auckland 1010", True),
        ("88 Cashel Street, Christchurch Central, Christchurch 8011", True),
        ("200 Tuam Street, Christchurch Central, Christchurch 8011", True),
        ("8 Māngere Road, Māngere Bridge, Auckland 2022", True),
        ("SH 1, RD 2, Taupo 3378", True),
        ("State Highway 2, RD 1, Katikati 3178", True),
        ("PRIVATE BAG 5902, WELLINGTON 6140", True),
        ("10 Main Street\nTe Aro\nWellington\n6011", True),
        ("5 Upper Queen Street, Auckland 1010", True),
        ("Corner Pitt and George Streets, Wellington 6011", False),
        ("PO Box 35391, Browns Bay 753", False),
        ("Auckland 2025", False),
        ("(09) 555 1234", False),
        ("021 123 4567", False),
        ("Cnr Broadway and Victoria Avenues, Palmerston North 4410", False),
        ("Wellington 6011", False),
        ("Pohangina, RD 5, Feilding 4775", False),
        ("R.D.5, Feilding 4775", False),
        ("12 staff, Auckland 1010", False),
        ("2023 Budget, Auckland 2023", False),
        ("Māngere Bridge, Auckland 2022", False),
        ("Care of John Smith, 1 Queen Street, Auckland 1010", False),
    ],
)
def test_full_address(input, expected):
    execute_matching_test(input, expected, data_nz.full_address)


def test_full_address_parts():
    example_addresses = [
        {
            "full_address": "127A Abel Smith Street, Aro Valley, Wellington 6011",
            "street_number": "127A",
            "street_name": "Abel Smith",
            "street_type": "Street",
            "sub_locality": "Aro Valley",
            "city": "Wellington",
            "postal_code": "6011",
        },
        {
            "full_address": "550A Finnis Road, RD 5, Pohangina, Feilding 4775",
            "street_number": "550A",
            "street_name": "Finnis",
            "street_type": "Road",
            "route_id": "RD 5",
            "sub_locality": "Pohangina",
            "city": "Feilding",
            "postal_code": "4775",
        },
        {
            "full_address": "PO Box 13678, Armagh, Christchurch 8141",
            "po_box": "PO Box 13678",
            "sub_locality": "Armagh",
            "city": "Christchurch",
            "postal_code": "8141",
        },
        {
            "full_address": "13/143 Quay Street, Auckland Central, Auckland 1010",
            "occupancy": "13",
            "street_number": "143",
            "street_name": "Quay",
            "street_type": "Street",
            "sub_locality": "Auckland Central",
            "city": "Auckland",
            "postal_code": "1010",
        },
        {
            "full_address": (
                "309 Durham Street North, Christchurch Central, Christchurch 8013"
            ),
            "street_number": "309",
            "street_name": "Durham",
            "street_type": "Street",
            "post_direction": "North",
            "sub_locality": "Christchurch Central",
            "city": "Christchurch",
            "postal_code": "8013",
        },
        {
            "full_address": (
                "Counter Delivery, Christchurch Central, Christchurch 8011"
            ),
            "po_box": "Counter Delivery",
            "sub_locality": "Christchurch Central",
            "city": "Christchurch",
            "postal_code": "8011",
        },
        {
            "full_address": "123 Main Road, Upper Hutt 5018",
            "street_number": "123",
            "street_name": "Main",
            "street_type": "Road",
            "sub_locality": None,
            "city": "Upper Hutt",
            "postal_code": "5018",
        },
        {
            "full_address": "45 Victoria Street West, Lower Hutt 5010",
            "street_name": "Victoria",
            "street_type": "Street",
            "post_direction": "West",
            "sub_locality": None,
            "city": "Lower Hutt",
            "postal_code": "5010",
        },
        {
            "full_address": "5106 Danseys Pass Road, Omarama 9448",
            "street_number": "5106",
            "street_name": "Danseys Pass",
            "street_type": "Road",
            "sub_locality": None,
            "city": "Omarama",
            "postal_code": "9448",
        },
        {
            "full_address": "5 Upper Queen Street, Auckland 1010",
            "street_name": "Upper Queen",
            "street_type": "Street",
            "sub_locality": None,
            "city": "Auckland",
        },
        {
            "full_address": "89 The Terrace, Wellington Central, Wellington 6011",
            "street_number": "89",
            "street_name": "The Terrace",
            "street_type": None,
            "sub_locality": "Wellington Central",
            "city": "Wellington",
        },
        {
            "full_address": "State Highway 2, RD 1, Katikati 3178",
            "street_number": None,
            "street_name": "State Highway 2",
            "route_id": "RD 1",
            "city": "Katikati",
            "postal_code": "3178",
        },
        {
            "full_address": "PRIVATE BAG 5902, WELLINGTON 6140",
            "po_box": "PRIVATE BAG 5902",
            "city": "WELLINGTON",
            "postal_code": "6140",
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

                parsed = parse(address_text, country="NZ")
                assert len(parsed) == 1
                for k, v in address_parts.items():
                    if k == "full_address":
                        assert parsed[
                            0
                        ].full_address == parser.AddressParser._normalize_string(v)
                    else:
                        assert parsed[0].__getattribute__(k) == v


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Our office moved to 127A Abel Smith Street, Aro Valley, "
            "Wellington 6011 last year",
            ["127A Abel Smith Street, Aro Valley, Wellington 6011"],
        ),
        (
            "Care of John Smith, 1 Queen Street, Auckland 1010",
            ["1 Queen Street, Auckland 1010"],
        ),
        (
            "Write to PO Box 1, Auckland 1140 or PO Box 2, Wellington 6140",
            ["PO Box 1, Auckland 1140", "PO Box 2, Wellington 6140"],
        ),
        ("We have 12 staff, Auckland 1010", []),
        ("In 2019 Street Fair, Auckland 1010", []),
        ("Room 5, 2023 Budget, Auckland 2023", []),
        ("Meet me at the office, Wellington 6011", []),
        ("Call (09) 555 1234 or 021 123 4567", []),
    ],
)
def test_parse_in_running_text(text, expected):
    assert [a.full_address for a in parse(text, country="NZ")] == expected


def test_parse_long_text_is_fast():
    paragraph = (
        "The Quarterly Report For The Board Of Directors Was Circulated To All "
        "Members, Including The Finance Committee And The Audit Group, Before "
        "The Meeting. "
    )
    text = paragraph * 200
    start = time.perf_counter()
    parsed = parse(text, country="NZ")
    elapsed = time.perf_counter() - start
    assert parsed == []
    assert elapsed < 5
