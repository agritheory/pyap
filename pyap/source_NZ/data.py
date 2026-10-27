# -*- coding: utf-8 -*-

"""
    pyap.source_NZ.data
    ~~~~~~~~~~~~~~~~~~~~~

    Regular expression definitions for detecting New Zealand addresses.

    Street types follow AS/NZS 4819 (New Zealand appendix) plus common NZ forms.

    New Zealand addresses carry no region, so the match is anchored on a street
    or delivery-service line and a required 4-digit postcode. A street line
    needs a street type unless it is a numbered "The X" road or a State
    Highway. A suburb (sub_locality) is only recognised between commas or
    newlines, so multi-word towns such as "Upper Hutt" stay whole. Every
    word-count quantifier is bounded so scanning long text stays linear.

    :copyright: (c) 2015 by Vladimir Goncharov.
    :license: MIT, see LICENSE for more details.
"""

import re

from pyap.source_US.data import street_type_list_to_regex

part_divider = r"(?:[\,\ \.\-]{0,3}[\,\n][\,\ \.\-]{0,3})"
space_pattern = r"(?:[\ \t]{1,3})"
line_end = rf"(?:{part_divider}|{space_pattern})"

# Latin-1 letters plus the Māori macron vowels.
upper = "A-ZÀ-ÖØ-ÞĀĒĪŌŪ"
lower = "a-zß-öø-ÿāēīōū"
letter = upper + lower
not_word_after = rf"(?![{letter}0-9'’])"


def any_case_regex(phrases):
    """Match each phrase in any letter case, trying longer phrases first."""
    alternatives = []
    for phrase in sorted(set(phrases), key=len, reverse=True):
        parts = []
        for char in phrase:
            if char.isalpha():
                parts.append(f"[{char.upper()}{char.lower()}]")
            elif char == " ":
                parts.append(r"\ ")
            else:
                parts.append(re.escape(char))
        alternatives.append("".join(parts))
    return "(?:" + "|".join(alternatives) + ")"


def title_or_upper_regex(phrases):
    """Match each phrase in Title Case or all capitals, not lower case."""
    forms = set()
    for phrase in phrases:
        forms.add(phrase)
        forms.add(phrase.upper())
    escaped = [form.replace(" ", r"\ ") for form in forms]
    return "(?:" + "|".join(sorted(escaped, key=len, reverse=True)) + ")"


street_type_list = [
    "Road",
    "Rd",
    "Street",
    "St",
    "Avenue",
    "Ave",
    "Drive",
    "Dr",
    "Place",
    "Pl",
    "Crescent",
    "Cres",
    "Terrace",
    "Tce",
    "Lane",
    "Close",
    "Cl",
    "Court",
    "Crt",
    "Way",
    "Grove",
    "Grv",
    "Parade",
    "Pde",
    "Quay",
    "Qy",
    "Esplanade",
    "Esp",
    "Square",
    "Sq",
    "Boulevard",
    "Blvd",
    "Line",
    "Belt",
    "Octagon",
    "Centre",
    "Center",
    "Parkway",
    "Pkwy",
    "Rise",
    "Track",
    "Trk",
    "Walk",
    "Wharf",
    "Whrf",
    "Mall",
    "Mews",
    "Loop",
    "Circle",
    "Cir",
    "Promenade",
    "Prom",
    "Alley",
    "Aly",
    "Arcade",
    "Arc",
    "Steps",
    "Stps",
    "Glade",
    "Gld",
    "Green",
    "Grn",
    "Runway",
    "Heights",
    "Gardens",
    "Ridge",
    "Point",
    "Cove",
    "Key",
    "End",
    "Row",
    "Strand",
    "Alleyway",
    "Alwy",
]

street_type_re = street_type_list_to_regex(street_type_list)

word = rf"(?:[{letter}][{letter}'’\-]*)"
words = rf"{word}(?:{space_pattern}{word}){{0,4}}?"

# Capitalised word, or a lower-case joining word inside a capitalised name.
cased_word = rf"(?:[{upper}][{letter}'’\-]*)"
particle = rf"(?:of|the|de|la|le|du|and|o|a|te|ki|&){not_word_after}"
cased_words = (
    rf"{cased_word}(?:{space_pattern}(?:{cased_word}|{particle})){{0,4}}?"
)

state_highway_body = rf"""
        (?:(?:[Ss]tate|STATE)\ (?:[Hh]ighway|HIGHWAY)|SH)
        {space_pattern}
        \d{{1,3}}[A-Za-z]?
        {not_word_after}
"""

street_number_body = r"""
        (?<![\.0-9])
        \d{1,5}[A-Za-z]?
        (?:\ ?-\ ?\d{1,5}[A-Za-z]?)?
        (?![0-9])
"""

street_number = rf"""
        (?P<street_number>
            {street_number_body}
        )
"""

street_type = rf"""
        (?P<street_type>
            {street_type_re}
        )
"""

# A numbered street may use any letter case ("89 the terrace"); an unnumbered
# one must be capitalised so ordinary prose does not start a match.
street_name_and_type = rf"""
        (?:
            (?(street_number)
                (?P<street_name_a>[Tt][Hh][Ee]{space_pattern}{word})
                (?={line_end})
            |
                (?!)
            )
            |
            (?P<street_name_b>{state_highway_body})
            |
            (?P<street_name_c>
                (?(street_number){words}|{cased_words})
            )
            {space_pattern}
            {street_type}
            {not_word_after}
        )
"""

post_direction_list = [
    "North",
    "South",
    "East",
    "West",
    "Upper",
    "Lower",
    "Extension",
]

post_direction = rf"""
        (?P<post_direction>
            {title_or_upper_regex(post_direction_list)}
            {not_word_after}
        )
"""

unit_slash = r"""
        (?P<occupancy_b>
            [A-Za-z]?\d{1,5}[A-Za-z]?
        )
        \ ?/\ ?
"""

flat_type_list = [
    "Unit",
    "Flat",
    "Apartment",
    "Apt",
    "Suite",
    "Ste",
    "Shop",
    "Studio",
    "Stu",
    "Townhouse",
    "Tnhs",
    "Room",
    "Office",
    "Lot",
    "Site",
    "Villa",
    "Warehouse",
    "Whse",
]

occupancy_body = rf"""
        (?:{any_case_regex(flat_type_list)}|U)
        {not_word_after}
        {space_pattern}
        (?:[A-Za-z]{{0,2}}\d{{1,5}}[A-Za-z]{{0,2}}|[A-Za-z])
        {not_word_after}
"""

occupancy = rf"""
        (?P<occupancy_a>
            {occupancy_body}
        )
"""

floor_body = rf"""
        (?:
            {any_case_regex(["First", "Ground", "Lower", "Upper", "Mezzanine"])}
            {space_pattern}
            {any_case_regex(["Floor"])}
            |
            \d{{1,2}}{any_case_regex(["st", "nd", "rd", "th"])}
            {space_pattern}
            {any_case_regex(["Floor"])}
            |
            (?:{any_case_regex(["Level", "Floor", "Lvl", "Fl"])}|L)
            {space_pattern}?
            \d{{1,3}}[A-Za-z]?
        )
        {not_word_after}
"""

floor = rf"""
        (?P<floor>
            {floor_body}
        )
"""

building_body = rf"""
        {any_case_regex(["Building", "Bldg"])}
        {space_pattern}
        \d{{1,4}}[A-Za-z]?
        {not_word_after}
"""

building = rf"""
        (?P<building_id>
            {building_body}
        )
"""

po_box_body = rf"""
        (?:
            (?:[Gg]\ ?)?[Pp]\.?\ ?[Oo]\.?\ ?[Bb][Oo][Xx]
            |
            {any_case_regex(["Private Bag", "Response Bag", "CMB"])}
        )
        {space_pattern}?
        [A-Za-z]{{0,3}}\d{{1,6}}[A-Za-z]{{0,2}}
        (?:{space_pattern}\d{{1,6}})?
        {not_word_after}
        |
        {any_case_regex(["Counter Delivery", "Poste Restante"])}
        {not_word_after}
"""

po_box = rf"""
        (?P<po_box>
            {po_box_body}
        )
"""

rural_delivery_body = rf"""
        (?:RD|R\.D\.)
        {space_pattern}?
        \d{{1,3}}
        {not_word_after}
"""

rural_delivery = rf"""
        (?P<route_id>
            {rural_delivery_body}
        )
"""

postal_code_body = rf"""
        (?<![{letter}0-9])
        \d{{4}}
        {not_word_after}
"""

postal_code = rf"""
        (?P<postal_code>
            {postal_code_body}
        )
"""

country_body = rf"""
        (?:
            {any_case_regex(["New Zealand"])}
            |
            {any_case_regex(["Aotearoa"])}
            (?:{space_pattern}{any_case_regex(["New Zealand"])})?
            |
            [Nn][Zz]
        )
        {not_word_after}
"""

country = rf"""
        (?P<country>
            {country_body}
        )
"""

city = rf"""
        (?P<city>
            {words}
            (?={line_end}{postal_code_body})
        )
"""

line1 = rf"""
        (?P<line1>
            (?:{unit_slash})?
            (?:{street_number}{space_pattern})?
            {street_name_and_type}
            (?:{space_pattern}{post_direction})?
        )
"""

line2 = rf"""
        (?P<line2>
            (?:{floor}{line_end})?
            (?:{occupancy}{line_end})?
            (?:{building}{line_end})?
        )
"""

full_street = rf"""
        (?P<full_street>
            {po_box}
            |
            {line2}
            {line1}
        )
"""

# The rural delivery number and the suburb may come in either order. A suburb
# must sit between commas or newlines.
locality = rf"""
        (?:
            {line_end}
            (?P<route_id_a>{rural_delivery_body})
            (?:
                {part_divider}
                (?P<sub_locality_a>{words})
                (?={part_divider})
            )?
            |
            {part_divider}
            (?P<sub_locality_b>{words})
            (?={part_divider})
            (?:
                {part_divider}
                (?P<route_id_b>{rural_delivery_body})
            )?
        )?
"""

full_address = rf"""
    (?<![{letter}0-9'’])
    (?P<full_address>
        {full_street}
        {locality}
        {line_end}
        {city}
        {line_end}
        {postal_code}
        (?:{line_end}{country})?
    )
"""
