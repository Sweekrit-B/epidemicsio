import time

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from MoneyModel import MoneyModel
from MoneyModel import compute_deaths as money_deaths
from MoneyModel import compute_incidence as money_incidence
from MoneyModel import compute_infected as money_infected
from MoneyModel import compute_prevalence as money_prevalence
from MoneyModel import compute_recovered as money_recovered
from MoneyModel import compute_susceptible as money_susceptible
from NetworkModel import NetworkModel

matplotlib.use('WebAgg')

st.title("Epidemics.io")

model_choice = st.sidebar.radio(
    "Simulation Type", ["Traditional (Grid)", "Network"], key="model_choice"
)

GRID_PRESETS = {
    "Flu-like": dict(
        infection_chance=40, death_risk=2, steps_to_death=10,
        age_risk=20, genetic_risk=15, lifestyle_risk=15,
    ),
    "COVID-like": dict(
        infection_chance=30, death_risk=10, steps_to_death=20,
        age_risk=40, genetic_risk=25, lifestyle_risk=25,
    ),
    "High Mortality": dict(
        infection_chance=25, death_risk=40, steps_to_death=8,
        age_risk=50, genetic_risk=40, lifestyle_risk=35,
    ),
}

NETWORK_PRESETS = {
    "Flu-like": dict(
        infection_chance=40, age_risk=20, genetic_risk=15,
        vaccination_rate=20, vaccination_efficacy=60,
    ),
    "COVID-like": dict(
        infection_chance=30, age_risk=40, genetic_risk=25,
        vaccination_rate=40, vaccination_efficacy=75,
    ),
    "High Mortality": dict(
        infection_chance=25, age_risk=50, genetic_risk=40,
        vaccination_rate=10, vaccination_efficacy=50,
    ),
}


def apply_preset():
    preset_name = st.session_state["disease_preset"]
    if preset_name == "Custom":
        return
    presets = (
        GRID_PRESETS if st.session_state["model_choice"] == "Traditional (Grid)" else NETWORK_PRESETS
    )
    for key, value in presets[preset_name].items():
        st.session_state[key] = value


def preset_slider(label, min_value, max_value, key, default, **kwargs):
    # Seed session_state right before this widget's own first mount (not in some
    # earlier, unrelated run) — seeding it earlier desyncs the slider's visual
    # thumb position from its value on widgets that only mount in one branch
    # (e.g. Network-only sliders, when Grid is the default landing mode).
    st.session_state.setdefault(key, default)
    return st.slider(label, min_value, max_value, key=key, **kwargs)


with st.sidebar:
    st.selectbox(
        "Disease Preset",
        ["Custom", "Flu-like", "COVID-like", "High Mortality"],
        key="disease_preset",
        on_change=apply_preset,
        help="Sets a starting point for the risk/infection sliders below — tweak them afterward as you like.",
    )

    st.title("Simulation Parameters")
    # Grid deaths only start after `steps_to_death` (default 30) consecutive infected
    # steps, so the default run length needs enough headroom to actually show one.
    default_ticks = 50 if model_choice == "Traditional (Grid)" else 15
    num_ticks = st.slider("Select number of steps for simulation", 0, 1000, default_ticks)

    if model_choice == "Traditional (Grid)":
        num_agents = st.slider("Number of Agents", 10, 1000, 250)
        infection_chance = preset_slider("Implicit Chance of Infection", 0, 100, "infection_chance", 30)
        grid_width = st.slider("Grid Width", 5, 50, 10)
        grid_height = st.slider("Grid Height", 5, 50, 10)
    else:
        num_agents = st.slider("Number of Agents", 50, 500, 200)
        infection_chance = preset_slider("Chance of Infection", 0, 100, "infection_chance", 30)

    st.title("Risk Factors")
    age_risk = preset_slider("Percent at-risk due to Age", 0, 100, "age_risk", 30)
    genetic_risk = preset_slider("Percent at-risk due to Genetics", 0, 100, "genetic_risk", 30)

    if model_choice == "Traditional (Grid)":
        lifestyle_risk = preset_slider("Percent at-risk due to Lifestyle", 0, 100, "lifestyle_risk", 30)

        st.title("Death & Recovery Parameters")
        death_risk = preset_slider("Risk of Death", 0, 100, "death_risk", 10)
        steps_to_death = preset_slider("Minimum steps before death risk applies", 1, 100, "steps_to_death", 30)
        infectious_size = st.slider("Size of Infectious Zone", 0, 5, 3)
        recovery_size = st.slider("Size of Recovery Zone", 0, 5, 3)
    else:
        tobacco_use = st.slider("Percent at-risk due to Smoking", 0, 100, 30)
        unhealthy_diet = st.slider("Percent at-risk due to Unhealthy Diet", 0, 100, 30)
        insufficient_physical_activity = st.slider("Percent at-risk due to Insufficient Physical Activity", 0, 100, 30)
        harmful_alcohol_use = st.slider("Percent at-risk due too Alcohol Use", 0, 100, 30)
        income_multiplier = st.slider("Income-based multiplier for increased lifestyle risk", value=1.2)

        st.title("Recovery Parameters")
        num_recoveries_slider = st.slider('Number of recoveries till immunity', 0, 10, 3)
        num_steps_recoveries_slider = st.slider("Number of steps till recovery", 0, 10, 3)
        vaccination_rate = preset_slider("Vaccination rate", 0, 100, "vaccination_rate", 30)
        vaccination_efficacy = preset_slider("Vaccination efficacy", 0, 100, "vaccination_efficacy", 75)

        st.title("Network Graph Parameters")
        graph_type_choice = st.selectbox(
            "Graph type",
            options=['Barabasi Albert', 'Watts Strogatz', 'Erdos Renyi', 'Power Law Cluster'],
        )
        p_value_slider = st.slider("P value", 0, 10, 4)
        m_value_slider = st.slider("M value", 0, 10, 3)

with st.expander("Citations"):
    url1 = "https://pubmed.ncbi.nlm.nih.gov/11130187/"
    st.write("[Impact of age-related immune dysfunction on risk of infections](%s)" % url1)
    url2 = "https://www.sciencedirect.com/science/article/pii/S128645791000211X?via%3Dihub"
    st.write("[Impact of aging on viral infections](%s)" % url2)
    if model_choice == "Network":
        url3 = "https://www.cdc.gov/globalhealth/healthprotection/fieldupdates/winter-2017/ncds-impact-ghs.html"
        st.write("[Three Ways NCDs Impact Global Health Security](%s)" % url3)
        url4 = "https://medcraveonline.com/JCCR/lifestyle-diseases-consequences-characteristics-causes-and-control.html"
        st.write("[Lifestyle Disease Consequences: Causes and Characteristics](%s)" % url4)

run = st.button("Run Simulation")


def run_grid_simulation():
    st.caption(
        "🔴 Infected &nbsp;&nbsp; 🟢 Recovered &nbsp;&nbsp; ⚪ Susceptible"
    )

    model = MoneyModel(
        N=num_agents,
        recovery_size=recovery_size,
        infectious_size=infectious_size,
        chance_of_infection=infection_chance,
        width=grid_width,
        height=grid_height,
        age_risk=age_risk,
        genetic_risk=genetic_risk,
        lifestyle_risk=lifestyle_risk,
        death_risk=death_risk,
        steps_to_death=steps_to_death,
    )

    def get_colors():
        xs, ys, colors = [], [], []
        for agent in model.agents:
            xs.append(agent.x)
            ys.append(agent.y)
            if agent.wealth > 0:
                colors.append('red')
            elif agent.recovered:
                colors.append('green')
            else:
                colors.append('grey')
        return xs, ys, colors

    def create_figure():
        xs, ys, colors = get_colors()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(xs, ys, c=colors, s=40, edgecolors='black', linewidths=0.5)
        ax.set_xlim(-0.5, model.grid.width - 0.5)
        ax.set_ylim(-0.5, model.grid.height - 0.5)
        ax.set_aspect('equal')
        ax.set_xticks(range(model.grid.width))
        ax.set_yticks(range(model.grid.height))
        ax.grid(True)
        return fig

    my_bar = st.progress(0, text="Simulation Progress")
    placeholder = st.empty()
    grid_container = st.empty()

    prevalence, incidence = [], []
    susceptible, infected, recovered, deaths = [], [], [], []

    line_plot_container1_title = st.empty()
    line_plot_container1 = st.empty()
    line_plot_container2_title = st.empty()
    line_plot_container2 = st.empty()
    line_plot_container3_title = st.empty()
    line_plot_container3 = st.empty()

    for i in range(num_ticks + 1):
        if not model.running:
            st.info("Simulation finished — all agents have recovered.")
            break

        model.step()
        my_bar.progress(i / max(num_ticks, 1), text="Simulation progress")
        placeholder.text(f"Step = {i}")

        fig = create_figure()
        grid_container.pyplot(fig)
        plt.close(fig)

        prevalence.append(money_prevalence(model))
        incidence.append(money_incidence(model))
        susceptible.append(money_susceptible(model))
        infected.append(money_infected(model))
        recovered.append(money_recovered(model))
        deaths.append(money_deaths(model))

        line_plot_container1_title.write("Prevalence and Incidence")
        line_plot_container1.line_chart({'Prevalence': prevalence, 'Incidence': incidence})
        line_plot_container2_title.write("SIR Graph")
        line_plot_container2.line_chart(
            {'Susceptible': susceptible, 'Infected': infected, 'Recovered': recovered}
        )
        line_plot_container3_title.write("Deaths")
        line_plot_container3.line_chart({'Deaths': deaths})

        time.sleep(0.1)

    ever_infected = sum(1 for a in model.agents if a.wealth > 0 or a.recovered == 1) + model.deaths
    peak_infected = max(infected) if infected else 0
    peak_day = infected.index(peak_infected) if infected else 0
    attack_rate = ever_infected / num_agents if num_agents else 0
    case_fatality_rate = model.deaths / ever_infected if ever_infected else 0

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peak Infected", peak_infected, help=f"Reached on step {peak_day}")
    col2.metric("Ever Infected", ever_infected, f"{attack_rate:.0%} attack rate", delta_color="off")
    col3.metric("Deaths", model.deaths, f"{case_fatality_rate:.0%} case fatality rate", delta_color="off")
    col4.metric("Final Recovered", recovered[-1] if recovered else 0)

    results_df = model.datacollector.get_model_vars_dataframe()
    with st.expander("Results dataframe"):
        st.dataframe(results_df)
    st.download_button(
        "Download results as CSV",
        results_df.to_csv().encode("utf-8"),
        file_name="grid_simulation_results.csv",
        mime="text/csv",
    )


def run_network_simulation():
    st.caption(
        "🔴 Infected &nbsp;&nbsp; 🟢 Recovered &nbsp;&nbsp; 🔵 Susceptible"
    )

    model = NetworkModel(
        num_agents,
        infection_chance,
        graph_type_choice,
        m_value_slider,
        p_value_slider,
        num_recoveries_slider,
        num_steps_recoveries_slider,
        age_risk,
        genetic_risk,
        tobacco_use,
        unhealthy_diet,
        insufficient_physical_activity,
        harmful_alcohol_use,
        income_multiplier,
        vaccination_rate,
        vaccination_efficacy,
    )
    model.create_agents()

    G = model.G
    pos = nx.spring_layout(G)

    def get_colors():
        node_colors = []
        edge_colors = ['black' for _ in G.edges]
        for node_id in G.nodes:
            for agent in model.grid.get_cell_list_contents([node_id]):
                if agent.wealth == 1 and agent.recovered == 0:
                    node_colors.append('red')
                elif agent.wealth == 0 and agent.recovered == 1:
                    node_colors.append('green')
                else:
                    node_colors.append('blue')
        return node_colors, edge_colors

    def create_figure():
        node_colors, edge_colors = get_colors()
        fig, ax = plt.subplots(figsize=(8, 8))
        nx.draw(G, pos, node_color=node_colors, edge_color=edge_colors, width=0.6, node_size=30)
        return fig

    my_bar = st.progress(0, text="Simulation Progress")
    placeholder = st.empty()
    graph_container = st.empty()

    total_infections, vaccinations = [], []
    prevalence, incidence = [], []
    susceptible, infected, recovered = [], [], []
    prevalence_age_risk, prevalence_genetic_risk = [], []
    prevalence_tobacco_risk, prevalence_diet_risk = [], []
    prevalence_physical_activity_risk, prevalence_alcohol_risk = [], []
    prevalence_lifestyle_risk = []

    line_plot_container1_title = st.empty()
    line_plot_container1 = st.empty()
    line_plot_container2_title = st.empty()
    line_plot_container2 = st.empty()
    line_plot_container3_title = st.empty()
    line_plot_container3 = st.empty()
    line_plot_container4_title = st.empty()
    line_plot_container4 = st.empty()

    for i in range(num_ticks + 1):
        model.step()
        my_bar.progress((i / num_ticks) if num_ticks else 1.0, text="Simulation progress")
        placeholder.text(f"Step = {i}")
        fig = create_figure()
        graph_container.pyplot(fig)
        plt.close(fig)

        total_infections.append(model.total_infections)
        vaccinations.append(model.vaccinations)
        prevalence.append(model.prevalence)
        incidence.append(model.incidence)
        susceptible.append(model.susceptible)
        infected.append(model.infected)
        recovered.append(model.recovered)
        prevalence_age_risk.append(model.prevalence_age_risk)
        prevalence_genetic_risk.append(model.prevalence_genetic_risk)
        prevalence_tobacco_risk.append(model.prevalence_tobacco_risk)
        prevalence_diet_risk.append(model.prevalence_diet_risk)
        prevalence_physical_activity_risk.append(model.prevalence_physical_activity_risk)
        prevalence_alcohol_risk.append(model.prevalence_alcohol_risk)
        prevalence_lifestyle_risk.append(model.prevalence_lifestyle_risk)

        line_plot_container1_title.write("Total Infections and Vaccinations")
        line_plot_container1.line_chart({'Total Infections': total_infections, 'Vaccinations': vaccinations})
        line_plot_container2_title.write("Prevalence and Incidence")
        line_plot_container2.line_chart({'Prevalence': prevalence, 'Incidence': incidence})
        line_plot_container3_title.write("SIR Graph")
        line_plot_container3.line_chart({'Susceptible': susceptible, 'Infected': infected, 'Recovered': recovered})
        line_plot_container4_title.write("Prevalence by Risk Factor")
        line_plot_container4.line_chart({
            'Age': prevalence_age_risk,
            'Genetic': prevalence_genetic_risk,
            'Tobacco': prevalence_tobacco_risk,
            'Diet': prevalence_diet_risk,
            'Physical Activity': prevalence_physical_activity_risk,
            'Alcohol': prevalence_alcohol_risk,
            'Lifestyle': prevalence_lifestyle_risk,
        })

        time.sleep(0.1)

    ever_infected = sum(1 for a in model.agents if a.wealth == 1 or a.num_recoveries > 0)
    peak_infected = max(infected) if infected else 0
    peak_day = infected.index(peak_infected) if infected else 0
    attack_rate = ever_infected / num_agents if num_agents else 0

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peak Infected", peak_infected, help=f"Reached on step {peak_day}")
    col2.metric("Ever Infected", ever_infected, f"{attack_rate:.0%} attack rate", delta_color="off")
    col3.metric("Vaccinations Given", model.vaccinations)
    col4.metric("Final Recovered", recovered[-1] if recovered else 0)

    with st.expander("Results dataframe"):
        st.dataframe(model.results_df)
    st.download_button(
        "Download results as CSV",
        model.results_df.to_csv().encode("utf-8"),
        file_name="network_simulation_results.csv",
        mime="text/csv",
    )


if run:
    if model_choice == "Traditional (Grid)":
        run_grid_simulation()
    else:
        run_network_simulation()
