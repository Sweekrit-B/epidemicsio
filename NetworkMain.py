from NetworkModel import NetworkModel
import mesa.visualization

def network_portrayal(G):
    portrayal = dict()
    portrayal['nodes'] = []

    for node_id, agents in G.nodes.data('agent'):
        for agent in agents:
            if agent.wealth == 1 and agent.recovered == 0:
                color = 'red'
            elif agent.wealth == 0 and agent.recovered == 1:
                color = 'green'
            elif agent.wealth == 0 and agent.recovered == 0:
                color = 'blue'
            else:
                color = 'grey'  # Add debugging here to print unexpected conditions
                print(f"Agent {agent.unique_id} has unexpected wealth={agent.wealth} and recovered={agent.recovered}")

            portrayal['nodes'].append({
                'id': node_id,
                'size': 6,
                'color': color,
                'label': str(agent.unique_id),
            })

    portrayal['edges'] = [
        {'source': source, 'target': target, 'color': 'grey'} for source, target in G.edges
    ]

    return portrayal

number_of_agents_slider = \
    mesa.visualization.Slider('Number of Agents', 1, 1, 500, 10)
chance_of_infection_slider = \
    mesa.visualization.Slider('Chance of Infection', 0, 0, 10, 1)


grid = mesa.visualization.NetworkModule(network_portrayal, 500, 500)
chart = mesa.visualization.ChartModule([{'Label': 'Prevalence', 'Color': 'Black'}], data_collector_name="datacollector")
chart2 = mesa.visualization.ChartModule([{'Label': 'Incidence', 'Color': 'Blue'}], data_collector_name="datacollector")
combined_chart = mesa.visualization.ChartModule(
    [
        {'Label': 'Susceptible', 'Color': 'Black'},
        {'Label': 'Infected', 'Color': 'Blue'},
        {'Label': 'Recovered', 'Color': 'Red'}
    ],
    data_collector_name="datacollector"
)

server = mesa.visualization.ModularServer(
    NetworkModel,
    [grid, chart, chart2, combined_chart],
    "epicurves.io - Network Simulation",
    {'N': number_of_agents_slider,
     'chance_of_infection': chance_of_infection_slider,
     'avg_node_degree': 3}
)

server.port = 8659
server.launch()
