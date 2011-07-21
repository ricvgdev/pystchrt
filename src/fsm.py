'''
Finite State Machine
'''
import types
from abc import ABCMeta, abstractmethod

def get_object_class(obj):
    if    isinstance(obj, types.ClassType) \
       or isinstance(obj, types.TypeType):
        return obj
    elif isinstance(obj, types.NoneType):
        return types.NoneType
    else:
        return obj.__class__
        

class Event(object):
    
    def __new__(cls, name = ''):
        obj = object.__new__(cls)
        obj.name = name
        return obj
    
    def get_name(self):
        if self.name != '':
            return self.name
        else:
            my_cls = get_object_class(self)
            return my_cls.__name__

    def __repr__(self):
        return self.get_name()
    
    def __eq__(self, other):
        if not Event.is_event_or_event_type(other):
            return False
        other_cls = get_object_class(other)
        my_cls = get_object_class(self)
        return issubclass(my_cls, other_cls) or issubclass(other_cls, my_cls) 
    
    @staticmethod
    def is_event_or_event_type(event):
        event_cls = get_object_class(event)
        return issubclass(event_cls, (Event))


def alwaysTrueGuard(*args):
    """Used to define event handlers without guard that always execute
    the effect method"""
    return True

def nop(*args, **kargs):
    pass


class EventHandlerResponse:
    """Abstract type used to define generic behavior for handler event result"""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, handler):
        """Verifies that the argument is of type EventHandler and it records
        the handler's last guard execution result"""
        EventHandlerResponse.__assertArgIsAnEventHandler(handler)
        self.was_effect_triggered = handler.guard_result
        
    @staticmethod
    def __assertArgIsAnEventHandler(arg):
        assert(isinstance(arg, EventHandlerWithGuardAndEffect))


class EventHandlerWithGuardAndEffect:
    """Abstract class with general functionality for event handlers"""
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, guard, effect, response_type):
        """Event handler requires a guard and effect method and the response
        type to be returned when an event is processed"""
        self.guard = guard
        self.effect = effect
        self.last_event = None
        self.guard_result = None
        self.last_response = None
        self.__response_type = response_type
        self.__assertResponseTypeisSubclassOfEventHandlerResponse()
    
    def __assertResponseTypeisSubclassOfEventHandlerResponse(self):
        assert(issubclass(self.__response_type, EventHandlerResponse))
    
    def process_event(self, event):
        """Executes effect method if guard is True and return an instance
        of self.__response_type"""
        self.last_event = event
        self.__execGuardAndAssertOutputIsBoolean()
        self.__execEffectIfGuardResultIsTrue()
        self.__buildResponseWithGuardResult()
        return self.last_response

    def __execEffectIfGuardResultIsTrue(self):
        self.__assertEffectIsNotNone()
        if self.guard_result:
            self.effect(self.last_event)

    def __buildResponseWithGuardResult(self):
        self.last_response = self.__response_type(self)
    
    def __assertGuardIsNotNone(self):
        assert(not self.guard is None)
        
    def __assertEffectIsNotNone(self):
        assert(not self.effect is None)
        
    def __execGuardAndAssertOutputIsBoolean(self):
        self.__assertGuardIsNotNone()
        self.guard_result = self.guard(self.last_event)
        self.__assertGuardResultIsBoolean()
    
    def __assertGuardResultIsBoolean(self):
        assert(type(self.guard_result) is bool)
    
    def __repr__(self):
        return self.get_name()

    def get_name(self):
        effect = self.effect.__name__
        guard = self.guard.__name__
        
        if self.guard == alwaysTrueGuard:
            out = '{effect}()'.format(effect=effect)
        else:
            out = '[{guard}] {effect}()'.format(effect=effect, guard=guard)
        return out


class TransitionResponse(EventHandlerResponse):
    """Result of a transition after handling an event"""
    
    def __init__(self, transition):
        EventHandlerResponse.__init__(self, transition)
        self.__addTargetToResponse(transition)

    def __addTargetToResponse(self, transition):
        if self.was_effect_triggered:
            self.target = transition.target
        else:
            self.target = None


class TransitionWithGuardAndEffect(EventHandlerWithGuardAndEffect):
    
    def __init__(self, guard, target, effect):
        EventHandlerWithGuardAndEffect.__init__(self, guard, effect, TransitionResponse)
        self.target = target
    
    def get_name(self):
        name = EventHandlerWithGuardAndEffect.get_name(self) + ' -> '
        if None != self.target:
            name += self.target.get_name()
        return name
    

class TransitionWithGuard(TransitionWithGuardAndEffect):

    def __init__(self, guard, target):
        TransitionWithGuardAndEffect.__init__(self, guard=guard,
                                              target=target, effect=nop)


class TransitionWithEffect(TransitionWithGuardAndEffect):

    def __init__(self, target, effect):
        TransitionWithGuardAndEffect.__init__(self, guard=alwaysTrueGuard,
                                              target=target, effect=effect)


class Transition(TransitionWithGuardAndEffect):
    """Type used to define an unnamed transition (i.e. triggers always a
    transition to the target state"""

    def __init__(self, target):
        TransitionWithGuardAndEffect.__init__(self, guard=alwaysTrueGuard,
                                              target=target, effect=nop)


class ActivityWithGuard(EventHandlerWithGuardAndEffect):
    
    def __new__(cls, guard, action):
        activity = EventHandlerWithGuardAndEffect.__new__(cls, guard=guard,
                                                          effect=action)
        return activity


class Activity(ActivityWithGuard):
    
    def __new__(cls, action):
        activity = ActivityWithGuard.__new__(cls, guard=alwaysTrueGuard, action=action)
        return activity


class EventHandlers(object):
    
    def __init__(self, stop_at_first_trigger):
        self.handlers = []
        self.stop_at_first_trigger = stop_at_first_trigger

    def process_event(self, event):
        last_triggered_tuple = (False,)
        for handler in self.handlers:
            tuple_res = handler.process_event(event)
            
            triggered = tuple_res.was_effect_triggered()

            if triggered:
                last_triggered_tuple = tuple_res
            
            if self.stop_at_first_trigger and triggered:
                break
        return last_triggered_tuple
    
    def add_handler(self, handler):
        self.__assertArgIsAnEventHandler(handler)
        self.handlers.append(handler)
    
    def __assertArgIsAnEventHandler(self, arg):
        assert(isinstance(arg, (EventHandlerWithGuardAndEffect)))
    
    def __iter__(self):
        for handler in self.handlers:
            yield handler
    
    def __repr__(self):
        return self.handlers.__repr__()


class TransitionList(EventHandlers):
    
    def __init__(self, transitions_arg = []):
        EventHandlers.__init__(self, stop_at_first_trigger=True)
        for transition in transitions_arg:
            self.add_transition(transition)
    
    def process_event(self, event):
        tuple_res = EventHandlers.process_event(self, event)
        if len(tuple_res) == 1:
            return (False, None)
        else:
            return tuple_res 

    def add_transition(self, transition):
        assert(isinstance(transition, (TransitionWithGuardAndEffect)))
        EventHandlers.add_handler(self, handler=transition)
    
    def add_handler(self, handler):
        # Don't use this. Use add_transition instead.
        assert(False)
    

class ActivityList(EventHandlers):
    
    def __init__(self, activities_arg = []):
        EventHandlers.__init__(self, stop_at_first_trigger=False)
        for activity in activities_arg:
            self.add_activity(activity)
    
    def add_activity(self, activity):
        assert(isinstance(activity, (ActivityWithGuard)))
        EventHandlers.add_handler(self, handler=activity)
    
    def add_handler(self, handler):
        # Don't use this. Use add_activity instead.
        assert(False)
    

class EventDictOfHandlerLists(object):
    
    def __init__(self):
        object.__init__(self)
        self.list_dict = {}
    
    def __contains__(self, event):
        return self.has_handlers_for_event(event)
    
    def has_handlers_for_event(self, event):
        event_cls = get_object_class(event)
        return event_cls in self.list_dict
    
    def __repr__(self):
        return self.list_dict.__repr__()
    

class EventDictOfTransitions(EventDictOfHandlerLists):

    def __init__(self):
        EventDictOfHandlerLists.__init__(self)

    def process_event(self, event):
        if event not in self:
            return (False, None)
        
        event_cls = get_object_class(event)
        transition_list = self.list_dict[event_cls]
        return transition_list.process_event(event)

    def add_transition(self, event, transition):
        event_cls = get_object_class(event)
        if event_cls not in self.list_dict:
            self.list_dict[event_cls] = TransitionList()

        transition_list = self.list_dict[event_cls]
        transition_list.add_transition(transition)
    
    def clear(self, event):
        event_cls = get_object_class(event)
        if event_cls in self.list_dict:
            del self.list_dict[event_cls]
        


class EventDictOfActivities(EventDictOfHandlerLists):

    def __init__(self):
        EventDictOfHandlerLists.__init__(self)

    def process_event(self, event):
        if event not in self:
            return (False,)
        
        event_cls = get_object_class(event)
        transition_list = self.list_dict[event_cls]
        return transition_list.process_event(event)

    def add_activity(self, event, activity):
        event_cls = get_object_class(event)
        if event_cls not in self.list_dict:
            self.list_dict[event_cls] = ActivityList()

        activity_list = self.list_dict[event_cls]
        activity_list.add_activity(activity)


class StimulusResponse(tuple):
    
    def __new__(cls, activity, transition, target):
        assert(isinstance(activity, (bool)))
        assert(isinstance(transition, (bool)))
        if target != None:
            assert(isinstance(transition, (bool)))
        tpl = tuple.__new__(cls, (activity, transition, target))
        return tpl
    
    def did_act_or_requested_transition(self):
        return self.did_act() or self.was_transition_requested()

    def did_act(self):
        return self[0]
    
    def was_transition_requested(self):
        return self[1] and None != self.get_target()
    
    def get_target(self):
        return self[2]


class State:
    
    __metaclass__ = ABCMeta
    
    class EnterEvent(Event):
        pass
    
    class ExitEvent(Event):
        pass
    
    class UnnamedEvent(Event):
        pass
    
    @abstractmethod
    def __init__(self, name = ''):
        object.__init__(self)
        self.name = name
        self.activities = EventDictOfActivities()
        self.transitions = EventDictOfTransitions()
        self._active = False

    def process_event(self, event):
        activity_triggered, = self.activities.process_event(event)
        transition_triggered, target = self.transitions.process_event(event)
        return StimulusResponse(activity_triggered, transition_triggered, target)
        
    def enter(self):
        self._active = True
        return State.process_event(self, State.EnterEvent)
    
    def exit(self):
        exit_response = State.process_event(self, State.ExitEvent)
        self._active = False
        return exit_response
    
    def start(self):
        return StimulusResponse(False, False, None)
    
    def stop(self):
        return StimulusResponse(False, False, None)
    
    def add_enter_activity(self, activity):
        self.add_activity(event=State.EnterEvent, activity=activity)
    
    def add_exit_activity(self, activity):
        self.add_activity(event=State.ExitEvent, activity=activity)
    
    def add_activity(self, event, activity):
        self.activities.add_activity(event, activity)
    
    def add_unnamed_transition(self, transition):
        self.add_transition(State.UnnamedEvent, transition)
    
    def add_transition(self, event, transition):
        self.transitions.add_transition(event, transition)
    
    def has_activities_for(self, event):
        return event in self.activities
    
    def has_transition_for(self, event):
        return event in self.transitions
    
    def is_active(self):
        return self._active
    
    def get_name(self):
        if self.name != '':
            return self.name
        else:
            return self.__class__.__name__
    
    def info(self, level = 0, indent = '  '):
        return "{indent}{name}: State".format(indent=level*indent, name=str(self))


    def __repr__(self):
        return self.get_name()


class StateList(list):
    pass


class FSM(object):
    
    class InitialState(State):
        
        def __init__(self):
            State.__init__(self, name="")

        def set_initial_transition(self, other):
            transition = Transition(target=other)
            self.transitions.clear(State.UnnamedEvent)
            self.transitions.add_transition(State.UnnamedEvent, transition)


    class FinalState(State):

        def __init__(self):
            State.__init__(self, name="")

        def add_final_transition_to_other(self, other):
            if other != self:
                to_final = Transition(self)
                other.add_transition(State.ExitEvent, to_final)
    

    def __init__(self, states =[], initial = InitialState(), final = FinalState()):
        object.__init__(self)
        self.state_change_activities = ActivityList()
        self.initial = initial
        self.final = final
        if len(states) > 0 and states[0] != None:
            set_inital_state = True
            if states[0] == None:
                states.remove(0)
        else:
            set_inital_state = False
        
        self.states = StateList(states)
        self.current = self.initial
        if set_inital_state:
            self.set_initial_state(states[0])
        else:
            self.set_initial_state(self.final) # Default transition
    
    def start(self):
        assert(self.current == self.initial or self.current == self.final)
        self.current = self.initial
        return self.process_event(State.EnterEvent)

    def stop(self):
        if self.current != self.final:
            self.final.add_final_transition_to_other(other=self.current)
            return self.process_event(State.ExitEvent)
        else:
            return StimulusResponse(False, False, None)
    
    def add_start_activity(self, activity):
        self.initial.add_enter_activity(activity)
    
    def add_stop_activity(self, activity):
        self.final.add_enter_activity(activity)
    
    def add_on_transition_completed_activity(self, activity):
        self.state_change_activities.add_activity(activity)
    
    def set_initial_state(self, state):
        assert(state in self or state == self.final)
        self.initial.set_initial_transition(state)
    
    def process_event(self, event):
        while True:
            response, send_unnamed = self._dipatch_to_current(event)
            
            if send_unnamed or event == State.EnterEvent:
                event = State.UnnamedEvent
            elif not response.was_transition_requested():
                break
        return response

    def _dipatch_to_current(self, event):

        response = self.current.process_event(event)
        
        exit = StimulusResponse(False, False, None)
        enter = StimulusResponse(False, False, None)
        unnamed_event_needed = False
        if    response.was_transition_requested():
            exit = self.current.exit()
            self.current = response.get_target()
            enter = self.current.enter()
            self.state_change_activities.process_event(Event)
            unnamed_event_needed = True
        
        agregated_response = StimulusResponse(   response.did_act() or exit.did_act()
                                              or enter.did_act(),
                                              response.was_transition_requested(),
                                              response.get_target())
        return (agregated_response, unnamed_event_needed)
    
    def __contains__(self, state):
        return state in self.states

    def name(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return self.name()
    
