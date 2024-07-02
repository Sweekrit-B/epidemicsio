import mesa
import seaborn as sns
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')
def compute_prevalence(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    l = len(agent_wealths)
    c = sum(agent_wealths)
    return c/l

def compute_incidence(model):
    return model.new_cases / model.num_agents
def compute_recovered(model):
    agent_recovered = [agent.recovered for agent in model.schedule.agents]
    l = len(agent_recovered)
    r = sum(agent_recovered)
    return r

def compute_infected(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    i = sum(agent_wealths)
    return i

def compute_susceptible(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    agent_recovered = [agent.recovered for agent in model.schedule.agents]
    i = sum(agent_wealths)
    r = sum(agent_recovered)
    return len(agent_wealths)-i-r

class MoneyAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        # pass the parameters to the parent class
        super().__init__(unique_id, model)
        # create the agent's variable and set the initial values
        self.x = None
        self.y = None
        self.wealth = 0
        self.steps = 0
        self.recovered = 0
        id_list = []
        id_list.append(unique_id)
        '''for x in id_list:
            if x < 1:
                self.wealth = 1
            else:
                self.wealth = 0'''

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.x, self.y = new_position
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_neighbors(self.pos, include_center=True, moore=True)
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            a = random.randrange(1, 10)
            if self.wealth == 1 and other.wealth < 1 and other.recovered != 1 and a <= self.model.chance_of_infection:
                other.wealth += 1
                self.model.new_cases += 1

    def in_recovery_zone(self):
        selected_cells = self.model.recovery_layer.select_cells(condition=lambda value: value == 1.0)
        selected_cells_clean = [(int(x), int(y)) for x, y in selected_cells]
        pos_tuple = (self.x, self.y)
        if pos_tuple in selected_cells_clean:
            return True
        else:
            return False

    def in_infectious_zone(self):
        selected_cells = self.model.infectious_layer.select_cells(condition=lambda value: value == 1.0)
        selected_cells_clean = [(int(x), int(y)) for x, y in selected_cells]
        pos_tuple = (self.x, self.y)
        if pos_tuple in selected_cells_clean:
            return True
        else:
            return False

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()
            self.steps += 1
        elif self.wealth < 1:
            self.steps = 0
        '''if self.steps == 14:
            self.wealth = 0
            self.recovered = 1
            self.model.new_recoveries += 1
            '''
        if self.in_recovery_zone() and self.wealth == 1:
            self.wealth = 0
            self.recovered = 1
            self.model.new_recoveries += 1
        if self.in_infectious_zone() and self.wealth == 0 and self.recovered == 0:
            self.wealth = 1
            self.model.new_cases += 1


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, N, recovery_size, infectious_size, chance_of_infection, width, height):
        super().__init__()
        self.num_agents = N
        self.chance_of_infection = chance_of_infection
        self.recovery_size = recovery_size
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.recovery_layer = mesa.space.PropertyLayer(
            name = "recovery_zone",
            width = width,
            height = height,
            default_value=0.0,
            dtype = np.float64
        )

        self.infectious_layer = mesa.space.PropertyLayer(
            name = "infectious_layer",
            width = width,
            height = height,
            default_value = 0.0,
            dtype = np.float64
        )

        for x in range(recovery_size):
            for y in range(recovery_size):
               self.recovery_layer.set_cell((x, y), 1.0)

        for x in range(width-infectious_size, width):
            for y in range(height-infectious_size, height):
                self.infectious_layer.set_cell((x, y), 1.0)

        self.new_cases = 0
        self.new_recoveries = 0
        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            # Add the agent to the scheduler
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

            a.x = x
            a.y = y

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

'''model = MoneyModel(10, 2, 4, 4)
for i in range(10):
    model.step()'''