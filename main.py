from MoneyModel import MoneyModel
import mesa.visualization

def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.3
    return portrayal

number_of_agents_slider = mesa.visualization.NumberInput('Number of Agents', 250, description="Number of agents in zone")

age_risk = mesa.visualization.NumberInput('At-Risk due to Age (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their age.")
genetic_risk = mesa.visualization.NumberInput('At-Risk due to Genetics (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their genetics.")
lifestyle_risk = mesa.visualization.NumberInput('At-Risk due to Lifestyle (0 < x < 100)', 30,description="Proportion of population that is at-risk due to their lifestyle.")
death_risk = mesa.visualization.NumberInput('Risk of Death (0 < x < 100)', 10, description="Risk of death after minimum amount of steps taken.")
steps_to_death = mesa.visualization.NumberInput('Minimum Steps before Death', 30, description="Minimum number of steps taken before agent is able to die.")

infection_zone_slider = mesa.visualization.Slider('Size of Infectious Zone', 3, 0, 5, 1)
recovery_zone_slider = mesa.visualization.Slider('Size of Recovery Zone', 3, 0, 5, 1)
chance_of_infection_slider = mesa.visualization.NumberInput('Implicit Chance of Infection (0 < x < 100)', 30, description="Chance of getting infected per interaction for an agent that does not have any factors that increase their chance of infection.")

grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 864, 864)
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
chart3 = mesa.visualization.ChartModule([{'Label': 'Deaths', 'Color': 'Green'}])

server = mesa.visualization.ModularServer(
    MoneyModel,
    [grid, chart, chart2, combined_chart, chart3],
    "epicurves.io - Traditional Simulation",
    {'N': number_of_agents_slider, 
     'chance_of_infection': chance_of_infection_slider,
     'death_risk': death_risk,
     'steps_to_death': steps_to_death,
     'age_risk': age_risk,
     'genetic_risk': genetic_risk,
     'lifestyle_risk': lifestyle_risk,
     'recovery_size': recovery_zone_slider,
     'infectious_size': infection_zone_slider,
     'width': 10, 'height': 10}
)

server.port = 8599
server.launch()
