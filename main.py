import solara
from MoneyModel import MoneyModel
from mesa.visualization import SolaraViz, SpaceRenderer, Slider, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle


def agent_portrayal(agent):
    if agent.wealth > 0:
        return AgentPortrayalStyle(color="red", size=50)
    if agent.recovered:
        return AgentPortrayalStyle(color="green", size=30)
    return AgentPortrayalStyle(color="grey", size=30)


@solara.component
def Legend(model):
    solara.Markdown(
        "**Legend:** 🔴 Infected &nbsp;&nbsp; "
        "🟢 Recovered &nbsp;&nbsp; "
        "⚪ Susceptible"
    )


@solara.component
def SimulationStatus(model):
    if not model.running:
        solara.Markdown("**Simulation finished** — all agents have recovered.")


model_params = {
    "N": Slider("Number of Agents", 250, 10, 1000, 1),
    "age_risk": Slider("At-Risk due to Age (0 < x < 100)", 30, 0, 100, 1),
    "genetic_risk": Slider("At-Risk due to Genetics (0 < x < 100)", 30, 0, 100, 1),
    "lifestyle_risk": Slider("At-Risk due to Lifestyle (0 < x < 100)", 30, 0, 100, 1),
    "death_risk": Slider("Risk of Death (0 < x < 100)", 10, 0, 100, 1),
    "steps_to_death": Slider("Minimum Steps before Death", 30, 1, 100, 1),
    "infectious_size": Slider("Size of Infectious Zone", 3, 0, 5, 1),
    "recovery_size": Slider("Size of Recovery Zone", 3, 0, 5, 1),
    "chance_of_infection": Slider(
        "Implicit Chance of Infection (0 < x < 100)", 30, 0, 100, 1
    ),
    "width": 10,
    "height": 10,
}

model = MoneyModel(
    N=250,
    recovery_size=3,
    infectious_size=3,
    chance_of_infection=30,
    width=10,
    height=10,
    age_risk=30,
    genetic_risk=30,
    lifestyle_risk=30,
    death_risk=10,
    steps_to_death=30,
)

renderer = SpaceRenderer(model, backend="matplotlib")
renderer.setup_structure()
renderer.setup_agents(agent_portrayal)
renderer.render()

page = SolaraViz(
    model,
    renderer=renderer,
    components=[
        Legend,
        SimulationStatus,
        make_plot_component({"Prevalence": "black"}),
        make_plot_component({"Incidence": "blue"}),
        make_plot_component(
            {"Susceptible": "black", "Infected": "blue", "Recovered": "red"}
        ),
        make_plot_component({"Deaths": "green"}),
    ],
    model_params=model_params,
    name="epidemics.io - Traditional Simulation",
)
