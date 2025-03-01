import streamlit as st
from NetworkModel import NetworkModel
import networkx as nx
import matplotlib.pyplot as plt
import mesa.visualization
import pandas as pd
import time
import matplotlib

matplotlib.use('WebAgg')

st.title("Epidemics.io - Network Simulation")

with st.sidebar:
    st.title("Simulation Parameters")
    num_ticks = st.slider("Select number of steps for simulation", 0, 1000, 15)
    num_agents = st.slider("Number of Agents", 50, 500, 200)
    infection_chance = st.slider("Chance of Infection", 0, 100, 30)

    st.title("Risk Factors")
    age_risk = st.slider("Percent at-risk due to Age", 0, 100, 30)
    genetic_risk = st.slider("Percent at-risk due to Genetics", 0, 100, 30)
    tobacco_use = st.slider("Percent at-risk due to Smoking", 0, 100, 30)
    unhealthy_diet = st.slider("Percent at-risk due to Unhealthy Diet", 0, 100, 30)
    insufficient_physical_activity = st.slider("Percent at-risk due to Insufficient Physical Activity", 0, 100, 30)
    harmful_alcohol_use = st.slider("Percent at-risk due too Alcohol Use", 0, 100, 30)
    income_multiplier = st.slider("Income-based multiplier for increased lifestyle risk", value=1.2)

    st.title("Recovery Parameters")
    num_recoveries_slider = st.slider('Number of recoveries till immunity', 0, 10, 3)
    num_steps_recoveries_slider = st.slider("Number of steps till recovery", 0, 10, 3)
    vaccination_rate= st.slider("Vaccination rate", 0, 100, 30)
    vaccination_efficacy = st.slider("Vaccination efficacy", 0, 100, 75)

    st.title("Network Graph Parameters")
    graph_type_choice = st.selectbox("Graph type", options=['Barabasi Albert', 'Watts Strogatz', 'Erdos Renyi', 'Power Law Cluster'])
    p_value_slider = st.slider("P value", 0, 10, 4)
    m_value_slider = st.slider("M value", 0, 10, 3)

with st.expander("Citations"):
    url1 = "https://pubmed.ncbi.nlm.nih.gov/11130187/"
    st.write("[Impact of age-related immune dysfunction on risk of infections](%s)" % url1)
    url2 = "https://www.sciencedirect.com/science/article/pii/S128645791000211X?via%3Dihub"
    st.write("[Impact of aging on viral infections](%s)")
    url3 = "https://www.cdc.gov/globalhealth/healthprotection/fieldupdates/winter-2017/ncds-impact-ghs.html"
    st.write("[Three Ways NCDs Impact Global Health Security](%s)")
    url4 = "https://medcraveonline.com/JCCR/lifestyle-diseases-consequences-characteristics-causes-and-control.html"
    st.write("[Lifestyle Disease Consequences: Causes and Characteristics](%s)")

run = st.button("Run Simulation")

model = NetworkModel(num_agents, infection_chance, graph_type_choice, m_value_slider, p_value_slider, num_recoveries_slider, num_steps_recoveries_slider,  age_risk, genetic_risk, tobacco_use, unhealthy_diet, insufficient_physical_activity, harmful_alcohol_use, income_multiplier, vaccination_rate, vaccination_efficacy)
model.create_agents()

def get_colors():
    node_colors = []
    edge_colors = ['black' for edge in G.edges]
    for node_id in G.nodes:
        agents = model.grid.get_cell_list_contents([node_id])
        for agent in agents:
            if agent.wealth == 1 and agent.recovered == 0:
                node_colors.append('red')
            elif agent.wealth == 0 and agent.recovered == 1:
                node_colors.append('green')
            elif agent.wealth == 0 and agent.recovered == 0:
                node_colors.append('blue')
    return node_colors, edge_colors

def create_figure():
    node_colors, edge_colors = get_colors()
    fig, ax = plt.subplots(figsize=(8,8))
    nx.draw(G, pos, node_color=node_colors, edge_color=edge_colors, width = 0.6, node_size=30)
    return fig

def create_line_plot():
    fig, ax = plt.subplots(figsize=(4, 8))
    px.line(prevalence, incidence)
    return fig

if run:
    #init graph
    G = model.G
    pos = nx.spring_layout(G)

    #init progress bar
    my_bar = st.progress(0, text="Simulation Progress")
    placeholder = st.empty()

    graph_container = st.empty()
    
    total_infections = []
    vaccinations = []

    prevalence = []
    incidence = []

    susceptible = []
    infected = []
    recovered = []

    prevalence_age_risk = []
    prevalence_genetic_risk = []
    prevalence_tobacco_risk = []
    prevalence_diet_risk = []
    prevalence_physical_activity_risk = []
    prevalence_alcohol_risk = []
    prevalence_lifestyle_risk = []
    prevalence_alcohol_risk = []
    
    line_plot_container1_title = st.empty()
    line_plot_container1 = st.empty()
    line_plot_container2_title = st.empty()
    line_plot_container2 = st.empty()
    line_plot_container3_title = st.empty()
    line_plot_container3 = st.empty()
    line_plot_container4_title = st.empty()
    line_plot_container4 = st.empty()

    #simulation loop
    for i in range(num_ticks+1):
        model.step()
        my_bar.progress((i / num_ticks), text="Simulation progress")
        placeholder.text(f"Step = {i}")
        fig = create_figure()
        graph_container.pyplot(fig)

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

        chart1 = {'Total Infections': total_infections, 'Vaccinations': vaccinations}
        chart2 = {'Prevalence': prevalence, 'Incidence': incidence}
        chart3 = {'Susceptible': susceptible, 'Infected': infected, 'Recovered': recovered}
        chart4 = {'Age': prevalence_age_risk, 'Genetic': prevalence_genetic_risk, 'Tobacco': prevalence_tobacco_risk, 'Diet': prevalence_diet_risk, 'Physical Activity': prevalence_physical_activity_risk, 'Alcohol': prevalence_alcohol_risk, 'Lifestyle': prevalence_lifestyle_risk}

        line_plot_container1_title.write("Total Infections and Vaccinations")
        line_plot_container1.line_chart(chart1)
        line_plot_container2_title.write("Prevalence and Incidence")
        line_plot_container2.line_chart(chart2)
        line_plot_container3_title.write("SIR Graph")
        line_plot_container3.line_chart(chart3)
        line_plot_container4_title.write("Prevalence by Risk Factor")
        line_plot_container4.line_chart(chart4)

        time.sleep(0.1)
    
    results_df = model.results_df
    with st.expander("Results dataframe"):
        st.dataframe(results_df)




