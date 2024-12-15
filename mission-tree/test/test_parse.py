import unittest
import parse
from parse import FieldTag

EXAMPLE = """# this is a comment
mission "Kestrel: More Weapons"
	landing
	invisible
	to offer
		has "kestrel: more weapons"
	on offer
		event "kestrel available: more weapons" 50
		fail



mission "Kestrel: More Engines"
	landing
	invisible
	to offer
		has "kestrel: more engines"
	on offer
		event "kestrel available: more engines" 50
		fail


"""


class TestParse(unittest.TestCase):
    def test_preprocess_lines(self):
        lines = EXAMPLE.split("\n")
        processed = parse.preprocess_lines(lines)
        self.assertEqual(
            processed,
            [
                (1, 0, 'mission "Kestrel: More Weapons"'),
                (2, 1, "landing"),
                (3, 1, "invisible"),
                (4, 1, "to offer"),
                (5, 2, 'has "kestrel: more weapons"'),
                (6, 1, "on offer"),
                (7, 2, 'event "kestrel available: more weapons" 50'),
                (8, 2, "fail"),
                (12, 0, 'mission "Kestrel: More Engines"'),
                (13, 1, "landing"),
                (14, 1, "invisible"),
                (15, 1, "to offer"),
                (16, 2, 'has "kestrel: more engines"'),
                (17, 1, "on offer"),
                (18, 2, 'event "kestrel available: more engines" 50'),
                (19, 2, "fail"),
            ],
        )

    def test_split_into_blocks(self):
        lines = EXAMPLE.split("\n")
        processed = parse.preprocess_lines(lines)
        blocks = parse.split_into_blocks(processed)
        self.assertEqual(
            blocks,
            [
                [
                    (1, 0, 'mission "Kestrel: More Weapons"'),
                    (2, 1, "landing"),
                    (3, 1, "invisible"),
                    (4, 1, "to offer"),
                    (5, 2, 'has "kestrel: more weapons"'),
                    (6, 1, "on offer"),
                    (7, 2, 'event "kestrel available: more weapons" 50'),
                    (8, 2, "fail"),
                ],
                [
                    (12, 0, 'mission "Kestrel: More Engines"'),
                    (13, 1, "landing"),
                    (14, 1, "invisible"),
                    (15, 1, "to offer"),
                    (16, 2, 'has "kestrel: more engines"'),
                    (17, 1, "on offer"),
                    (18, 2, 'event "kestrel available: more engines" 50'),
                    (19, 2, "fail"),
                ],
            ],
        )

    def test_parse_header(self):
        header = parse.LineText(1, 'mission "Kestrel: More Weapons"')
        parsed = parse.parse_block_header(header)
        self.assertEqual(parsed, (parse.BlockType.MISSION, ["Kestrel: More Weapons"]))

        header = parse.LineText(12, 'ship "Kestrel" "Kestrel (More Weapons)"')
        parsed = parse.parse_block_header(header)
        self.assertEqual(parsed, (parse.BlockType.SHIP, ["Kestrel", "Kestrel (More Weapons)"]))
    
    def test_parse_line(self):
        line = parse.LineText(7, 'on offer')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.ON_OFFER, []))

        line = parse.LineText(0, 'mission "Kestrel Testing"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.MISSION, ['Kestrel Testing']))

        line = parse.LineText(0, 'name "Warship Testing"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.NAME, ['Warship Testing']))

        line = parse.LineText(0, 'description "Travel to the <waypoints> system to fight and disable a prototype warship that Tarazed Corporation is testing. Do not destroy the ship, or you will lose your payment and your opportunity to buy one."')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.DESCRIPTION, ['Travel to the <waypoints> system to fight and disable a prototype warship that Tarazed Corporation is testing. Do not destroy the ship, or you will lose your payment and your opportunity to buy one.']))

        line = parse.LineText(0, 'source "Wayfarer"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.SOURCE, ['Wayfarer']))

        line = parse.LineText(0, 'waypoint "Umbral"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.WAYPOINT, ['Umbral']))

        line = parse.LineText(0, 'to offer')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.TO_OFFER, []))

        line = parse.LineText(0, 'or')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.OR, []))

        # line = parse.LineText(0, '"combat rating" > 6000')
        # parsed = parse.parse_line(line)
        # self.assertEqual(parsed, (None, ['"combat rating" > 6000']))

        line = parse.LineText(0, 'and')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.AND, []))

        line = parse.LineText(0, 'has "global: unlocked kestrel"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.HAS, ['global: unlocked kestrel']))

        line = parse.LineText(0, '`As you are visiting one of the spaceport`')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (None, ['`As you are visiting one of the spaceport`']))

        line = parse.LineText(0, 'payment 2000')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.PAYMENT, ['2000']))
