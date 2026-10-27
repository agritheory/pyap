# -*- coding: utf-8 -*-

"""
    pyap.source_IE.data
    ~~~~~~~~~~~~~~~~~~~

    Regular expression definitions for detecting Irish (Republic of Ireland)
    postal addresses.

    Street-type vocabulary is hand-curated; there is no open national list
    comparable to Geoscape G-NAF.

    A match starts at a structural cue (street number, unit, floor, PO box),
    at the start of a line, or at a short capitalised line followed by a
    comma. Every quantifier is bounded so scanning long text stays linear.

    The region must be one of: a "Co."/"County" county, a numbered Dublin
    district, or a bare county / "Dublin" followed by an Eircode. A bare
    county on its own ("Thanks, Kerry") is not an address.

    :copyright: (c) 2015 by Vladimir Goncharov.
    :license: MIT, see LICENSE for more details.
"""

from pyap.source_US.data import str_list_to_upper_lower_regex, street_type_list_to_regex

part_divider = r"(?:[\,\ \.\-]{0,3}[\,\n][\,\ \.\-]{0,3})"
space_pattern = r"(?:[\ \t]{1,3})"

upper = "A-ZÀ-ÖØ-Þ"
lower = "a-zß-öø-ÿ"
letter = upper + lower
not_word_after = rf"(?![{letter}0-9'’])"

# Hand-curated Irish / English thoroughfare types (full words and common abbrevs).
street_type_list = [
    "Street",
    "St",
    "Road",
    "Rd",
    "Avenue",
    "Ave",
    "Drive",
    "Dr",
    "Lane",
    "Ln",
    "Close",
    "Court",
    "Ct",
    "Crescent",
    "Cres",
    "Grove",
    "Park",
    "Place",
    "Pl",
    "Square",
    "Sq",
    "Terrace",
    "Tce",
    "Way",
    "View",
    "Lawn",
    "Lawns",
    "Green",
    "Heights",
    "Hill",
    "Rise",
    "Walk",
    "Quay",
    "Row",
    "Mall",
    "Gardens",
    "Gdns",
    "Downs",
    "Manor",
    "Wood",
    "Vale",
    "Glen",
    "Boulevard",
    "Blvd",
    "Esplanade",
    "Mews",
    "Mount",
    "Mt",
]

county_name_list = [
    "Carlow",
    "Cavan",
    "Clare",
    "Cork",
    "Donegal",
    "Dublin",
    "Galway",
    "Kerry",
    "Kildare",
    "Kilkenny",
    "Laois",
    "Leitrim",
    "Limerick",
    "Longford",
    "Louth",
    "Mayo",
    "Meath",
    "Monaghan",
    "Offaly",
    "Roscommon",
    "Sligo",
    "Tipperary",
    "Waterford",
    "Westmeath",
    "Wexford",
    "Wicklow",
]


def county_name_regex(names):
    """Match a county in Title Case or all capitals, not mixed or lower case."""
    forms = set()
    for name in names:
        forms.add(name)
        forms.add(name.upper())
    return "(?:" + "|".join(sorted(forms, key=len, reverse=True)) + ")"


# A bare county name is only a region when written "Cork" or "CORK"; lowercase
# "cork" in prose is not. After "Co." / "County" any case is accepted.
counties_bare_re = county_name_regex(
    [name for name in county_name_list if name != "Dublin"]
)
counties_any_case_re = "(?:" + str_list_to_upper_lower_regex(county_name_list) + ")"
street_type_re = street_type_list_to_regex(street_type_list)

word = rf"(?:[{letter}][{letter}0-9'’]*|&)"
word_sep = r"[\ \.\-]{1,3}"

# One comma-separated address line: at most six words.
line_words = rf"{word}(?:{word_sep}{word}){{0,5}}"
short_line = rf"{word}(?:{word_sep}{word}){{0,3}}"

# Capitalised word, or an Irish eclipsed / h-prefixed word ("hAbhann", "tSráid").
cased_word = rf"(?:[{upper}][{letter}0-9'’]*|[{lower}]{{1,2}}[{upper}][{letter}'’]*)"
particle = rf"(?:na|an|de|le|la|of|the|and|on|in|a|ar|ag|y|du|&){not_word_after}"
cased_line = rf"{cased_word}(?:{word_sep}(?:{cased_word}|{particle})){{0,3}}"

postal_code_body = r"""
            (?<![A-Za-z0-9])
            (?:
                [Dd]6[Ww]
                |
                [ACDEFHKNPRTVWXYacdefhknprtvwxy][0-9]{2}
            )
            \ ?
            [0-9ACDEFHKNPRTVWXYacdefhknprtvwxy]{4}
            (?![A-Za-z0-9])
"""

postal_code = rf"""
        (?P<postal_code>
            {postal_code_body}
        )
"""

country_body = rf"""
        (?:
            (?:[Rr][Ee][Pp][Uu][Bb][Ll][Ii][Cc]\ [Oo][Ff]\ )?[Ii][Rr][Ee][Ll][Aa][Nn][Dd]
            |
            [EeÉé][Ii][Rr][Ee]
        )
        {not_word_after}
"""

country = rf"""
        (?P<country>
            {country_body}
        )
"""

dublin_district_num = rf"""
        [Dd][Uu][Bb][Ll][Ii][Nn]
        {space_pattern}
        (?:6[Ww]|1[0-8]|20|22|24|[1-9])
        (?![{letter}0-9])
"""

# Bare "Dublin" is not a region when another word follows ("DUBLIN ROAD",
# "DUBLIN IND ESTATE"), unless that word is the country or an Eircode.
dublin_bare = rf"""
        (?:Dublin|DUBLIN)
        {not_word_after}
        (?!{space_pattern}(?!(?:{country_body})|(?:{postal_code_body})){word})
"""

dublin_any = rf"(?:(?:{dublin_district_num})|(?:{dublin_bare}))"

co_prefix_region = rf"""
        (?:[Cc][Oo]\.?{space_pattern}|[Cc][Oo][Uu][Nn][Tt][Yy]{space_pattern})
        {counties_any_case_re}
        {not_word_after}
"""

county_bare = rf"""
        {counties_bare_re}
        {not_word_after}
        (?![\ \t]*(?:{street_type_re}))
        (?:[\ \t]*,[\ \t]*{counties_bare_re}{not_word_after})?
"""

region1_body = rf"""
        (?:
            (?:{dublin_district_num})
            |
            (?:{co_prefix_region})
            |
            (?:{dublin_bare})
            |
            (?:{county_bare})
        )
"""

region1 = rf"""
        (?P<region1>
            {region1_body}
        )
"""

# A comma-separated chunk that is itself the county/district, not a street line.
region_segment = rf"""
        {region1_body}
        (?=
            {part_divider}
            |
            {space_pattern}(?:{postal_code_body})
            |
            {space_pattern}(?:{country_body})
            |
            [\ \t\.]*\Z
        )
"""

street_number_body = rf"""
        \d{{1,4}}[A-Za-z]?
        (?:{space_pattern}?\-\ ?\d{{1,4}}[A-Za-z]?)?
        (?:{space_pattern}?/\ ?\d{{1,4}}[A-Za-z]?)?
"""

street_number = rf"""
        (?P<street_number>
            {street_number_body}
        )
"""

street_name = rf"""
        (?P<street_name>
            {line_words}
        )
"""

street_type = rf"""
        (?P<street_type>
            {street_type_re}
        )
"""

occupancy_body = rf"""
        (?:
            [Uu][Nn][Ii][Tt]|[Ff][Ll][Aa][Tt]|[Aa][Pp][Tt]\.?|
            [Aa][Pp][Aa][Rr][Tt][Mm][Ee][Nn][Tt]|[Ss][Uu][Ii][Tt][Ee]|[Ss][Tt][Ee]\.?
        )
        {space_pattern}
        [A-Za-z0-9][A-Za-z0-9\-/]{{0,15}}
"""

occupancy = rf"""
        (?P<occupancy>
            {occupancy_body}
        )
"""

floor_body = rf"""
        (?:
            (?:
                [Ff][Ii][Rr][Ss][Tt]|[Gg][Rr][Oo][Uu][Nn][Dd]|[Ll][Oo][Ww][Ee][Rr]|
                [Uu][Pp][Pp][Ee][Rr]|[Mm][Ee][Zz][Zz][Aa][Nn][Ii][Nn][Ee]
            )
            {space_pattern}?
            [Ff][Ll][Oo][Oo][Rr]
            |
            [Ff][Ll][Oo][Oo][Rr]{space_pattern}?\d{{1,3}}[A-Za-z]?
            |
            \d{{1,2}}(?:[Ss][Tt]|[Nn][Dd]|[Rr][Dd]|[Tt][Hh]){space_pattern}?[Ff][Ll][Oo][Oo][Rr]
            |
            [Ll][Ee][Vv][Ee][Ll]{space_pattern}?\d{{1,3}}[A-Za-z]?
        )
        {not_word_after}
"""

floor = rf"""
        (?P<floor>
            {floor_body}
        )
"""

building_body = rf"""
        [{letter}0-9][{letter}0-9\ \.\-'’&]{{0,40}}
        {space_pattern}?
        (?:
            [Hh][Oo][Uu][Ss][Ee]|[Hh][Aa][Ll][Ll]|[Cc][Ee][Nn][Tt][Rr][Ee]|
            [Tt][Oo][Ww][Ee][Rr]|[Ll][Oo][Dd][Gg][Ee]|[Mm][Aa][Nn][Ss][Ii][Oo][Nn]
        )
        {not_word_after}
"""

building = rf"""
        (?P<building_id>
            {building_body}
        )
"""

po_box_body = rf"""
        [Pp]\.?\ ?[Oo]\.?\ ?[Bb][Oo][Xx]{space_pattern}?\d{{1,6}}
"""

po_box = rf"""
        (?P<po_box>
            {po_box_body}
        )
"""

line1 = rf"""
        (?P<line1>
            (?:\d{{1,4}}[A-Za-z]?{space_pattern}?/\ ?)?
            (?:{street_number}{space_pattern}?)?
            {street_name}
            (?:{space_pattern}{street_type})?
        )
"""

line_end = rf"(?:{part_divider}|{space_pattern})"

full_street = rf"""
        (?P<full_street>
            (?P<line2>
                (?:{po_box}{line_end}?)?
                (?:{floor}{line_end}?)?
                (?:{occupancy}{line_end}?)?
                (?:{building}{line_end}?)?
            )
            (?:{cased_line}{part_divider}(?=\d))?
            {line1}
        )
"""

# A non-street line between the street and the region: locality, district,
# or a CRO-style "ROAD SWORDS CO. DUBLIN" / "NAAS KILDARE W91 R620" line.
address_line = rf"""
        (?:{street_number_body}{space_pattern}?)?
        {line_words}
        (?:{space_pattern}(?:{dublin_district_num}))?
        (?:{space_pattern}\d{{1,2}}\.?)?
        (?:{space_pattern}(?:{postal_code_body}))?
"""

# Checked just before the region: a bare county or bare "Dublin" must be
# followed (after any repeated region, locality, or country) by an Eircode.
region_evidence = rf"""
        (?=
            (?:{co_prefix_region})
            |
            (?:{dublin_district_num})
            |
            {region1_body}
            (?:{line_end}{region1_body}){{0,2}}
            (?:{part_divider}{address_line}{part_divider}?{dublin_any})?
            (?:{part_divider}{counties_bare_re}{not_word_after})?
            (?:{line_end}(?:{country_body}))?
            {line_end}(?:{postal_code_body})
        )
"""

address_tail = rf"""
        (?:{part_divider}(?!{region_segment}){address_line}){{0,3}}?
        (?:{part_divider}(?!{region_segment})(?P<city>{address_line}))?
        {line_end}
        {region_evidence}
        {region1}
        (?:{line_end}{region1_body}){{0,2}}
        (?:{part_divider}{address_line}{part_divider}?{dublin_any})?
        (?:{part_divider}{counties_bare_re}{not_word_after})?
        (?:{line_end}{postal_code})?
        (?:{line_end}{country})?
        (?:
            {part_divider}
            (?:{address_line}{part_divider})?
            {region1_body}
            (?:{line_end}(?:{postal_code_body}))?
        )?
        (?:{line_end}(?:{postal_code_body}))?
"""

address_start = rf"""
        (?<![{letter}0-9'’])
        (?:
            (?=\d)
            |
            (?={po_box_body})
            |
            (?={floor_body})
            |
            (?={occupancy_body})
            |
            (?={cased_line}{part_divider})
            |
            (?<![^\n])(?={short_line}{part_divider})
        )
"""

full_address = rf"""
    {address_start}
    (?P<full_address>
        {full_street}
        {address_tail}
    )
"""
