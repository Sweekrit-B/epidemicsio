import mesa
import seaborn as sns
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import datetime
import os

matplotlib.use('Agg')

#https://pubmed.ncbi.nlm.nih.gov/11130187/
#https://www.sciencedirect.com/science/article/pii/S128645791000211X?via%3Dihub

output_path = "C:/Users/sweek/Documents/buildspace/output_data"

def compute_total_infections(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0)

def compute_prevalence(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0)/model.num_nodes
def compute_incidence(model):
    return model.new_cases / model.num_nodes
def compute_recovered(model):
    return sum(1 for agent in model.agents if agent.recovered == 1)
def compute_infected(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0)
def compute_susceptible(model):
    return sum(1 for agent in model.agents if agent.wealth == 0 and agent.num_recoveries < model.num_recoveries_for_immune)
def compute_vaccinated(model):
    return model.vaccinations
def compute_prevalence_age(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_age_risk != 1)/sum(1 for agent in model.agents if agent.increase_age_risk != 1)
def compute_prevalence_genetic(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_genetic_risk != 1)/sum(1 for agent in model.agents if agent.increase_genetic_risk != 1)
def compute_prevalence_lifestyle(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_lifestyle_risk != 1)/sum(1 for agent in model.agents if agent.increase_lifestyle_risk != 1)
def compute_prevalence_tobacco(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_tobacco_use != 1)/sum(1 for agent in model.agents if agent.increase_tobacco_use != 1)
def compute_prevalence_diet(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_unhealthy_diet != 1)/sum(1 for agent in model.agents if agent.increase_unhealthy_diet != 1)
def compute_prevalence_activity(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_physical_activity != 1)/sum(1 for agent in model.agents if agent.increase_physical_activity != 1)
def compute_prevalence_alcohol(model):
    return sum(1 for agent in model.agents if agent.wealth == 1 and agent.recovered == 0 and agent.increase_alcohol_use != 1)/sum(1 for agent in model.agents if agent.increase_alcohol_use != 1)


class NetworkAgent(mesa.Agent):
    def __init__(self, model=None):
        if model is None:
            raise ValueError("Model is None")
        # pass the parameters to the parent class
        # super().__init__(model)
        # create the agent's variable and set the initial values
        self.wealth = 0
        self.steps = 0
        self.recovered = 0
        self.num_recoveries = 0
        self.increase_age_risk = 1
        self.increase_genetic_risk = 1
        self.increase_tobacco_use = 1
        self.increase_unhealthy_diet = 1
        self.increase_physical_activity = 1
        self.increase_alcohol_use = 1
        self.increase_lifestyle_risk = 1
        self.chance_of_infection = self.model.chance_of_infection
        self.vaccinated = 0

        if self.unique_id < 2:
            self.wealth = 1
        if self.unique_id < self.model.vaccination_rate * self.model.num_nodes:
            self.vaccinated = self.model.vaccination_efficacy
        if random.random() < self.model.age_risk_proportion/100:
            self.increase_age_risk = 1.2
        if random.random() < self.model.genetic_risk_proportion/100:
            self.increase_genetic_risk = 1.2
        if random.random() < self.model.tobacco_risk_proportion/100:
            self.increase_tobacco_use = 1.2
        if random.random() < self.model.unhealthy_diet_proportion/100:
            self.increase_unhealthy_diet = 1.2
        if random.random() < self.model.physical_activity_proportion/100:
            self.increase_physical_activity = 1.2
        if random.random() < self.model.alcohol_use_proportion/100:
            self.increase_alcohol_use = 1.2
            self.increase_lifestyle_risk = self.increase_tobacco_use * self.increase_unhealthy_diet * self.increase_physical_activity * self.increase_alcohol_use * self.model.income_multiplier

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=2)
        if len(possible_steps) > 0:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def give_disease(self):
        neighbor_agents = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [agent for agent in neighbor_agents if agent.wealth == 0]
        if susceptible_neighbors:
            for a in susceptible_neighbors:
                if a.wealth == 0 and a.num_recoveries < a.model.num_recoveries_for_immune:
                    if a.random.random() < a.chance_of_infection/100 * a.increase_age_risk * a.increase_genetic_risk * a.increase_lifestyle_risk:
                        if random.random() > a.vaccinated:
                            a.recovered = 0
                            a.wealth = 1
                            self.model.new_cases += 1
                            break

    def step(self):
        self.move()
        if self.wealth == 1:
            self.give_disease()
            self.steps += 1
        elif self.wealth == 0:
            self.steps = 0
        if self.steps == self.model.num_steps:
            self.steps = 0
            self.wealth = 0
            self.recovered = 1
            self.num_recoveries += 1
            if self.increase_age_risk == 1.2:
                self.chance_of_infection *= 0.75
            elif self.increase_age_risk == 1:
                self.increase_age_risk *= 0.5

            #Vaccination code
            #Efficacy of vaccines - 30-40% for ages 65+ and 70-90% for ages <65
            if random.random() <= self.model.vaccination_rate/100:
                #Age factors
                if self.increase_age_risk == 1.2:
                    self.vaccinated = 0.35*self.model.vaccination_efficacy
                elif self.increase_age_risk == 1:
                    self.vaccinated = 0.80*self.model.vaccination_efficacy
                self.model.vaccinations += 1


class NetworkModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, chance_of_infection, graph_type, m_value, p_value, num_recoveries_for_immune, num_steps,  age_risk_proportion, genetic_risk_proportion, tobacco_risk_proportion, unhealthy_diet_proportion, physical_activity_proportion, alcohol_use_proportion, income_multiplier, vaccination_rate, vaccination_efficacy):

        super().__init__()
        
        self.num_nodes = N
        self.num_steps = num_steps

        self.results_df = pd.DataFrame(columns=[
            "Total Infections", "Prevalence", "Incidence", "Susceptible", "Infected", "Recovered", 
            "Vaccinations", "Prevalence - Age Risk", "Prevalence - Genetic Risk", 
            "Prevalence - Tobacco", "Prevalence - Diet", "Prevalence - Physical Activity", 
            "Prevalence - Alcohol Use", "Prevalence - Lifestyle Risk"
        ])

        #Defines the number of recoveries that are required for a person to become IMMUNE from a disease. This is to reflect the evolution of diseases, and different strains that may arise.
        self.num_recoveries_for_immune = num_recoveries_for_immune

        #The IMPLICIT chance of infection of getting diseases. This value chances depending on age, genetic, and lifestyle factors as defined above.
        self.chance_of_infection = chance_of_infection

        self.age_risk_proportion = age_risk_proportion
        self.genetic_risk_proportion = genetic_risk_proportion
        self.tobacco_risk_proportion = tobacco_risk_proportion
        self.unhealthy_diet_proportion = unhealthy_diet_proportion
        self.physical_activity_proportion = physical_activity_proportion
        self.alcohol_use_proportion = alcohol_use_proportion

        self.income_multiplier = income_multiplier
        
        #Vaccination rate describes the likelihood of agents getting the vaccine. This is a SOCIAL factor, almost as the acceptance of vaccination in the community.
        self.vaccination_rate = vaccination_rate

        #Vaccination efficacy is the vaccine's ability to block disease under IDEAL conditions. This value changes to become the EFFECTIVENESS of the vaccine when we deal with the agent class
        self.vaccination_efficacy = vaccination_efficacy/100
        
        self.vaccinations = 0

        #Here, need to generate a random graph, and then make a grid on it
        if graph_type == 'Barabasi Albert':
            #In a Barabasi Albert graph, the m value is the number of new edges per new node. Therefore, when a new node is added to the network, it establishes m edges to existing nodes. Nodes with more connections are more likely to receive new edges. A larger m value will increase the connectivity of new nodes, leading to a network with a high number of edges and more pronounced hubs.
            self.G = nx.barabasi_albert_graph(n=self.num_nodes, m=m_value)
        elif graph_type == 'Watts Strogatz':
            #In a Watts Strogatz graph, the p_value represents the probability of rewiring each edge, or the randomness of the graph. It controls the tradeoff between a regular lattice (p = 0), and a completely random graph (p = 1)
            self.G= nx.watts_strogatz_graph(n=self.num_nodes, k=6, p=p_value/10)
        elif graph_type == 'Erdos Renyi':
            #In an Erdos-Renyi graph, the p_value represents the probability that an edge exists between any pair of nodes. This probability controls the density of the network, with a p = 0 creating a graph with n isolated nodes and no edges, while a p = 1 creates a complete graph where everyr possible edge between nodes exists.
            self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=p_value/10)
        elif graph_type == 'Power Law Cluster':
            #In a Power-Law Cluster Graph, m is the number of new edges per node (the same as a Barabasi Albert graph). Meanwhile, p is the probability of adding a triangle, or when a new edge is added to the network, a triangle forming by adding an additional edge between two existing nodes that are both connected to the new node. A higher p value means higher clustering.
            self.G = nx.powerlaw_cluster_graph(n=self.num_nodes, m=m_value, p=p_value/10)
        self.grid = mesa.space.NetworkGrid(self.G)

        self.new_cases = 0
        self.new_recoveries = 0

        self.datacollector = mesa.DataCollector(model_reporters={
         "Total Infections": compute_total_infections,
         "Prevalence": compute_prevalence,
         "Incidence": compute_incidence,
         "Susceptible": compute_susceptible,
         "Infected": compute_infected,
         "Recovered": compute_recovered,
         "Vaccinations": compute_vaccinated,
         "Prevalence - Age Risk": compute_prevalence_age,
         "Prevalence - Genetic Risk": compute_prevalence_genetic,
         "Prevalence - Tobacco": compute_prevalence_tobacco,
         "Prevalence - Diet": compute_prevalence_diet,
         "Prevalence - Physical Activity": compute_prevalence_activity,
         "Prevalence - Alcohol Use": compute_prevalence_alcohol,
         "Prevalence - Lifestyle Risk": compute_prevalence_lifestyle},
        agent_reporters={"Wealth": "wealth"})

        self.total_infections = 1
        self.vaccinations = 0
        
        self.prevalence = 0
        self.incidence = 0

        self.susceptible = 0
        self.infected = 1
        self.recovered = 0

        self.prevalence_age_risk = 0
        self.prevalence_genetic_risk = 0
        self.prevalence_tobacco_risk = 0
        self.prevalence_diet_risk = 0
        self.prevalence_physical_activity_risk = 0
        self.prevalence_alcohol_risk = 0
        self.prevalence_lifestyle_risk = 0

    def create_agents(self):
        for i, node in enumerate(self.G.nodes()):
            a = NetworkAgent(model=self)
            # Add the agent to a node
            self.grid.place_agent(a, node)

    def step(self):
        self.datacollector.collect(self)

        self.total_infections = compute_total_infections(self)
        self.prevalence = compute_prevalence(self)
        self.incidence = compute_incidence(self)
        self.susceptible = compute_susceptible(self)
        self.infected = compute_infected(self)
        self.recovered = compute_recovered(self)
        self.vaccinations = compute_vaccinated(self)
        self.prevalence_age_risk = compute_prevalence_age(self)
        self.prevalence_genetic_risk = compute_prevalence_genetic(self)
        self.prevalence_tobacco_risk = compute_prevalence_tobacco(self)
        self.prevalence_diet_risk = compute_prevalence_diet(self)
        self.prevalence_physical_activity_risk = compute_prevalence_activity(self)
        self.prevalence_alcohol_risk = compute_prevalence_alcohol(self)
        self.prevalence_lifestyle_risk = compute_prevalence_lifestyle(self)

        new_row = {
            "Total Infections": self.total_infections,
            "Prevalence": self.prevalence,
            "Incidence": self.incidence,
            "Susceptible": self.susceptible,
            "Infected": self.infected,
            "Recovered": self.recovered,
            "Vaccinations": self.vaccinations,
            "Prevalence - Age Risk": self.prevalence_age_risk,
            "Prevalence - Genetic Risk": self.prevalence_genetic_risk,
            "Prevalence - Tobacco": self.prevalence_tobacco_risk,
            "Prevalence - Diet": self.prevalence_diet_risk,
            "Prevalence - Physical Activity": self.prevalence_physical_activity_risk,
            "Prevalence - Alcohol Use": self.prevalence_alcohol_risk,
            "Prevalence - Lifestyle Risk": self.prevalence_lifestyle_risk,
        }
    
        self.results_df = self.results_df._append(new_row, ignore_index=True)
        self.new_cases = 0
        self.agents.do("step")

        # if self.agents.do("step") != 1 and prevalence == 0.0:
        #     print("All agents have recovered. Simulation finished.")
        #     self.running = False
            # ct = str(datetime.datetime.now())
            # ct = ct.replace(':', '-')
            # ct = ct.replace(' ', '--')
            # filename = f'{ct}_network_model_run.csv'
            # filepath = os.path.join(output_path, filename)
            # self.results_df.to_csv(filepath, index=False)
            # print("Saved!")

"""model = NetworkModel(10, 3, 3)
for i in range(10):
    model.step()"""