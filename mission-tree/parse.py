from enum import Enum


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
    blocks = [parse_block(block) for block in block_data]
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
        num_tabs = line.count("\t")
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


def parse_block(block: list[tuple[int, int, str]]):
    """
    Block is a list of tuples in the form of (line_number, num_tabs, line)
    """
    header = block[0]
    block_type, tags = parse_block_header(header)

    parser_map = {
        BlockType.MISSION: lambda x: None,
    }
    if block_type in parser_map:
        parser_map[block_type](block)
    else:
        raise ParseError(f"Parser not implemented for block type: {block_type}")
    print(block_type, tags)


if __name__ == "__main__":
    parse("../data/human/kestrel.txt")
