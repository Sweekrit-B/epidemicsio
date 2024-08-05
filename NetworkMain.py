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

interest_form = mesa.visualization.StaticText('<h4><a href = "https://tinyurl.com/epiointerest" target = "_blank"> tinyurl.com/epiointerest </a></h4>')
base_factors_header = mesa.visualization.StaticText('<div style="width: 400px;"><h2><b>Base Factors</b></h2></div>')
risk_factors_header = mesa.visualization.StaticText('<h2><b>Risk Factors</b></h2>')
lifestyle_factors_header = mesa.visualization.StaticText('<h4><b>Lifestyle Risk Factors</b></h4>')
graph_factors_header = mesa.visualization.StaticText('<h2><b>Graph Customization</h2></b>')
recovery_factors_header = mesa.visualization.StaticText('<h2><b>Recovery Factors</h2></b>')
citation_title = mesa.visualization.StaticText('<h2><b>Citations</h2></b>')

num_agents_descriptor = mesa.visualization.StaticText('<div style="width: 400px;"><p>Determines the number of nodes that are present in the graph. Represents a city or a location, connected with edges (transportation networks).</p><p>Note that agents can only spread disease to other agents <b>directly connected</b> to it.</p></div>')
number_of_agents_slider = mesa.visualization.NumberInput('Number of Agents', 200, description = "Number of agents in the simulation.")

chance_of_infection_descriptor = mesa.visualization.StaticText('<div style="width: 400px;"><p>Determines the chance that an agent gets infected when interacting with a diseased agent. This is a number out of 100 (percentage).</p></div>')
chance_of_infection_slider = mesa.visualization.NumberInput('Implicit Chance of Infection (0 < x < 100)', 30, description="Chance of getting infected per interaction for an agent that does not have any factors that increase their chance of infection.")

age_descriptor = mesa.visualization.StaticText('<div style="width: 400px;"><p>Those ages 65+ have increased risk of disease. This is due to age-related immunity changes. </p> <p> 1. Aging decreases the efficacy of vaccines. Prevention is 70-90 percent normally, while in ages 65+ is anywhere from 30-40 percent.</p> <p>2. Adaptive immunity decreases with aging. Humoral immunity (with somatic hypermutation) decreases with age. Furthermore, E47 (which regulates B-cell function), decreases with age.</p> <p>3. Aging decreases T-cell functions which have a reduced ability to form functional immunological synapses with younger T-cells. </p> <p>4. For innate immunity, aging impairs plasmacytoid dendritic cells (pDCs) ability to produce Type I interferons, which initiates host response.</p></div>')
age_risk = mesa.visualization.NumberInput('At-Risk due to Age (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their age.")

genetic_descriptor = mesa.visualization.StaticText('<div style="width: 400px;"><p>There are genetic factors that increase the probability of obtaining a disease. This is a catch-all factor that ensures this is accounted for. However, note that it is impossible to factor in all possible genetic factors (as they are unique per person).</p></div>')
genetic_risk = mesa.visualization.NumberInput('At-Risk due to Genetics (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their genetics.")

lifestyle_descriptor = mesa.visualization.StaticText('<div style="width: 400px;"><p>Lifestyle choices effect the chance of infection of disease and mortality. We look to four lifestyle factors, which specifically incease the chance of NCDs (non-communicable diseases), which in turn increase the risk of infection disease:</p> <p>Tobacco use, an unhealthy diet, insufficient physical activity, and harmful alcohol use.</p> <p> We are also including an income multiplier, for an increased lifestyle risk. This is because those in low or middle-income communities are more likely to be at risk for these lifestyle factors and hence infectious disease</p></div>')
tobacco_use = mesa.visualization.NumberInput('At-Risk due to Smoking (0 < x < 100)', 30, description="Proportion of population that is at-risk due to smoking.")
unhealthy_diet = mesa.visualization.NumberInput('At-Risk due to Unhealthy Diet (0 < x < 100)', 30, description="Proportion of population that is at-risk due to an unhealthy diet.")
insufficient_physical_activity = mesa.visualization.NumberInput('At-Risk due to Insufficient Physical Activity (0 < x < 100)', 30, description="Proportion of population that is at-risk due to insufficient physical activity.")
harmful_alcohol_use = mesa.visualization.NumberInput('At-Risk due to Harmful Alcohol Use (0 < x < 100)', 30, description="Proportion of population that is at-risk due to harmful alcohol use.")
income_multiplier = mesa.visualization.NumberInput('Income-based multiplier for increased lifestyle risk', 1.2,description="Proportion of population that is at-risk due to their income.")


graph_type_choice = mesa.visualization.Choice('Graph Type', value='Barabasi Albert', choices=['Barabasi Albert', 'Watts Strogatz', 'Erdos Renyi', 'Power Law Cluster'], description="Type of graph, defining structure.")
graph_type_description = mesa.visualization.StaticText('<div style="width: 400px;"><br><p>Barabási-Albert for scale-free networks (power law degree distribution) with hubs </p> <p>Watts-Strogatz for small-world networks with short paths and high clustering </p> <p>Erdős-Rényi for random graphs with uniform connectivity. </p> <p>Power Law Cluster for networks with both high clustering using triangles and a power-law degree distribution. <p> Graph types define <b> the structure </b> of your network.</p></div>')

p_value_slider = mesa.visualization.NumberInput('P Value (0 < x < 10)', 4)
p_value_description = mesa.visualization.StaticText('<div style="width: 400px;"><p>1. Watts Strogatz - Probability of rewiring each edge to another, separate, node.</p> <p>2. Erdos Renyi - probability of an edge existing between a pair of nodes to connect them together. </p> <p>3. Power Law Cluster - probability of a triangle being created between a node and its two closest members </p> </div>')

m_value_slider = mesa.visualization.NumberInput('M Value (0 < x < number of nodes)', 3, description="Number of new edges per node, selected preferentially (Barabasi Albert and Power Law Cluster")
m_value_description = mesa.visualization.StaticText('<div style = "width: 400px;"><p> Number of new edges per node that is created, selected preferentially (some nodes have a gerater chance of being selected). </p><p>Please note that the m-variable is the same for both Power Law cluster and Barabasi Albert. However, it is inconsequential to the other two graph types </p> </div>')

num_recoveries_slider = mesa.visualization.NumberInput('Number of Recoveries', 3, description="Number of recoveries an agent has before they are immune.")
num_recoveries_description = mesa.visualization.StaticText('<div style = "width: 400 px;" <p> Indicates the number of recoveries that an agent must go through before they are able to recover. A representation of the number of strains that the virus goes through before pure immunity. </p>')

num_steps_to_recovery_slider = mesa.visualization.NumberInput('Number of Steps till Recovery', 10, description="Number of steps an agent has to take before they automatically recover")
num_steps_to_recovery_description = mesa.visualization.StaticText('<div style = "width: 400 px;" <p> The number of steps that an agent must take before having to recover. After these steps, there is a chance that the agent gets vaccinated as well. </p>')

vaccination_rate = mesa.visualization.NumberInput("Vaccination Rate (0 < x < 100)", 30)
vaccination_rate_description = mesa.visualization.StaticText('<div style = "width: 400 px;" <p> The probability of an agent already being vaccinated or getting vaccinated after recovering from disease. </p>')

vaccination_efficacy = mesa.visualization.NumberInput("Vaccination Efficacy (0 < x < 100)", 75)
vaccination_efficacy_description = mesa.visualization.StaticText('<div style = "width: 400 px;" <p> The efficacy of a vaccination. Efficacy describes how good the vaccine is at preventing disease under IDEAL conditions. Note that factors like age play an impact in the <b>effectiveness</b> (unideal situations) of disease. </p>')

citation_text = mesa.visualization.StaticText('<div style = "width: 1000 px;" <p><a href = "https://pubmed.ncbi.nlm.nih.gov/11130187/">1. Impact of age-related immune dysfunction on risk of infections </a></p> <p><a href = "https://www.sciencedirect.com/science/article/pii/S128645791000211X?via%3Dihub">2. Impact of aging on viral infections </a></p> <p><a href = "https://www.cdc.gov/globalhealth/healthprotection/fieldupdates/winter-2017/ncds-impact-ghs.html">3. Three Ways NCDs Impact Global Health Security </a></p> <p><a href = "https://medcraveonline.com/JCCR/lifestyle-diseases-consequences-characteristics-causes-and-control.html"> 4. Lifestyle Disease Consequences: Causes and Characteristics</a></p>')

grid = mesa.visualization.NetworkModule(network_portrayal, canvas_height=1000, canvas_width=864)
chart4 = mesa.visualization.ChartModule([{'Label': 'Total Infections', 'Color': 'Red'}], data_collector_name="datacollector")
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
chart3 = mesa.visualization.ChartModule([{'Label': 'Vaccinations', 'Color': 'Green'}])
combined_chart2 = mesa.visualization.ChartModule(
    [
        {'Label': 'Prevalence - Tobacco', 'Color': 'Aqua'},
        {'Label': 'Prevalence - Diet', 'Color': 'Red'},
        {'Label': 'Prevalence - Physical Activity', 'Color': 'Blue'},
        {'Label': 'Prevalence - Alcohol Use', 'Color': 'Black'}
    ],
    data_collector_name="datacollector"
)
combined_chart3 = mesa.visualization.ChartModule(
    [
        {'Label': 'Prevalence - Age Risk', 'Color': 'Orange'},
        {'Label': 'Prevalence - Genetic Risk', 'Color': 'Purple'},
        {'Label': 'Prevalence - Lifestyle Risk', 'Color': 'Green'}
    ]
)


server = mesa.visualization.ModularServer(
    NetworkModel,
    [grid, chart4, chart, chart2, combined_chart, chart3, combined_chart2, combined_chart3],
    "epidemics.io - Network Simulation",
    {'interest_form': interest_form,
     'base_factors_header': base_factors_header,
     'N': number_of_agents_slider,
     'num_agents_descriptor': num_agents_descriptor,
     'chance_of_infection': chance_of_infection_slider, 
     'chance_of_infection_descriptor': chance_of_infection_descriptor,
     
     'risk_factors_header': risk_factors_header,
     'age_risk_proportion': age_risk,
     'age_descriptor': age_descriptor,
     'genetic_risk_proportion': genetic_risk,
     'genetic_descriptor': genetic_descriptor,
     
     'lifestyle_factors_header': lifestyle_factors_header,
     'lifestyle_descriptor': lifestyle_descriptor,
     'tobacco_risk_proportion': tobacco_use, 
     'unhealthy_diet_proportion': unhealthy_diet, 'physical_activity_proportion': insufficient_physical_activity, 'alcohol_use_proportion': harmful_alcohol_use,
     'income_multiplier': income_multiplier,

     'graph_factors_header': graph_factors_header,
     'graph_type': graph_type_choice,
     'graph_type_descriptor': graph_type_description,
     'p_value': p_value_slider,
     'p_value_descriptor': p_value_description,
     'm_value': m_value_slider,
     'm_value_descriptor': m_value_description,

     'recovery_factors_header': recovery_factors_header,
     'num_recoveries_for_immune': num_recoveries_slider,
     'num_recoveries_descriptor': num_recoveries_description,
     'num_steps': num_steps_to_recovery_slider,
     'num_steps_descriptor': num_steps_to_recovery_description,
     'vaccination_rate': vaccination_rate,
     'vaccination_rate_description': vaccination_rate_description,
     'vaccination_efficacy': vaccination_efficacy,
     'vaccination_rate_efficacy': vaccination_efficacy_description,
     
     'citation_title': citation_title,
     'citation_text': citation_text
     }
)

server.port = 8660
server.launch()
