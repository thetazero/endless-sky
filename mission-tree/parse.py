from enum import Enum
from typing import Callable, Optional


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
    return blocks

def preprocess_lines(
    lines: list[str]
) -> list[tuple[int, int, str]]:
    """
    Preprocesses lines to include line number and number of tabs 
    Returns a list of tuples in the form of (line_number, num_tabs, line)
    """
    data: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        if line.startswith("#") or line.strip() == "":
            continue
        num_tabs = 0
        for s in line:
            if s == "\t":
                num_tabs+=1
            else:
                break
        data.append((i, num_tabs, line.strip()))
    return data

def split_into_blocks(data: list[tuple[int, int, str]]) -> list[list[tuple[int, int, str]]]:
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


def parse_block_header(header: tuple[int, int, str]) -> tuple[BlockType, list[str]]:
    """
    Parses the header of a block
    Format: block_type "block_name"
    or block_type "block_name" "block_description"
    """
    line_number, _, header_text = header
    block_type = header_text.split(" ")[0]
    tags = header_text.split("\"")[1:]
    assert block_type in [b.value for b in BlockType], f"Invalid block type: {block_type} on line {line_number}"
    tags = [tag for tag in tags if tag.strip() != ""]
    block_type = BlockType(block_type)
    return block_type, tags

class ParserNode:
    line_data: tuple[int, str]
    """
    line_number, line_text
    """
    children: list["ParserNode"]
    """
    List of child ParserNodes
    """
    def __init__(self, line_data: tuple[int, str], children: list["ParserNode"], depth: int, parent: Optional["ParserNode"] = None):
        self.line_data = line_data
        self.children = children
        self.parent = parent
        self.depth = depth
        assert all([child.depth == depth-1 for child in children]), "All children must have 1 less depth"

def parse_block_to_nodes(block: list[tuple[int, int, str]]) -> ParserNode:
    """
    Block is a list of tuples in the form of (line_number, num_tabs, line)

    Returns a tree of ParserNodes
    """
    block_type, tags = parse_block_header(block[0])
    root = ParserNode((block[0][0], block[0][2]), [], block[0][1])
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
        current_node.children.append(ParserNode((line_number, line_text), [], num_tabs, parent=current_node))
        current_depth = num_tabs



def parse_node(block: list[tuple[int, int, str]]):
    """
    Block is a list of tuples in the form of (line_number, num_tabs, line)
    """
    header = block[0]
    block_type, tags = parse_block_header(header)

    parser_map: dict[BlockType, Callable[[list[tuple[int, int, str]], list[str], int], None]] = {
        BlockType.MISSION: parse_mission
    }
    if block_type in parser_map:
        parser_map[block_type](block[1:], tags, header[0])
    else:
        pass
        # raise ParseError(f"Parser not implemented for block type: {block_type}")

def parse_mission(block_contents: list[tuple[int, int, str]], tags: list[str], start_line: int):
    assert len(tags) == 1, f"Invalid number of tags for mission: {tags} on line {start_line}"
    pass


if __name__ == "__main__":
    parse("../data/human/kestrel.txt")
