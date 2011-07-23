'''
Finite State Machine
'''
import types
from abc import ABCMeta, abstractmethod

def get_object_class(obj):
    """Returns the type of the argument""" 
    if    isinstance(obj, types.ClassType) \
       or isinstance(obj, types.TypeType):
        # Return the argument if this one is a type.
        return obj
    elif isinstance(obj, types.NoneType):
        # Special case: None
        return types.NoneType
    else:
        # Argument type
        return obj.__class__
        

class Event(object):
    
    def __new__(cls):
        obj = object.__new__(cls)
        return obj
    
    def get_name(self):
        return get_object_class(self).__name__
    
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


class EventHandlerResult:
    """Abstract type used to define generic behavior for result objects"""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, handler):
        """Builds by default a result as if the handler's guard returned
        False and no effect method was executed, then it retrieves the
        actual guard result if handler is valid."""
        self.__setAsIfHandlerDidNothing()
        self.__getHandlerGuardResultIfHandlerIsNotNone(handler)
    
    def was_handler_triggered(self):
        return self.handler_triggered
    
    def __setAsIfHandlerDidNothing(self):
        self.handler_triggered = False
        
    def __getHandlerGuardResultIfHandlerIsNotNone(self, handler):
        if None != handler:
            EventHandlerResult.__assertArgIsAnEventHandler(handler)
            self.handler_triggered = handler.guard_result
        
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
        assert(issubclass(self.__response_type, EventHandlerResult))
    
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


class TransitionResult(EventHandlerResult):
    """Result of a transition after handling an event"""
    
    def __init__(self, transition):
        EventHandlerResult.__init__(self, transition)
        self.__addTargetToResponse(transition)

    def __addTargetToResponse(self, transition):
        if None != transition and self.handler_triggered:
            self.target = transition.target
        else:
            self.target = None
    
    @staticmethod
    def buildResultForUntriggeredTransition():
        return TransitionResult(transition=None)



class TransitionWithGuardAndEffect(EventHandlerWithGuardAndEffect):
    """Transition that executes an effect if the guard is True"""
    
    def __init__(self, guard, target, effect):
        EventHandlerWithGuardAndEffect.__init__(self, guard, effect, TransitionResult)
        self.target = target
    
    def get_name(self):
        name = EventHandlerWithGuardAndEffect.get_name(self) + ' -> '
        if None != self.target:
            name += self.target.get_name()
        return name
    

class TransitionWithGuard(TransitionWithGuardAndEffect):
    """Transition that is only valid if the guard returns True"""

    def __init__(self, guard, target):
        TransitionWithGuardAndEffect.__init__(self, guard=guard,
                                              target=target, effect=nop)


class TransitionWithEffect(TransitionWithGuardAndEffect):
    """Transition that is always valid and that executes an effect"""

    def __init__(self, target, effect):
        TransitionWithGuardAndEffect.__init__(self, guard=alwaysTrueGuard,
                                              target=target, effect=effect)


class Transition(TransitionWithGuardAndEffect):
    """Simple transition that is always valid"""

    def __init__(self, target):
        TransitionWithGuardAndEffect.__init__(self, guard=alwaysTrueGuard,
                                              target=target, effect=nop)


class ActivityResult(EventHandlerResult):
    
    def __init__(self, activity):
        EventHandlerResult.__init__(self, activity)
    
    @staticmethod
    def buildResultForUntriggeredActivity():
        return ActivityResult(activity=None)


class ActivityWithGuard(EventHandlerWithGuardAndEffect):
    """Event handler used to execute an action method whenever the guard
    returns True when processing an event."""
    
    def __init__(self, guard, action):
        EventHandlerWithGuardAndEffect.__init__(self, guard=guard,
                                effect=action, response_type = ActivityResult)


class Activity(ActivityWithGuard):
    """Event handler that executes the action method whenever an event is
    processed."""
    
    def __init__(self, action):
        ActivityWithGuard.__init__(self, guard=alwaysTrueGuard, action=action)


class EventHandlerList:
    """List of event handlers used to inject an event into each handler,
    optionally stopping at the first handler that is triggered."""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, stop_at_first_trigger, untriggered_response):
        EventHandlerList.__assertArgIsOfEventHandlerResultType(untriggered_response)
        self.handlers = []
        self.stop_at_first_trigger = stop_at_first_trigger
        self.untriggered_response = untriggered_response

    def process_event(self, event):
        last_result = self.untriggered_response
        for handler in self.handlers:
            result = handler.process_event(event)
            
            if result.handler_triggered:
                last_result = result
            
                if self.stop_at_first_trigger:
                    break
        
        return last_result
    
    def _add_handler(self, handler):
        EventHandlerList.__assertArgIsAnEventHandler(handler)
        self.handlers.append(handler)
    
    @staticmethod
    def __assertArgIsAnEventHandler(arg):
        assert(isinstance(arg, (EventHandlerWithGuardAndEffect)))
    
    @staticmethod
    def __assertArgIsOfEventHandlerResultType(arg):
        assert(isinstance(arg, (EventHandlerResult)))
    
    def __iter__(self):
        for handler in self.handlers:
            yield handler
    
    def __repr__(self):
        return self.handlers.__repr__()


class TransitionList(EventHandlerList):
    """List of transitions used to inject an event into all transitions until
    one is triggered."""
    
    def __init__(self, transitions_arg = []):
        EventHandlerList.__init__(self, stop_at_first_trigger=True,
            untriggered_response = TransitionResult.buildResultForUntriggeredTransition())

        # Indicates if list contains a simple transition. A simple transition
        # is always triggered, hence it will always overrule the
        # other transitions. Note that the trigger process also depends on the
        # position of the transition in the list.
        self.with_unguarded_transition = False

        for transition in transitions_arg:
            self.add_transition(transition)
    
    def containsUnguardedTransition(self):
        return self.with_unguarded_transition

    def add_transition(self, transition):
        self.__assertIsATransition(transition)
        self.__setFlagIfTransitionIsUnguarded(transition)
        EventHandlerList._add_handler(self, handler=transition)
    
    def __setFlagIfTransitionIsUnguarded(self, transition):
        if TransitionList.__transitionHasAlwaysTrueGuard(transition):
            self.with_unguarded_transition = True
    
    @staticmethod
    def __transitionHasAlwaysTrueGuard(transition):
        return transition.guard == alwaysTrueGuard
    
    def __checkIfTransitionIsSimpleAndSetFlagIfSo(self, transition):
        if isinstance(transition, (Transition)):
            self.with_unguarded_transition = True
    
    def __assertIsATransition(self, transition):
        assert(isinstance(transition, (TransitionWithGuardAndEffect)))
    
    

class ActivityList(EventHandlerList):
    """List of activities used to automatically handle an event by
    all activities"""
    
    def __init__(self, activities_arg = []):
        EventHandlerList.__init__(self, stop_at_first_trigger=False,
            untriggered_response = ActivityResult.buildResultForUntriggeredActivity())
        for activity in activities_arg:
            self.add_activity(activity)
    
    def add_activity(self, activity):
        assert(isinstance(activity, (ActivityWithGuard)))
        EventHandlerList._add_handler(self, handler=activity)
    
    

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
    
