from parse import Mission, Payment, Event
from io import TextIOWrapper

def event_fmt(event: Event) -> str:
    print(f'Event: {event.id}')
    double_quote = '"'
    single_quote = "'"
    return f'"{event.id.replace(double_quote, single_quote)}"'

def mission_fmt(mission: Mission) -> str:
    return f'"{mission.id}"'

def payment_fmt(payment: Payment) -> str:
    return f'"payment:{payment.amount}"'

def draw_event(event: Event, file: TextIOWrapper):
    file.write(f'{event_fmt(event)} [shape=ellipse,fillcolor=lightblue,style=filled]\n')

def draw_mission_node(mission: Mission, file: TextIOWrapper):
    file.write(f'{mission_fmt(mission)} [shape=box,fillcolor=lightgreen,style=filled]\n')

def draw_payment(payment: Payment, file: TextIOWrapper):
    file.write(f'{payment_fmt(payment)} [shape=oval,fillcolor=lightpink,style=filled]\n')

def visualize_missions(missions: list[Mission], output_path: str):
    events: set[Event] = set()
    payments: set[Payment] = set()
    with open(output_path, "w") as f:
        for mission in missions:
            if mission.to_offer.has:
                events.add(mission.to_offer.has.event)
            if mission.on_complete and mission.on_complete.payment:
                payments.add(mission.on_complete.payment)
                for event in mission.on_complete.events:
                    events.add(event)
        f.write("digraph G {\n")
        for event in events:
            draw_event(event, f)
        for mission in missions:
            draw_mission_node(mission, f)
        for payment in payments:
            draw_payment(payment, f)
        for mission in missions:
            if mission.to_offer.has:
                f.write(f'{event_fmt(mission.to_offer.has.event)} -> {mission_fmt(mission)}\n')
            if mission.on_complete:
                if mission.on_complete.payment:
                    f.write(f'{mission_fmt(mission)} -> {payment_fmt(mission.on_complete.payment)}\n')
                for event in mission.on_complete.events:
                    f.write(f'{mission_fmt(mission)} -> {event_fmt(event)}\n')
        f.write("}\n")
