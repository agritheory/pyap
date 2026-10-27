# -*- coding: utf-8 -*-

"""
    pyap.source_SG.data
    ~~~~~~~~~~~~~~~~~~~

    Regular expressions for Singapore postal addresses.

    A match needs a street (or a P.O. Box) and then the word Singapore
    beside a 6-digit postcode. SingPost assigns that code to the building.
    UPU examples:

        16 Sandilands Road
        SINGAPORE 546080

        Blk 35 Mandalay Road
        #13-37 Mandalay Towers
        SINGAPORE 308215
        REP. OF SINGAPORE

    Numbered streets keep the number on the type: ``10 Eunos Road 8``,
    ``53 Ang Mo Kio Avenue 3``. ``Lorong`` and ``Jalan`` lead the name:
    ``Blk 145 Lorong 2 Toa Payoh``, ``Jalan Besar``.

    :copyright: (c) 2015 by Vladimir Goncharov.
    :license: MIT, see LICENSE for more details.
"""

from pyap.source_US.data import (
    str_list_to_upper_lower_regex,
    street_type_list_to_regex,
)

part_divider = r"(?:[\,\ \.\-]{0,3}[\,\n][\,\ \.\-]{0,3})"
space_pattern = r"(?:[\ \t]{1,3})"
sep = rf"(?:{part_divider}|{space_pattern})"

street_type_list = [
    "Avenue",
    "Ave",
    "Boulevard",
    "Blvd",
    "Central",
    "Ctrl",
    "Circus",
    "Close",
    "Cl",
    "Crescent",
    "Cres",
    "Drive",
    "Dr",
    "Garden",
    "Gardens",
    "Gdns",
    "Green",
    "Grove",
    "Heights",
    "Highway",
    "Hwy",
    "Hill",
    "Jalan",
    "Jln",
    "Lane",
    "Ln",
    "Link",
    "Loop",
    "Lorong",
    "Lor",
    "Park",
    "Pk",
    "Path",
    "Place",
    "Pl",
    "Plain",
    "Plaza",
    "Quay",
    "Rise",
    "Road",
    "Rd",
    "Square",
    "Sq",
    "Street",
    "St",
    "Terrace",
    "Ter",
    "Turn",
    "View",
    "Vista",
    "Walk",
    "Way",
]

# These lead the street name. The others follow it.
leading_type_list = [
    "Jalan",
    "Jln",
    "Lorong",
    "Lor",
]

street_type_re = street_type_list_to_regex(street_type_list)
leading_type_re = street_type_list_to_regex(leading_type_list)

block_label = r"(?:" + str_list_to_upper_lower_regex(["Blk", "Block"]) + r")"

# Words that continue a sentence rather than a Lorong/Jalan name.
# "Jalan Besar is in Singapore 208878" must not become an address.
prose_words = [
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "last",
    "of",
    "on",
    "our",
    "the",
    "to",
    "was",
    "we",
    "were",
    "with",
    "year",
]
prose_word_re = str_list_to_upper_lower_regex(prose_words)

city_body = r"(?<![A-Za-z])" r"[Ss][Ii][Nn][Gg][Aa][Pp][Oo][Rr][Ee]" r"(?![A-Za-z])"

# Stop a name or building before "Singapore 546080" when they share a line.
not_city_postcode = r"(?!" + city_body + r"(?:" + sep + r")\d{6}(?!\d)" + r")"

name_word = not_city_postcode + r"[A-Za-z][A-Za-z0-9\.'\-&]*"
# Lazy: the street type follows, so take as few words as possible.
street_name_before_type = name_word + r"(?:" + space_pattern + name_word + r"){0,5}?"
# Greedy, but a prose word ends the name so the city has to come next.
leading_name_word = (
    not_city_postcode
    + r"(?!(?:"
    + prose_word_re
    + r")(?![A-Za-z]))"
    + r"[A-Za-z][A-Za-z0-9\.'\-&]*"
)
street_name_after_type = (
    leading_name_word + r"(?:" + space_pattern + leading_name_word + r"){0,3}"
)
# "Tower 1", "Block A": a short number may follow the first word.
building_number_word = r"\d{1,3}[A-Za-z]?(?![\w\-/])"
building_body = (
    name_word
    + r"(?:"
    + space_pattern
    + r"(?:"
    + building_number_word
    + r"|"
    + name_word
    + r")"
    + r"){0,6}"
)

# A building on its own line has no unit mark to anchor it, so each word
# must be capitalized and not a prose word ("The" may open the name).
building_line_word = (
    not_city_postcode
    + r"(?!(?:"
    + prose_word_re
    + r")(?![A-Za-z]))"
    + r"[A-Z][A-Za-z0-9\.'\-&]*"
)
building_line_body = (
    r"(?:[Tt][Hh][Ee]"
    + space_pattern
    + r")?"
    + building_line_word
    + r"(?:"
    + space_pattern
    + r"(?:"
    + building_number_word
    + r"|"
    + building_line_word
    + r")"
    + r"){0,6}"
)

postal_code_body = r"(?<![A-Za-z0-9])\d{6}(?![A-Za-z0-9])"

postal_code = r"""
    (?P<postal_code>
        {postal_code_body}
    )
""".format(
    postal_code_body=postal_code_body,
)

city = r"""
    (?P<city>
        {city_body}
    )
""".format(
    city_body=city_body,
)

country_body = (
    r"(?:[Rr][Ee][Pp]\.?|[Rr][Ee][Pp][Uu][Bb][Ll][Ii][Cc])"
    + space_pattern
    + r"[Oo][Ff]"
    + space_pattern
    + city_body
)

country = r"""
    (?P<country>
        {country_body}
    )
""".format(
    country_body=country_body,
)

street_number_body = r"\d{1,5}[A-Za-z]?(?!\d)"

street_number = r"""
    (?P<street_number>
        {street_number_body}
    )
""".format(
    street_number_body=street_number_body,
)

street_type = r"""
    (?P<street_type>
        {street_type_re}
    )
""".format(
    street_type_re=street_type_re,
)

occupancy_body = (
    r"\#"
    + space_pattern
    + r"?[A-Za-z]?\d{1,3}[A-Za-z]?"
    + space_pattern
    + r"?\-"
    + space_pattern
    + r"?\d{1,4}[A-Za-z]?"
    + r"(?:/\d{1,4}[A-Za-z]?)?"
)

occupancy = r"""
    (?P<occupancy>
        {occupancy_body}
    )
""".format(
    occupancy_body=occupancy_body,
)

po_box_body = (
    r"[Pp]\.?"
    + space_pattern
    + r"?[Oo]\.?"
    + space_pattern
    + r"?[Bb][Oo][Xx]"
    + space_pattern
    + r"?\d+"
)

po_box = r"""
    (?P<po_box>
        {po_box_body}
    )
""".format(
    po_box_body=po_box_body,
)

route_body = r"\d{1,3}[A-Za-z]?(?!\d)"


def make_unit_line(suffix: str) -> str:
    """Unit line ``#13-37`` plus an optional building name on that same line."""
    return r"""
        (?P<occupancy_{suffix}>
            {occupancy_body}
        )
        (?:
            {space}
            (?P<building_id_{suffix}>
                {building_body}
            )
        )?
    """.format(
        suffix=suffix,
        occupancy_body=occupancy_body,
        space=space_pattern,
        building_body=building_body,
    )


# ``10 Eunos Road 8`` / ``Blk 35 Mandalay Road`` / ``53 Ang Mo Kio Avenue 3``
street_order_follow = r"""
    (?:
        (?:{block_label}){space}?
    )?
    (?:
        [Nn][Oo]\.?{space}?
    )?
    (?P<street_number_a>
        {street_number_body}
    )
    {space}
    (?P<street_name_a>
        {street_name_before_type}
    )
    {space}?
    (?P<street_type_a>
        {street_type_re}
    )
    (?:
        {space}
        (?P<route_id_a>
            {route_body}
        )
    )?
""".format(
    block_label=block_label,
    space=space_pattern,
    street_number_body=street_number_body,
    street_name_before_type=street_name_before_type,
    street_type_re=street_type_re,
    route_body=route_body,
)

# ``Lorong 2 Toa Payoh`` / ``Jalan Besar`` / ``Blk 145 Lorong 2 Toa Payoh``
street_order_lead = r"""
    (?:
        (?:
            (?:{block_label}){space}?
        )?
        (?P<street_number_b>
            {street_number_body}
        )
        {space}
    )?
    (?P<street_type_b>
        {leading_type_re}
    )
    (?:
        {space}
        (?P<route_id_b>
            {route_body}
        )
    )?
    {space}
    (?P<street_name_b>
        {street_name_after_type}
    )
""".format(
    block_label=block_label,
    space=space_pattern,
    street_number_body=street_number_body,
    leading_type_re=leading_type_re,
    route_body=route_body,
    street_name_after_type=street_name_after_type,
)

full_street = r"""
    (?P<full_street>
        (?:
            (?:
                (?P<line2_a>
                    {unit_a}
                )
                {sep}
            )?
            (?P<line1>
                (?:
                    {street_order_follow}
                    |
                    {street_order_lead}
                )
            )
            (?:
                (?:
                    {part_divider}
                    (?P<line2_b>
                        (?P<building_id_d>
                            {building_line_body}
                        )
                        (?:
                            {sep}
                            {unit_c}
                        )?
                    )
                )
                |
                (?:
                    {sep}
                    (?P<line2_c>
                        {unit_b}
                    )
                )
            )?
            |
            (?P<line1_b>
                {po_box}
            )
        )
    )
""".format(
    unit_a=make_unit_line("a"),
    unit_b=make_unit_line("b"),
    unit_c=make_unit_line("c"),
    building_line_body=building_line_body,
    part_divider=part_divider,
    sep=sep,
    street_order_follow=street_order_follow,
    street_order_lead=street_order_lead,
    po_box=po_box,
)

# Never start right after "-", "/" or "#": "#05-01 International Plaza"
# would otherwise yield street number "01".
address_start = r"""
    (?:
        ^
        |
        (?<=[\s,;:\(\[\"'])
    )
    (?=
        \d{{1,5}}[A-Za-z]?(?!\d){space}[A-Za-z]
        |
        (?:{block_label}){space}?\d
        |
        \#
        |
        {leading_type_re}
        |
        [Nn][Oo]\.?{space}?\d
        |
        [Pp]\.?{space}?[Oo]
    )
""".format(
    space=space_pattern,
    block_label=block_label,
    leading_type_re=leading_type_re,
)

full_address = r"""
    {address_start}
    (?P<full_address>
        {full_street}
        {sep}
        (?P<city>
            {city_body}
        )
        {sep}
        (?P<postal_code>
            {postal_code_body}
        )
        (?:
            {sep}
            (?P<country>
                {country_body}
            )
        )?
    )
""".format(
    address_start=address_start,
    full_street=full_street,
    sep=sep,
    city_body=city_body,
    postal_code_body=postal_code_body,
    country_body=country_body,
)
