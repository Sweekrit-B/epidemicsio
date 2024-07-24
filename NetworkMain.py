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
            '''else:
                color = 'grey'  # Add debugging here to print unexpected conditions
                print(f"Agent {agent.unique_id} has unexpected wealth={agent.wealth} and recovered={agent.recovered}")
            '''
            portrayal['nodes'].append({
                'id': node_id,
                'size': 6,
                'color': color,
                'label': str(agent.unique_id),
            })

    portrayal['edges'] = [
        {'source': source, 'target': target, 'color': 'black'} for source, target in G.edges
    ]

    return portrayal

number_of_agents_slider = mesa.visualization.NumberInput('Number of Agents', 40, description = "Number of agents in the simulation.")
chance_of_infection_slider = mesa.visualization.NumberInput('Implicit Chance of Infection (0 < x < 100)', 30, description="Chance of getting infected per interaction for an agent that does not have any factors that increase their chance of infection.")

age_risk = mesa.visualization.NumberInput('At-Risk due to Age (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their age.")
genetic_risk = mesa.visualization.NumberInput('At-Risk due to Genetics (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their genetics.")
lifestyle_risk = mesa.visualization.NumberInput('At-Risk due to Lifestyle (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their lifestyle.")


graph_type_choice = mesa.visualization.Choice('Graph Type', value='Barabasi Albert', choices=['Barabasi Albert', 'Watts Strogatz', 'Erdos Renyi', 'Power Law Cluster'], description="Barabási-Albert for scale-free networks (power law degree distribution) with hubs. \nWatts-Strogatz for small-world networks with short paths and high clustering. \nErdős-Rényi for random graphs with uniform connectivity. \nPower Law Cluster for networks with both high clustering using triangles and a power-law degree distribution.")

p_value_slider = mesa.visualization.NumberInput('P Value (0 < x < 10)', 4, description="Probability of rewiring each edge (Watts Strogatz). \nProbability of an edge existing between a pair of nodes (Erdos Renyi). \nProbability of a triangle being created (Power Law Cluster).")
m_value_slider = mesa.visualization.NumberInput('M Value (0 < x < number of nodes)', 3, description="Number of new edges per node, selected preferentially (Barabasi Albert and Power Law Cluster")
num_recoveries_slider = mesa.visualization.NumberInput('Number of Recoveries', 3, description="Number of recoveries an agent has before they are immune.")
num_steps_to_recovery_slider = mesa.visualization.NumberInput('Number of Steps till Recovery', 10, description="Number of steps an agent has to take before they automatically recover")

grid = mesa.visualization.NetworkModule(network_portrayal, canvas_height=1000, canvas_width=864)
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
     'chance_of_infection': chance_of_infection_slider, 'age_risk_proportion': age_risk,
     'genetic_risk_proportion': genetic_risk,
     'lifestyle_risk_proportion': lifestyle_risk,
     'graph_type': graph_type_choice,
     'p_value': p_value_slider,
     'm_value': m_value_slider,
     'num_recoveries_for_immune': num_recoveries_slider,
     'num_steps': num_steps_to_recovery_slider}
)

server.port = 8660
server.launch()
