'''
Hierarchical State Machine
'''
import fsm

class Event(fsm.Event):
    pass

class TransitionWithGuardAndEffect(fsm.TransitionWithGuardAndEffect):
    pass

class TransitionWithGuard(fsm.TransitionWithGuard):
    pass

class TransitionWithEffect(fsm.TransitionWithEffect):
    pass

class Transition(fsm.Transition):
    pass

class ActivityWithGuard(fsm.ActivityWithGuard):
    pass

class Activity(fsm.Activity):
    pass


class OldTransition(fsm.Transition):

    def react(self, event):
        # Do pre-action test. If True, continue with transition.
        # Else, let the upstream logic figure out appropriate response.
        if not self.pre_trans_action_test(event):
            return None

        if self.action != None:
            # Do action if available.
            self.action(event)
        
        source_stack = self.__get_parent_stack(self.source)
        source_set = set(source_stack)
        target_stack = self.__get_parent_stack(self.target)
        target_set = set(target_stack)
        common_set = target_set & source_set
        exit_set = source_set - common_set
        enter_set = target_set - common_set
        
        exit_stack = [st for st in source_stack if st in exit_set ]
        enter_stack = [st for st in target_stack if st in enter_set ]

        for st in exit_stack:
            st.exit(follow_final_trans = False)
        
        last_state = self.target
        for i, st in enumerate(enter_stack):
            do_unnamed = False
            do_init = False
            if len(enter_stack) == i + 1:
                do_unnamed = True
                do_init = True
            last_state = st.enter(follow_unnamed_trans = do_unnamed, follow_init_trans = do_init)
        
        # Transition completed. Return new state.
        return last_state
    
    def __get_parent_stack(self, state):
        st = state
        stack = []
        while True:
            stack.append(st)
            st = st.parent
            if st == None:
                break
        stack.reverse()
        return stack

class StimulusResponse(fsm.StimulusResponse):
    pass

class StimulusResponseDict(dict):
    
    def __init__(self, init_dict):
        dict.__init__(self)
        # Trigger own __setitem__
        for key in init_dict:
            self[key] = init_dict[key]
    
    def __setitem__(self, key, value):
        assert(isinstance(key, (SimpleState)))
        assert(isinstance(value, (fsm.StimulusResponse)))
        dict.__setitem__(self, key, value)
    
    def add_response_dict(self, res_dict):
        assert(isinstance(res_dict, (StimulusResponseDict)))
        self.update(res_dict)
    
    def did_act_or_requested_transition(self):
        return self.did_act() or self.was_transition_requested()
    
    def did_act(self):
        for key in self:
            if self[key].did_act():
                return True
        return False
    
    def was_transition_requested(self):
        for key in self:
            if self[key].was_transition_requested():
                return True
        return False


class SimpleState(fsm.State):

    def __init__(self, name = ''):
        fsm.State.__init__(self, name = name)
        self.parent = None
    
    def stimulate(self, event):
        single_response = fsm.State.stimulate(self, event)
        if not single_response.did_act_or_requested_transition() and self.has_parent():
            return self.parent.stimulate(event)
        else:
            return single_response
    
    def start(self):
        return StimulusResponse(False, False, None)
    
    def stop(self):
        return StimulusResponse(False, False, None)
    
    def has_parent(self):
        return None != self.parent

    def get_parent_stack(self):
        stack = []
        state = self
        while True:
            stack.append(state)
            
            if not state.has_parent():
                break

            state = state.parent
        stack.reverse()
        return stack

    def is_parent(self, other):
        if self.parent == None:
            return False
    
        if self.parent == other:
            return True
        else:
            return self.parent.is_parent(other)

    def __contains__(self, child):
        return False


class CompositeState(fsm.FSM, SimpleState):
    
    class InitialState(SimpleState, fsm.FSM.InitialState):
        pass

    class FinalState(SimpleState, fsm.FSM.FinalState):
        pass 
    
    def __init__(self, states = [], name = ''):
        SimpleState.__init__(self, name = name)
        fsm.FSM.__init__(self, states, initial = CompositeState.InitialState(),
                         final = CompositeState.FinalState())
    
    def start(self):
        return fsm.FSM.start(self)
    
    def stop(self):
        return fsm.FSM.stop(self)
    
    def __contains__(self, other):
        return fsm.FSM.__contains__(self, other)


class HSM(object):
    
    class TopState(CompositeState):
        pass
    
    def __init__(self, states = []):
        object.__init__(self)
        self.top = HSM.TopState()
    
    def start(self):
        self.current = self.top.initial
        return self.dispatch(SimpleState.EnterEvent)
    
    def stop(self):
        self.top.final.add_final_transition_to_other(other=self.current)
        return self.dispatch(SimpleState.ExitEvent)
    
    def add_start_activity(self, activity):
        self.top.add_start_activity(activity)
    
    def add_stop_activity(self, activity):
        self.top.add_stop_activity(activity)
    
    def add_on_transition_completed_activity(self, activity):
        self.top.add_on_transition_completed_activity(activity)
    
    def dispatch(self, event):
        while True:
            response = self._dipatch_to_current(event)
            
            if event == SimpleState.EnterEvent:
                event = SimpleState.UnnamedEvent
            elif not response.was_transition_requested():
                break
        return response

    def _dipatch_to_current(self, event):
        
        response = self.current.stimulate(event)
        
        if not response.was_transition_requested():
            return response

        source_stack = self.current.get_parent_stack()
        source_set = set(source_stack)
        target_stack = response.get_target().get_parent_stack()
        target_set = set(target_stack)
        common_set = target_set & source_set
        exit_set = source_set - common_set
        enter_set = target_set - common_set
        exit_stack = [st for st in source_stack if st in exit_set ]
        exit_stack.reverse()
        enter_stack = [st for st in target_stack if st in enter_set ]

        for st in exit_stack:
            exit_response = st.exit()
                
            if exit_response.did_act():
                activity = True
        
        for st in enter_stack:
            enter_response = st.enter()

            if enter_response.did_act():
                activity = True
        
        self.current = enter_stack[-1]
        self.top.state_change_activities.stimulate(Event)
        
        start_response = self.current.start()
        return StimulusResponse(activity or start_response.did_act(), True, self.current)

    def fsm_dipatch_to_current(self, event):
        '''_dipatch_to_state(state, event) -> active_state, did_transition'''

        if self.current == self.initial and fsm.State.EnterEvent == fsm.get_object_class(event) \
           and self.no_initial_transition:
            return False, False, None
            
        if fsm.State.ExitEvent == fsm.get_object_class(event) and self.no_final_transition:
            return False, False, None

        activity, transition, target = self.current.stimulate(event)
        
        if transition and None != target:
            self.current.exit()
            self.current = target
            self.current.enter()
            self.state_change_activities.stimulate(Event)
        
        return activity, transition, target
