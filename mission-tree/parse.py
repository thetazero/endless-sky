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
    print(block_type, tags)

    parser_map: dict[BlockType, Callable[[list[ParserNode], list[str], int], None]] = {
        BlockType.MISSION: parse_mission
    }
    if block_type in parser_map:
        parser_map[block_type](block.children, tags, block.line.line)
    else:
        pass
        # raise ParseError(f"Parser not implemented for block type: {block_type}")


def parse_mission(children: list[ParserNode], tags: list[str], start_line: int):
    assert (
        len(tags) == 1
    ), f"Invalid number of tags for mission: {tags} on line {start_line}"
    for child in children:
        print(child)
    pass


def parse_line(line: LineText) -> tuple[str, list[str]]:
    field = line.text.split(" ")[0]
    tags = line.text.split('"')[1:]
    tags = [tag for tag in tags if tag.strip() != ""]
    return field, tags


def parse_block_header(header: LineText) -> tuple[BlockType, list[str]]:
    """
    Parses the header of a block
    Format: block_type "block_name"
    or block_type "block_name" "block_description"
    """
    block_type, tags = parse_line(header)
    assert block_type in [
        b.value for b in BlockType
    ], f"Invalid block type: {block_type} on line {header.line}"
    block_type = BlockType(block_type)
    return block_type, tags


if __name__ == "__main__":
    parse("../data/human/kestrel.txt")
