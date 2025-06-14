
"""
.. module:: servicestatetables
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: servicestatetables module.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Dict, Optional

from xml.etree.ElementTree import Element

def process_state_table(service_state_table_el: Element, namespaces: Optional[dict] = None) -> dict:
    # pylint: disable=no-self-use
    variablesTable = {}
    typesTable = {}
    eventsTable = {}

    state_variable_el_list = service_state_table_el.findall("stateVariable", namespaces=namespaces)
    for state_variable_el in state_variable_el_list:
        name = state_variable_el.find("name", namespaces=namespaces).text
        dataType = state_variable_el.find("dataType", namespaces=namespaces).text

        varInfo = { "name": name, "dataType": dataType}
        if name.startswith("A_ARG_TYPE_"):
            typesTable[name] = varInfo
        else:
            variablesTable[name] = varInfo

            sendEvents = "no"
            if "sendEvents" in state_variable_el.attrib:
                sendEvents = state_variable_el.attrib["sendEvents"]

            if sendEvents == "yes":
                eventsTable[name] = varInfo

    return variablesTable, typesTable, eventsTable


class ServiceVariableDesc:
    """
        Represents a state variable in a UPnP service description.
    
        This class is used to represent a state variable in a UPnP service description. It can be extended to include methods for manipulating state variables.
    """
    
    def __init__(self, *, name: str, dataType: str, sendEvents: bool = False):
        self.name = name
        self.dataType = dataType
        self.sendEvents = sendEvents
        return
    
    def as_dict(self) -> dict:
        """
            Convert the ServiceVariableDesc object to a dictionary.
        
            :returns: Dictionary representation of the ServiceVariableDesc object.
        """
        rtnval = {
            "name": self.name,
            "dataType": self.dataType,
            "sendEvents": self.sendEvents
        }

        return rtnval
    

class ServiceStateTables:
    """
        Represents the ServiceStateTable in a UPnP service description.
    
        This class is used to manage the state variables of a UPnP service.  It can be extended to include methods for manipulating state variables.
    """
    
    def __init__(self, *, variablesTable=None, typesTable=None, eventsTable=None):
        self.variablesTable = variablesTable if variablesTable is not None else {}
        self.typesTable = typesTable if typesTable is not None else {}
        self.eventsTable = eventsTable if eventsTable is not None else {}
        return
