"""
This module extends the RoleDcrGraph class to include support for milestone and
no-response relations within Dynamic Condition Response (DCR) Graphs.

The module adds functionality to handle milestone and no-response constraints,
allowing for more expressive process models with additional types of relations
between events.

Classes:
    MilestoneNoResponseDcrGraph: Extends RoleDcrGraph to include milestone and no-response relations.

This class provides methods to manage and manipulate milestone and no-response
relations within a DCR Graph, enhancing the model's ability to represent complex
process behaviors and dependencies.

References
----------
.. [1] Hildebrandt, T., Mukkamala, R.R., Slaats, T. (2012). Nested Dynamic Condition Response Graphs. In: Arbab, F., Sirjani, M. (eds) Fundamentals of Software Engineering. FSEN 2011. Lecture Notes in Computer Science, vol 7141. Springer, Berlin, Heidelberg. `DOI <https://doi.org/10.1007/978-3-642-29320-7_23>`_.

.. [2] Hildebrandt, T.T., Normann, H., Marquard, M., Debois, S., Slaats, T. (2022). Decision Modelling in Timed Dynamic Condition Response Graphs with Data. In: Marrella, A., Weber, B. (eds) Business Process Management Workshops. BPM 2021. Lecture Notes in Business Information Processing, vol 436. Springer, Cham. `DOI <https://doi.org/10.1007/978-3-030-94343-1_28>`_.
"""
from typing import Dict, Set

from pm4py.objects.dcr.distributed.obj import DistributedDcrGraph
from pm4py.objects.dcr.obj import DcrGraph

class ExtendedDcrGraph(DistributedDcrGraph):
    """
    This class extends the RoleDcrGraph to include milestone and no-response
    relations, allowing for more expressive DCR Graphs with additional constraints.


    Attributes
    ----------
    self.__milestonesFor: Dict[str, Set[str]]
        A dictionary mapping events to sets of their milestone events.
    self.__noResponseTo: Dict[str, Set[str]]
        A dictionary mapping events to sets of their no-response events.

    Methods
    -------
    obj_to_template(self) -> dict:
        Converts the object to a template dictionary, including milestone and no-response relations.
    get_constraints(self) -> int:
        Computes the total number of constraints in the DCR Graph, including milestone and no-response relations.
    """
    def __init__(self, template=None):
        super().__init__(template)
        self.__milestonesFor = {} if template is None else template['milestonesFor']
        self.__noResponseTo = {} if template is None else template['noResponseTo']
        self.__superActivities = {} if template is None else template['superActivities']
    def obj_to_template(self):
        res = super().obj_to_template()
        res['milestonesFor'] = self.__milestonesFor
        res['noResponseTo'] = self.__noResponseTo
        res['superActivities'] = self.__superActivities
        return res
    
    @DcrGraph.conditions.setter
    def conditions(self, value: Dict[str, Set[str]]):          
        self._DcrGraph__conditionsFor = self.nestingUpdate(value)

    @DcrGraph.includes.setter
    def includes(self, value: Dict[str, Set[str]]):          
        self._DcrGraph__includesTo = self.nestingUpdate(value)
    
    @DcrGraph.responses.setter
    def responses(self, value: Dict[str, Set[str]]):          
        self._DcrGraph__responseTo = self.nestingUpdate(value)
    
    @DcrGraph.excludes.setter
    def excludes(self, value: Dict[str, Set[str]]):          
        self._DcrGraph__excludesTo = self.nestingUpdate(value)
    
    def nestingUpdate(self, value: Dict[str, Set[str]]):
        # Loop over keys (Condition to key from value)
        for event in set(value.keys()):
            for event_prime in set(value[event]):
                if event_prime in self.superActivities:
                    event_prime_activities = self.superActivities[event_prime]
                    value[event].update(event_prime_activities)
                    value[event].remove(event_prime)

        # Loop over keys (Condition to value to key)
        for event in set(value.keys()):
            if event in self.superActivities:
                for e_prime in self.superActivities[event]:
                    value[e_prime] = value[event]
                    # Add the e_prime to the event that conditions the superevent
                # Remove the condition to the superActivity
                del value[event]   
        return value
    # Keys are the super activities, and they point to a set (which contains their)
    # sub activities
    @property 
    def superActivities(self) -> Dict[str, Set[str]]:
        return self.__superActivities
    
    @superActivities.setter
    def superActivities(self, value: Dict[str, Set[str]]):
        self.__superActivities = value
    
    @property
    def milestones(self) -> Dict[str, Set[str]]:
        return self.__milestonesFor
    
    @milestones.setter
    def milestones(self, value: Dict[str, Set[str]]):
        self.__milestonesFor = value

    @property
    def noresponses(self) -> Dict[str, Set[str]]:
        return self.__noResponseTo

    @noresponses.setter
    def noresponses(self, value: Dict[str, Set[str]]):
        self.__noResponseTo = value

    def get_constraints(self) -> int:
        no = super().get_constraints()
        for i in self.__milestonesFor.values():
            no += len(i)
        for i in self.__noResponseTo.values():
            no += len(i)
        return no

    def __eq__(self, other):
        return super().__eq__(other) and self.milestones == other.milestones and self.noresponses == other.noresponses

