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

number_of_agents_slider = \
    mesa.visualization.Slider('Number of Agents', 1, 1, 500, 10)
infection_zone_slider = \
    mesa.visualization.Slider('Size of Infectious Zone', 0, 0, 5, 1)
recovery_zone_slider = \
    mesa.visualization.Slider('Size of Recovery Zone', 0, 0, 5, 1)
chance_of_infection_slider = \
    mesa.visualization.Slider('Chance of Infection', 0, 0, 10, 1)


grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)
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
    MoneyModel,
    [grid, chart, chart2, combined_chart],
    "epicurves.io",
    {'N': number_of_agents_slider, 'recovery_size': recovery_zone_slider,
     'infectious_size': infection_zone_slider,
     'chance_of_infection': chance_of_infection_slider,
     'width': 10, 'height': 10}
)

server.port = 8599
server.launch()
