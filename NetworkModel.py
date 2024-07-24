import mesa
import seaborn as sns
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx

matplotlib.use('TkAgg')

def compute_prevalence(model):
    return sum(1 for agent in model.schedule.agents if agent.wealth == 1 and agent.recovered == 0)/model.num_nodes
def compute_incidence(model):
    return model.new_cases / model.num_nodes
def compute_recovered(model):
    return sum(1 for agent in model.schedule.agents if agent.recovered == 1)
def compute_infected(model):
    return sum(1 for agent in model.schedule.agents if agent.wealth == 1 and agent.recovered == 0)
def compute_susceptible(model):
    return sum(1 for agent in model.schedule.agents if agent.wealth == 0 and agent.num_recoveries < model.num_recoveries_for_immune)

class NetworkAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        # pass the parameters to the parent class
        super().__init__(unique_id, model)
        # create the agent's variable and set the initial values
        self.wealth = 0
        self.steps = 0
        self.recovered = 0
        self.num_recoveries = 0

        self.increase_age_risk = 1
        self.increase_genetic_risk = 1
        self.increase_lifestyle_risk = 1

        id_list = []
        id_list.append(unique_id)
        for x in id_list:
            if x < 1:
                self.wealth = 1
            if random.random() < self.model.age_risk_proportion/100:
                self.increase_age_risk = 1.2
            if random.random() < self.model.genetic_risk_proportion/100:
                self.increase_genetic_risk = 1.2
            if random.random() < self.model.lifestyle_risk_proportion/100:
                self.increase_lifestyle_risk = 1.2

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, include_center=False, radius=2)
        if len(possible_steps) > 0:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def give_money(self):
        neighbor_agents = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [agent for agent in neighbor_agents if agent.wealth == 0]
        if susceptible_neighbors:
            for a in susceptible_neighbors:
                if a.wealth == 0 and a.num_recoveries < a.model.num_recoveries_for_immune:
                    if a.random.random() < a.model.chance_of_infection/100 * a.increase_age_risk * a.increase_genetic_risk * a.increase_lifestyle_risk:
                        a.recovered = 0
                        a.wealth = 1
                        self.model.new_cases += 1
                        break

    def step(self):
        self.move()
        if self.wealth == 1:
            self.give_money()
            self.steps += 1
            print(f"Agent {self.unique_id} has stepped {self.steps} times.")
        elif self.wealth == 0:
            self.steps = 0
        if self.steps == self.model.num_steps:
            self.steps = 0
            self.wealth = 0
            self.recovered = 1
            self.num_recoveries += 1
            print(f"Agent {self.unique_id} has stepped twice.")
            print(f"Agent {self.unique_id} has {self.num_recoveries}")


class NetworkModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, chance_of_infection, graph_type, m_value, p_value, num_recoveries_for_immune, num_steps,  age_risk_proportion, genetic_risk_proportion, lifestyle_risk_proportion):
        super().__init__()
        self.num_nodes = N
        self.num_steps = num_steps
        self.num_recoveries_for_immune = num_recoveries_for_immune
        self.chance_of_infection = chance_of_infection
        self.age_risk_proportion = age_risk_proportion
        self.genetic_risk_proportion = genetic_risk_proportion
        self.lifestyle_risk_proportion = lifestyle_risk_proportion
        self.schedule = mesa.time.RandomActivation(self)
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

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = NetworkAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.add(a)
            # Add the agent to a node
            self.grid.place_agent(a, node)

        self.datacollector = mesa.DataCollector(model_reporters={"Prevalence": compute_prevalence,
         "Incidence": compute_incidence,
         "Susceptible": compute_susceptible,
         "Infected": compute_infected,
         "Recovered": compute_recovered},
        agent_reporters={"Wealth": "wealth"})

    def step(self):
        self.datacollector.collect(self)

        prevalence = compute_prevalence(self)
        incidence = compute_incidence(self)
        susceptible = compute_susceptible(self)
        infected = compute_infected(self)
        recovered = compute_recovered(self)
        print(f"Step {self.schedule.steps}: Prevalence = {prevalence}, Incidence = {incidence}")
        print(f"Susceptible = {susceptible}, Infected = {infected}, Recovered = {recovered}")

        self.new_cases = 0
        self.schedule.step()

        if self.schedule.steps != 1 and prevalence == 0.0:
            print("All agents have recovered. Simulation finished.")
            self.running = False

"""model = NetworkModel(10, 3, 3)
for i in range(10):
    model.step()"""