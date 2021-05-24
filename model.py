import geopandas
import shapely.geometry
import fiona
from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import RandomActivation
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from mesa.time import BaseScheduler
import random

'''write block shapefile to geojson'''
shp_file = geopandas.read_file(r'C:\ESRIPress\AgentAnalyst\Chapter03\Data\blocks.shp')
shp_file.to_file('blocks.geojson', driver='GeoJSON')



class SchellingAgent(GeoAgent):
    """Schelling-Segregation-Model """

    def __init__(self, unique_id, model, shape, agent_type=None):
        """create a Schelling agent.

        Args:
            unique_id: agent ID.
            agent_type: agent type (minority=1, majority=0)
        """
        super().__init__(unique_id, model, shape)
        self.agentType = agent_type


    def step(self):
        """define agent step."""
        similar = 0
        different = 0
        neighbors = self.model.grid.get_neighbors(self)
        if neighbors:
            for neighbor in neighbors:
                if neighbor.COLOR != "UNOCCUPIED":
                    continue
                elif neighbor.COLOR == self.COLOR:
                    similar += 1
                else:
                    different += 1

        # if the similar neighbors are less than different agent,move
        if similar < different:
            # choose an empty agent("unoccupied")
            empties = [a for a in self.model.grid.agents if a.COLOR == "UNOCCUPIED"]
            # add new agentType and delete old agentType  on scheduler
            new_region = random.choice(empties)
            new_region.COLOR = self.COLOR
            self.model.schedule.add(new_region)
            self.COLOR = "UNOCCUPIED"
            self.model.schedule.remove(self)
        else:
            self.model.happy += 1

    def __repr__(self):
        return "Agent " + str(self.unique_id)
        print(self.COLOR)


class SchellingModel(Model):
    """model class Schelling segregation model."""

    def __init__(self, density, minority_pc):
        self.density = density
        self.minority_pc = minority_pc

        self.schedule = RandomActivation(self)
        self.grid = GeoSpace()
        self.steps = 0

        self.happy = 0
        self.datacollector = DataCollector({"happy": "happy"})

        self.running = True

        # add geojson on the grid
        agent_kwargs = dict(model=self)
        AC = AgentCreator(agent_class=SchellingAgent, agent_kwargs=agent_kwargs)
        #read geojson file
        agents = AC.from_file("blocks.geojson")
        self.grid.add_agents(agents)

        # set agents
        for agent in agents:
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent.COLOR = "GREEN"
                else:
                    agent.COLOR = "RED"
                self.schedule.add(agent)

    def step(self):
        """run one step.

        when all agents are happy,stop
        """
        self.happy = 0  # reset happy agents
        self.steps += 1
        self.schedule.step()

        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False


