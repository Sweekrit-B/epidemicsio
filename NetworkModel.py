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
    return sum(1 for agent in model.schedule.agents if agent.wealth == 0 and agent.recovered == 0)

class NetworkAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        # pass the parameters to the parent class
        super().__init__(unique_id, model)
        # create the agent's variable and set the initial values
        self.wealth = 0
        self.steps = 0
        self.recovered = 0
        id_list = []
        id_list.append(unique_id)
        for x in id_list:
            if x < 1:
                self.wealth = 1
            else:
                self.wealth = 0

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
                if a.wealth == 0 and a.recovered != 1:
                    if a.random.random() < a.model.chance_of_infection/10:
                        a.wealth = 1
                        self.model.new_cases += 1
                        break

    def step(self):
        self.move()
        if self.wealth == 1:
            self.give_money()
            self.steps += 1
        elif self.wealth == 0:
            self.steps = 0
        if self.steps == 14:
            self.wealth -= 1
            self.recovered = 1
            self.model.new_recoveries += 1


class NetworkModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, chance_of_infection, avg_node_degree):
        super().__init__()
        self.num_nodes = N
        prob = avg_node_degree / self.num_nodes

        self.chance_of_infection = chance_of_infection
        self.schedule = mesa.time.RandomActivation(self)
        
        #Here, need to generate a random graph, and then make a grid on it
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
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