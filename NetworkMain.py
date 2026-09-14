from NetworkModel import NetworkModel
from mesa.visualization import SolaraViz, SpaceRenderer, Slider, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle


def agent_portrayal(agent):
    if agent.wealth == 1 and agent.recovered == 0:
        color = "red"
    elif agent.wealth == 0 and agent.recovered == 1:
        color = "green"
    else:
        color = "blue"
    return AgentPortrayalStyle(color=color, size=30)


model_params = {
    "N": Slider("Number of Agents", 200, 10, 1000, 1),
    "chance_of_infection": Slider(
        "Implicit Chance of Infection (0 < x < 100)", 30, 0, 100, 1
    ),
    "graph_type": {
        "type": "Select",
        "label": "Graph Type",
        "value": "Barabasi Albert",
        "values": [
            "Barabasi Albert",
            "Watts Strogatz",
            "Erdos Renyi",
            "Power Law Cluster",
        ],
    },
    "p_value": Slider("P Value (0 < x < 10)", 4, 0, 10, 1),
    "m_value": Slider("M Value (0 < x < number of nodes)", 3, 0, 10, 1),
    "num_recoveries_for_immune": Slider("Number of Recoveries", 3, 0, 10, 1),
    "num_steps": Slider("Number of Steps till Recovery", 10, 0, 10, 1),
    "age_risk_proportion": Slider("At-Risk due to Age (0 < x < 100)", 30, 0, 100, 1),
    "genetic_risk_proportion": Slider(
        "At-Risk due to Genetics (0 < x < 100)", 30, 0, 100, 1
    ),
    "tobacco_risk_proportion": Slider(
        "At-Risk due to Smoking (0 < x < 100)", 30, 0, 100, 1
    ),
    "unhealthy_diet_proportion": Slider(
        "At-Risk due to Unhealthy Diet (0 < x < 100)", 30, 0, 100, 1
    ),
    "physical_activity_proportion": Slider(
        "At-Risk due to Insufficient Physical Activity (0 < x < 100)", 30, 0, 100, 1
    ),
    "alcohol_use_proportion": Slider(
        "At-Risk due to Harmful Alcohol Use (0 < x < 100)", 30, 0, 100, 1
    ),
    "income_multiplier": Slider(
        "Income-based multiplier for increased lifestyle risk", 1.2, 1.0, 3.0, 0.1
    ),
    "vaccination_rate": Slider("Vaccination Rate (0 < x < 100)", 30, 0, 100, 1),
    "vaccination_efficacy": Slider("Vaccination Efficacy (0 < x < 100)", 75, 0, 100, 1),
}

model = NetworkModel(
    N=200,
    chance_of_infection=30,
    graph_type="Barabasi Albert",
    m_value=3,
    p_value=4,
    num_recoveries_for_immune=3,
    num_steps=10,
    age_risk_proportion=30,
    genetic_risk_proportion=30,
    tobacco_risk_proportion=30,
    unhealthy_diet_proportion=30,
    physical_activity_proportion=30,
    alcohol_use_proportion=30,
    income_multiplier=1.2,
    vaccination_rate=30,
    vaccination_efficacy=75,
)
model.create_agents()

renderer = SpaceRenderer(model, backend="matplotlib")
renderer.setup_structure()
renderer.setup_agents(agent_portrayal)
renderer.render()

page = SolaraViz(
    model,
    renderer=renderer,
    components=[
        make_plot_component({"Total Infections": "red"}),
        make_plot_component({"Prevalence": "black"}),
        make_plot_component({"Incidence": "blue"}),
        make_plot_component(
            {"Susceptible": "black", "Infected": "blue", "Recovered": "red"}
        ),
        make_plot_component({"Vaccinations": "green"}),
        make_plot_component(
            {
                "Prevalence - Tobacco": "aqua",
                "Prevalence - Diet": "red",
                "Prevalence - Physical Activity": "blue",
                "Prevalence - Alcohol Use": "black",
            }
        ),
        make_plot_component(
            {
                "Prevalence - Age Risk": "orange",
                "Prevalence - Genetic Risk": "purple",
                "Prevalence - Lifestyle Risk": "green",
            }
        ),
    ],
    model_params=model_params,
    name="epidemics.io - Network Simulation",
)
