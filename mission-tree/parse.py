from enum import Enum
from typing import Callable, Optional, NamedTuple


class LineText(NamedTuple):
    line: int
    text: str


class ParseError(ValueError):
    pass


class BlockType(Enum):
    MISSION = "mission"
    SHIPYARD = "shipyard"
    EVENT = "event"
    SHIP = "ship"

class FieldTag(Enum):
    DESCRIPTION = "description"
    EVENT = "event"
    MISSION = "mission"
    NAME = "name"
    ON_OFFER = "on offer"
    SHIP = "ship"
    SHIPYARD = "shipyard"   
    SOURCE = "source"
    TO_OFFER = "to offer"
    WAYPOINT = "waypoint"
    OR = "or"
    AND = "and"
    HAS = "has"
    ON_COMPLETE = "on complete"
    PAYMENT = "payment"


def parse(file: str):
    with open(file, "r") as f:
        lines = f.readlines()

    lines = preprocess_lines(lines)
    block_data = split_into_blocks(lines)
    blocks = [parse_block_to_nodes(block) for block in block_data]
    blocks = [parse_node(node) for node in blocks]
    return blocks


def preprocess_lines(lines: list[str]) -> list[tuple[int, int, str]]:
    """
    Preprocesses lines to include line number and number of tabs
    Returns a list of tuples in the form of (line_number, num_tabs, line)
    """
    data: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        if line.strip().startswith("#") or line.strip() == "":
            continue
        num_tabs = 0
        for s in line:
            if s == "\t":
                num_tabs += 1
            else:
                break
        data.append((i, num_tabs, line.strip()))
    return data


def split_into_blocks(
    data: list[tuple[int, int, str]]
) -> list[list[tuple[int, int, str]]]:
    """
    Splits the data into blocks of related lines
    """
    blocks: list[list[tuple[int, int, str]]] = []
    current_block: list[tuple[int, int, str]] = []
    for line in data:
        num_tabs = line[1]
        if num_tabs == 0 and current_block:
            blocks.append(current_block)
            current_block = []
        current_block.append(line)
    if current_block:
        blocks.append(current_block)
    return blocks


class ParserNode:
    line: LineText
    """
    line_number, line_text
    """
    children: list["ParserNode"]
    """
    List of child ParserNodes
    """

    def __init__(
        self,
        line_data: LineText,
        children: list["ParserNode"],
        depth: int,
        parent: Optional["ParserNode"] = None,
    ):
        self.line = line_data
        self.children = children
        self.parent = parent
        self.depth = depth
        assert all(
            [child.depth == depth - 1 for child in children]
        ), "All children must have 1 less depth"

    def __str__(self) -> str:
        return f"<ParserNode: {self.line} [{len(self.children)}]>"


def parse_block_to_nodes(block: list[tuple[int, int, str]]) -> ParserNode:
    """
    Block is a list of tuples in the form of (line_number, num_tabs, line)

    Returns a tree of ParserNodes
    """
    root = ParserNode(LineText(block[0][0], block[0][2]), [], block[0][1])
    current_node = root
    current_depth = 1
    for line in block[1:]:
        assert isinstance(current_node, ParserNode)
        line_number, num_tabs, line_text = line
        if num_tabs > current_depth:
            current_node = current_node.children[-1]
        elif num_tabs < current_depth:
            for _ in range(current_depth - num_tabs):
                assert current_node.parent is not None
                current_node = current_node.parent
        current_node.children.append(
            ParserNode(
                LineText(line_number, line_text), [], num_tabs, parent=current_node
            )
        )
        current_depth = num_tabs
    return root


def parse_node(block: ParserNode):
    """
    Block is a list of tuples in the form of (line_number, num_tabs, line)
    """
    block_type, tags = parse_block_header(block.line)

    parser_map: dict[
        BlockType, Callable[[list[ParserNode], list[str], int], Mission]
    ] = {BlockType.MISSION: parse_mission}
    if block_type in parser_map:
        return parser_map[block_type](block.children, tags, block.line.line)
    else:
        pass
        # raise ParseError(f"Parser not implemented for block type: {block_type}")


class Has:
    condition: str

    def __init__(self, condition: str):
        self.condition = condition

    def __str__(self) -> str:
        return f"<Has: {self.condition}>"


class ToOffer:
    has: Optional[Has]

    def __init__(self):
        self.has = None
        pass

    def __str__(self) -> str:
        return f"<ToOffer has: {self.has}>"


class OnComplete:

    def __init__(self):
        pass

    def __str__(self) -> str:
        return f"<OnComplete>"


class Payment:

    amount: int

    def __init__(self, amount: int):
        self.amount = amount


class Mission:
    to_offer: ToOffer
    id: str
    on_complete: Optional[OnComplete]

    def __init__(self, id: str):
        self.id = id


def parse_has(node: ParserNode) -> Has:
    field, tags = parse_line(node.line)
    assert field == FieldTag.HAS
    assert len(tags) == 1
    return Has(tags[0])


def parse_on_offer(node: ParserNode) -> ToOffer:
    res = ToOffer()
    for child in node.children:
        field, tags = parse_line(child.line)
        if field == FieldTag.HAS:
            res.has = parse_has(child)
    return res


def parse_on_complete(node: ParserNode) -> OnComplete:
    res = OnComplete()
    for child in node.children:
        field, tags = parse_line(child.line)
        print(field, tags)
        if field == FieldTag.PAYMENT:
            pass
    return res


def parse_mission(children: list[ParserNode], tags: list[str], start_line: int):
    assert (
        len(tags) == 1
    ), f"Invalid number of tags for mission: {tags} on line {start_line}"
    res = Mission(tags[0])
    for child in children:
        field, tags = parse_line(child.line)
        if field == FieldTag.TO_OFFER:
            res.to_offer = parse_on_offer(child)
        elif field == FieldTag.ON_COMPLETE:
            res.on_complete = parse_on_complete(child)
        else:
            pass

    return res


def parse_line(line: LineText) -> tuple[Optional[FieldTag], list[str]]:
    for tag in FieldTag:
        if line.text.startswith(tag.value):
            field = tag
            remaining = line.text[len(tag.value) + 1 :]
            tags = remaining.split('"')[1:]
            if len(tags) == 0 and remaining.strip() != "":
                tags = [remaining]
            elif len(tags) == 0:
                tags = []
            else:
                tags = [tag for tag in tags if tag.strip() != ""]
            return field, tags 
    return None, [line.text]


def parse_block_header(header: LineText) -> tuple[BlockType, list[str]]:
    """
    Parses the header of a block
    Format: block_type "block_name"
    or block_type "block_name" "block_description"
    """
    block_type, tags = parse_line(header)
    assert isinstance(block_type, FieldTag)
    block_type = BlockType(block_type.value)
    return block_type, tags
