from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from new import SchellingModel
from mesa_geo.visualization.MapModule import MapModule




class HappyElement(TextElement):
    """
    show happy agents count
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)


model_params = {
    "density": UserSettableParameter("slider", "Agent density", 0.6, 0.1, 1.0, 0.1),
    "minority_pc": UserSettableParameter(
        "slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05
    ),
}


def schelling_draw(agent):
  
    portrayal = dict()
    if agent.COLOR == "UNOCCUPIED":
        portrayal["color"] = "Grey"
    elif agent.COLOR == "RED":
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Green"
    return portrayal

happy_element = HappyElement()
map_element = MapModule(schelling_draw, [34, -118], 4, 500, 800)
happy_chart = ChartModule([{"Label": "happy", "Color": "Black"}])
server = ModularServer(
    SchellingModel, [map_element, happy_element, happy_chart], "Schelling", model_params
)

server.launch()
