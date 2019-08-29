"""
controlarea.py - This module defines a cost function that penalizes
the "area under the curve" of the control pulse.
"""

from qoc.models import (Cost, OperationPolicy)
from qoc.standard.convenience import sum_axis

class ControlArea(Cost):
    """
    This cost penalizes the area under the
    function of time generated by the discrete control parameters.
    
    Fields:
    cost_multiplier
    dt :: float - the time inbetween control steps
    max_control_norms
    normalization_constant :: float - used to normalize the cost
    """

    def __init__(self, control_count,
                 control_step_count, evolution_time,
                 max_control_norms,
                 cost_multiplier=1.):
        """
        See class docstring for arguments not listed here.
        
        Args:
        control_step_count
        evolution_time
        """
        super().__init__(cost_multiplier=cost_multiplier)
        self.dt = evolution_time / control_step_count
        self.max_control_norms = max_control_norms
        self.normalization_constant = control_count * control_step_count


    def cost(self, controls, states, system_step,
             operation_policy=OperationPolicy.CPU):
        """
        Compute the penalty.

        Args:
        controls
        operation_policy
        states
        system_step
        
        Returns:
        cost
        """
        normalized_step_areas = (self.dt / self.max_control_norms) * controls
        cost = sum_axis(normalized_step_areas,
                        operation_policy=operation_policy)
        cost_normalized = cost / self.normalization_constant

        return cost_normalized * self.cost_multiplier