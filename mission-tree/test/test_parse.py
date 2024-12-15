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

EXAMPLE2 = """
mission "Kestrel Testing"
	name "Warship Testing"
	on offer
		conversation
			`As you are visiting one of the spaceport bars, a man recognizes you. "<first> <last>!" he says. "It's an honor to meet you. Your exploits in battle are well known." He picks up his drink and walks over to sit next to you. "My name is Charles Atinoda," he says, "the chief starship designer for Tarazed Corporation. Say, would you be willing to help us test out a new warship?"`
			choice
				`	"Tell me more."`
				`	"Sorry, I don't have time right now."`
					defer
			`	"Well," he says, "here's the story. Seven years ago, in a time of deep personal crisis, I left my job at Tarazed to wander the galaxy with nothing in my backpack but a change of clothes, a canteen of water, and a few boxes of emergency rations. An anarchist commune on one of the fringe worlds took me in. After I had been there for a month, the village elder, sensing my inner turmoil, invited me to a vision quest in their sweat lodge. I fell into a trance and my consciousness journeyed through many universes, where I saw strange things. I saw a sword made of light. I saw a blue sun. I saw..." He pauses for a moment. "... a Welsh Corgi hacking into a computer? Some of it was hard to understand."`
			choice
	on complete
		payment 2000000
		"global: unlocked kestrel" ++
		conversation
			`Atinoda meets up with you soon after you land. "I see that you survived," he says. "Was it a difficult fight?"`
			choice
				`	"Yes, you have built an impressive ship."`
					goto yes
				`	"No, I'm afraid I made short work of it."`
					goto no
			
			label yes
			`	"Glad to hear it," he says. "Now, we have the opportunity to make a few tweaks before we start mass-producing this ship. What changes would you recommend?"`
				goto changes
			
			label no
			`	"Oh well," he says, "you are the infamous <first> <last>, after all, so I suppose any single warship will be little threat to you. Now, we have the opportunity to make a few tweaks before we start mass-producing this ship. What changes would you recommend?"`
				goto changes
			
			label changes
			choice
				`	"Lots of weapon space is always my first priority."`
					goto weapons
				`	"You should make sure it has enough space for any engine."`
					goto engines
				`	"Maybe you should work on improving the shields and hull."`
					goto shields
				`	"I feel like such a large ship should have more bays for fighters."`
					goto bays
			
			label weapons
			action
				set "kestrel: more weapons"
			`	"Very well," he says, "we'll see if we can expand the weapon capacity so that even the biggest weapons will fit."`
				goto name
			
			label engines
			action
				set "kestrel: more engines"
			`	"Very well," he says, "we'll see if we can expand the engine capacity enough that even the biggest engines will fit."`
				goto name
			
			label shields
			action
				set "kestrel: more shields"
			`	"Okay," he says, "we'll focus on strengthening the hull and the shield matrix."`
				goto name
			
			label bays
			action
				set "kestrel: more bays"
			`	"Very well," he says, "we'll see if we can incorporate more fighter bays into the hull."`
				goto name
			
			label name
			`	"Does the ship model have a name yet?" you ask.`
			`	"Not yet," he says. "Do you have a suggestion?"`
			choice
				`	"The Wraith."`
					goto wraith
				`	"The Grey Goose."`
					goto goose
			
			label wraith
			`	"Not a bad name, I suppose," he says, "but at Tarazed we usually name our ships after animals. Any other ideas?"`
			choice
				`	"The Dire Wolf."`
					goto wolf
				`	"The Kestrel."`
					goto kestrel
			
			label goose
			`	"I suppose it does sort of look like a goose in flight," he says, "but that's hardly an intimidating name. Do you have any scarier ideas?"`
			choice
				`	"The Reaper."`
					goto reaper
				`	"The Kestrel."`
					goto kestrel
			
			label wolf
			`	"Not bad," he says, "but all our other ships - the Falcon, the Osprey, the Hawk - they're all birds. Maybe a bird name?"`
			choice
				`	"The Grey Goose."`
					goto goose
				`	"The Kestrel."`
					goto kestrel
			
			label reaper
			`	"I don't know," he says, "that sounds a little bit over the top. Any other suggestions?"`
			choice
				`	"The Wraith."`
					goto wraith
				`	"The Kestrel."`
					goto kestrel
			
			label kestrel
			`	When you say the word 'Kestrel' he jerks as if he's just been electrocuted. "Yes," he says, "that's it! That's the name we'll go with. Thank you, Captain. I will let you know as soon as the Kestrel is available for sale, and we will take your recommendations into account when making our final modifications to the design." He pays you two million credits and wishes you the best of luck in your future endeavors.`
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
        self.assertEqual(
            parsed, (parse.BlockType.SHIP, ["Kestrel", "Kestrel (More Weapons)"])
        )

    def test_parse_line(self):
        line = parse.LineText(7, "on offer")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.ON_OFFER, []))

        line = parse.LineText(0, 'mission "Kestrel Testing"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.MISSION, ["Kestrel Testing"]))

        line = parse.LineText(0, 'name "Warship Testing"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.NAME, ["Warship Testing"]))

        line = parse.LineText(
            0,
            'description "Travel to the <waypoints> system to fight and disable a prototype warship that Tarazed Corporation is testing. Do not destroy the ship, or you will lose your payment and your opportunity to buy one."',
        )
        parsed = parse.parse_line(line)
        self.assertEqual(
            parsed,
            (
                FieldTag.DESCRIPTION,
                [
                    "Travel to the <waypoints> system to fight and disable a prototype warship that Tarazed Corporation is testing. Do not destroy the ship, or you will lose your payment and your opportunity to buy one."
                ],
            ),
        )

        line = parse.LineText(0, 'source "Wayfarer"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.SOURCE, ["Wayfarer"]))

        line = parse.LineText(0, 'waypoint "Umbral"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.WAYPOINT, ["Umbral"]))

        line = parse.LineText(0, "to offer")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.TO_OFFER, []))

        line = parse.LineText(0, "or")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.OR, []))

        # line = parse.LineText(0, '"combat rating" > 6000')
        # parsed = parse.parse_line(line)
        # self.assertEqual(parsed, (None, ['"combat rating" > 6000']))

        line = parse.LineText(0, "and")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.AND, []))

        line = parse.LineText(0, 'has "global: unlocked kestrel"')
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.HAS, ["global: unlocked kestrel"]))

        line = parse.LineText(0, "`As you are visiting one of the spaceport`")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (None, ["`As you are visiting one of the spaceport`"]))

        line = parse.LineText(0, "payment 2000")
        parsed = parse.parse_line(line)
        self.assertEqual(parsed, (FieldTag.PAYMENT, ["2000"]))

    def test_parse_example_2(self):
        input = EXAMPLE2.split("\n")
        processed = parse.parse_lines(input)
        self.assertEqual(len(processed), 1)
        mission = processed[0]
        self.assertIsInstance(mission, parse.Mission)
        self.assertIsInstance(mission.on_complete, parse.OnComplete)
        self.assertIsInstance(mission.on_complete.events[0], parse.Event)
        # self.assertEqual(mission.name, "Warship Testing")
