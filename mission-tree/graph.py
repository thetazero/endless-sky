from parse import Mission
from io import TextIOWrapper

def event_fmt(event: str) -> str:
    return f'"{event}"'

def mission_fmt(mission: str) -> str:
    return f'"{mission}"'

def draw_event(condition: str, file: TextIOWrapper):
    file.write(f'{event_fmt(condition)} [shape=box,fillcolor=lightblue,style=filled]\n')

def draw_mission_node(mission: Mission, file: TextIOWrapper):
    file.write(f'{mission_fmt(mission.id)} [shape=box,fillcolor=lightgreen,style=filled]\n')

def visualize_missions(missions: list[Mission], output_path: str):
    conditions = set()
    for mission in missions:
        if mission.to_offer.has:
            conditions.add(mission.to_offer.has.condition)
    with open(output_path, "w") as f:
        f.write("digraph G {\n")
        for condition in conditions:
            draw_event(condition, f)
        for mission in missions:
            draw_mission_node(mission, f)
        for mission in missions:
            if mission.to_offer.has:
                f.write(f'{event_fmt(mission.to_offer.has.condition)} -> {mission_fmt(mission.id)}\n')
        f.write("}\n")
