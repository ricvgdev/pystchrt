import unittest
import fsm

class TestEventHandler(unittest.TestCase):
    
    def setUp(self):
        pass


class TestEvent:
    pass


class TestState(fsm.State):

    def __init__(self):
        fsm.State.__init__(self, name="")
    

class Test(unittest.TestCase):
    
    def setUp(self):
        self.clr_A()
        self.clr_B()
        self.clr_C()
        self.clr_D()
        self.clr_E()
        self.clr_F()
    
    def set_A(self, event=None):
        self.A = True
    
    def clr_A(self, event=None):
        self.A = False
    
    def is_A_set(self, event=None):
        return self.A
    
    def is_A_clr(self, event=None):
        return not self.A
    
    def set_B(self, event=None):
        self.B = True
    
    def clr_B(self, event=None):
        self.B = False
    
    def is_B_set(self, event=None):
        return self.B
    
    def is_B_clr(self, event=None):
        return not self.B
    
    def set_C(self, event=None):
        self.C = True
    
    def clr_C(self, event=None):
        self.C = False
    
    def is_C_set(self, event=None):
        return self.C
    
    def is_C_clr(self, event=None):
        return not self.C
    
    def set_D(self, event=None):
        self.D = True
    
    def clr_D(self, event=None):
        self.D = False
    
    def is_D_set(self, event=None):
        return self.D
    
    def is_D_clr(self, event=None):
        return not self.D
    
    def set_E(self, event=None):
        self.E = True
    
    def clr_E(self, event=None):
        self.E = False
    
    def is_E_set(self, event=None):
        return self.E
    
    def is_E_clr(self, event=None):
        return not self.E
    
    def set_F(self, event=None):
        self.F = True
    
    def clr_F(self, event=None):
        self.F = False
    
    def is_F_set(self, event=None):
        return self.F
    
    def is_F_clr(self, event=None):
        return not self.F
    
    def test01_TransitionWithGuardAndEffect(self):
        event = TestEvent()
        state = TestState()
        transition = fsm.TransitionWithGuardAndEffect(guard=self.is_A_set,
                                                      target=state,
                                                      effect=self.set_B)
        assert(self.is_A_clr() and self.is_B_clr())

        result = transition.process_event(event)
        assert(not result.handler_triggered)
        assert(result.target == None)
        assert(self.is_A_clr() and self.is_B_clr())
        
        self.set_A()
        assert(self.is_A_set() and self.is_B_clr())

        result = transition.process_event(event)
        assert(result.handler_triggered)
        assert(result.target == state)
        assert(self.is_A_set() and self.is_B_set())

    def test02_TransitionWithEffect(self):
        event = TestEvent()
        state = TestState()
        trans_with_effect = fsm.TransitionWithEffect(target=state, effect=self.set_A)

        assert(self.is_A_clr())

        result = trans_with_effect.process_event(event)
        assert(result.handler_triggered)
        assert(result.target == state)
        assert(self.is_A_set())
    
    def test03_Transition(self):
        event = fsm.Event()
        state = TestState()
        transition = fsm.Transition(state)
        result = transition.process_event(event)
        assert(result.handler_triggered)
        assert(result.target == state)

    def test04_ActivityWithGuard(self):
        event = fsm.Event()
        activity = fsm.ActivityWithGuard(guard=self.is_A_set,
                                         action=self.set_B)
        
        assert(self.is_A_clr())
        assert(self.is_B_clr())

        result = activity.process_event(event)
        assert(not result.handler_triggered)
        assert(self.is_A_clr())
        assert(self.is_B_clr())

        self.set_A()

        assert(self.is_A_set())
        assert(self.is_B_clr())
        
        result = activity.process_event(event)
        assert(result.handler_triggered)
        assert(self.is_A_set())
        assert(self.is_B_set())
    
    def test05_Activity(self):
        event = fsm.Event()
        activity = fsm.Activity(action=self.set_A)
        
        assert(self.is_A_clr())

        result = activity.process_event(event)
        assert(result.handler_triggered)
        assert(self.is_A_set())

    def test06_TransitionList(self):
        event = fsm.Event()
        stateA = TestState()
        stateB = TestState()
        transA = fsm.TransitionWithGuardAndEffect(guard=self.is_A_set,
                                                  target=stateA,
                                                  effect=self.set_C)
        transB = fsm.TransitionWithGuardAndEffect(guard=self.is_B_set,
                                                  target=stateB,
                                                  effect=self.set_D)
        transitions = fsm.TransitionList()
        transitions.add_handler(transA)
        transitions.add_handler(transB)

        assert(self.is_C_clr())
        result = transitions.process_event(event)
        assert(not result.handler_triggered)
        assert(None == result.target)
        assert(self.is_C_clr())
        
        self.set_A()

        assert(self.is_C_clr())
        result = transitions.process_event(event)
        assert(result.handler_triggered)
        assert(stateA == result.target)
        assert(self.is_C_set())

        self.clr_A()
        self.set_B()
        assert(self.is_D_clr())
        result = transitions.process_event(event)
        assert(result.handler_triggered)
        assert(stateB == result.target)
        assert(self.is_D_set())

        # If both guards are true, the first transition should get triggered.
        self.clr_C()
        self.clr_D()
        self.set_A()
        assert(self.is_C_clr())
        assert(self.is_D_clr())
        result = transitions.process_event(event)
        assert(result.handler_triggered)
        assert(stateA == result.target)
        assert(self.is_C_set())
        assert(self.is_D_clr())
    
    
    def test07_ActivityList(self):
        event = fsm.Event()
        setBifAset = fsm.ActivityWithGuard(guard=self.is_A_set, action=self.set_B)
        setDifCset = fsm.ActivityWithGuard(guard=self.is_C_set, action=self.set_D)
        activities = fsm.ActivityList([setBifAset, setDifCset])

        assert(self.is_A_clr() and self.is_B_clr())
        assert(self.is_C_clr() and self.is_D_clr())

        result = activities.process_event(event)
        assert(not result.handler_triggered)
        assert(self.is_A_clr() and self.is_B_clr())
        assert(self.is_C_clr() and self.is_D_clr())
        
        self.set_A()

        assert(self.is_A_set())
        assert(self.is_B_clr() and self.is_C_clr() and self.is_D_clr())
        result = activities.process_event(event)
        assert(result.handler_triggered)
        assert(self.is_A_set() and self.is_B_set())
        assert(self.is_C_clr() and self.is_D_clr())
        
        self.clr_B()
        self.set_C()

        assert(self.is_A_set() and self.is_C_set())
        assert(self.is_B_clr() and self.is_D_clr())
        result = activities.process_event(event)
        assert(result.handler_triggered)
        assert(    self.is_A_set() and self.is_B_set()
               and self.is_C_set() and self.is_D_set())
        
    def test08_ActivitiesDict(self):
        class Event1(fsm.Event): pass
        class Event2(fsm.Event): pass
        class Event3(fsm.Event): pass
        ev0 = fsm.Event()
        ev1 = Event1()
        ev2 = Event2()
        ev3 = Event3()
        setA = fsm.Activity(action=self.set_A)
        setB = fsm.Activity(action=self.set_B)
        setDifCset = fsm.ActivityWithGuard(guard=self.is_C_set, action=self.set_D)
        act_dict = fsm.EventDictOfActivities()
        act_dict.add_handler(ev1, setA)
        act_dict.add_handler(ev2, setB)
        act_dict.add_handler(ev3, setDifCset)

        assert(self.is_A_clr())
        assert(self.is_B_clr())
        assert(self.is_C_clr())
        assert(self.is_D_clr())

        result = act_dict.process_event(ev0)
        assert(not result.handler_triggered)
        assert(self.is_A_clr())
        assert(self.is_B_clr())
        assert(self.is_C_clr())
        assert(self.is_D_clr())

        result = act_dict.process_event(ev1)
        assert(result.handler_triggered)
        assert(self.is_A_set())
        assert(self.is_B_clr())
        assert(self.is_C_clr())
        assert(self.is_D_clr())

        result = act_dict.process_event(ev2)
        assert(result.handler_triggered)
        assert(self.is_A_set())
        assert(self.is_B_set())
        assert(self.is_C_clr())
        assert(self.is_D_clr())

        result = act_dict.process_event(ev3)
        assert(not result.handler_triggered)
        assert(self.is_A_set())
        assert(self.is_B_set())
        assert(self.is_C_clr())
        assert(self.is_D_clr())
        
        self.set_C()

        result = act_dict.process_event(ev3)
        assert(result.handler_triggered)
        assert(self.is_A_set())
        assert(self.is_B_set())
        assert(self.is_C_set())
        assert(self.is_D_set())
    
    def test09_TransitionDict(self):
        stateA = TestState()
        stateB = TestState()
        stateC = TestState()
        stateD = TestState()
        class Event1(fsm.Event): pass
        class Event2(fsm.Event): pass
        class Event3(fsm.Event): pass
        class Event4(fsm.Event): pass
        ev0 = fsm.Event()
        ev1 = Event1()
        ev2 = Event2()
        ev3 = Event3()
        ev4 = Event4()
        to_A = fsm.Transition(stateA)
        to_B_if_B_set = fsm.TransitionWithGuard(guard=self.is_B_set, target=stateB)
        set_C_and_go_to_C = fsm.TransitionWithEffect(target=stateC, effect=self.set_C)
        set_D_and_go_to_D_if_A_set = fsm.TransitionWithGuardAndEffect(
                                            guard=self.is_A_set,
                                            target=stateD,
                                            effect=self.set_D)
        trans_dict = fsm.EventDictOfTransitions()
        trans_dict.add_handler(ev1, to_A)
        trans_dict.add_handler(ev2, to_B_if_B_set)
        trans_dict.add_handler(ev3, set_C_and_go_to_C)
        trans_dict.add_handler(ev4, set_D_and_go_to_D_if_A_set)

        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr())

        result = trans_dict.process_event(ev0)
        assert(not result.handler_triggered)
        assert(None == result.target)

        result = trans_dict.process_event(ev1)
        assert(result.handler_triggered)
        assert(stateA == result.target)

        result = trans_dict.process_event(ev2)
        assert(not result.handler_triggered)
        assert(None == result.target)

        self.set_B()
        result = trans_dict.process_event(ev2)
        assert(result.handler_triggered)
        assert(stateB == result.target)

        assert(self.is_C_clr())
        result = trans_dict.process_event(ev3)
        assert(result.handler_triggered)
        assert(stateC == result.target)
        assert(self.is_C_set())

        result = trans_dict.process_event(ev4)
        assert(not result.handler_triggered)
        assert(None == result.target)

        self.set_A()
        assert(self.is_D_clr())
        result = trans_dict.process_event(ev4)
        assert(result.handler_triggered)
        assert(stateD == result.target)
        assert(self.is_D_set())
    
    def test10_StateEnterAndExit(self):
        state = TestState()

        assert(not state.is_active())

        result = state.enter()
        assert(state.is_active())
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        
        result = state.exit()
        assert(not state.is_active())
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)


    def test11_StateUnnamedTransition(self):
        stateA = TestState()
        stateB = TestState()
        
        to_B = fsm.Transition(stateB)

        stateA.add_unnamed_transition(to_B)

        assert(not stateA.is_active())
        result = stateA.enter()
        assert(stateA.is_active())
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)

    def test12_StateEnterActivities(self):
        set_A = fsm.Activity(self.set_A)
        set_B_if_C_set = fsm.ActivityWithGuard(guard=self.is_C_set,
                                               action=self.set_B)

        state = TestState()
        
        state.add_enter_activity(set_A)
        state.add_enter_activity(set_B_if_C_set)
        
        result = state.enter()
        assert(state.is_active())
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set())
        assert(self.is_B_clr() and self.is_C_clr())
        
        self.clr_A()
        self.set_C()

        assert(self.is_C_set())
        assert(self.is_A_clr() and self.is_B_clr())
        result = state.enter()
        assert(state.is_active())
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set() and self.is_B_set() and self.is_C_set())

        
    def test13_StateExitActivities(self):
        set_A = fsm.Activity(self.set_A)
        set_B_if_C_set = fsm.ActivityWithGuard(guard=self.is_C_set,
                                               action=self.set_B)

        state = TestState()
        
        state.add_exit_activity(set_A)
        state.add_exit_activity(set_B_if_C_set)
        
        result = state.exit()
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set())
        assert(self.is_B_clr() and self.is_C_clr())
        
        self.clr_A()
        self.set_C()

        assert(self.is_C_set())
        assert(self.is_A_clr() and self.is_B_clr())
        result = state.exit()
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set() and self.is_B_set() and self.is_C_set())

        
    def test14_StateActivities(self):
        event = fsm.Event()
        
        set_A = fsm.Activity(self.set_A)
        set_B_if_C_set = fsm.ActivityWithGuard(guard=self.is_C_set,
                                               action=self.set_B)
        state = TestState()
        state.add_activity(event, set_A)
        state.add_activity(event, set_B_if_C_set)
        
        assert(self.is_A_clr() and self.is_B_clr() and self.is_C_clr())
        
        result = state.process_event(event)
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set())
        assert(self.is_B_clr() and self.is_C_clr())
        
        self.clr_A()
        self.set_C()
        assert(self.is_A_clr() and self.is_B_clr() and self.is_C_set())
        
        result = state.process_event(event)
        assert(result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_set() and self.is_B_set() and self.is_C_set())


    def test15_StateTransitions(self):
        state = TestState()
        stateA = TestState()
        stateB = TestState()
        stateC = TestState()
        stateD = TestState()
        class Event1(fsm.Event): pass
        class Event2(fsm.Event): pass
        class Event3(fsm.Event): pass
        class Event4(fsm.Event): pass
        ev0 = fsm.Event()
        ev1 = Event1()
        ev2 = Event2()
        ev3 = Event3()
        ev4 = Event4()
        to_A = fsm.Transition(stateA)
        to_B_if_B_set = fsm.TransitionWithGuard(guard=self.is_B_set, target=stateB)
        set_C_and_go_to_C = fsm.TransitionWithEffect(target=stateC, effect=self.set_C)
        set_D_and_go_to_D_if_A_set = fsm.TransitionWithGuardAndEffect(
                                            guard=self.is_A_set,
                                            target=stateD,
                                            effect=self.set_D)
    
        state.add_transition(ev1, to_A)
        state.add_transition(ev2, to_B_if_B_set)
        state.add_transition(ev3, set_C_and_go_to_C)
        state.add_transition(ev4, set_D_and_go_to_D_if_A_set)

        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr())

        result = state.process_event(ev0)
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr())

        result = state.process_event(ev1)
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateA == result.transition.target)
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr())

        result = state.process_event(ev2)
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr())

        self.set_B()
        result = state.process_event(ev2)
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateB == result.transition.target)
        assert(self.is_A_clr() and self.is_C_clr() and self.is_D_clr())
        assert(self.is_B_set())

        result = state.process_event(ev3)
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateC == result.transition.target)
        assert(self.is_A_clr() and self.is_D_clr())
        assert(self.is_B_set() and self.is_C_set())

        result = state.process_event(ev4)
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        assert(self.is_A_clr() and self.is_D_clr())
        assert(self.is_B_set() and self.is_C_set())

        self.set_A()
        result = state.process_event(ev4)
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateD == result.transition.target)
        assert(    self.is_A_set() and self.is_B_set()
               and self.is_D_set() and self.is_C_set())

    
    def test16_StateUnnamedTransition(self):
        stateA = TestState()
        self_trans = fsm.Transition(target=stateA)
        stateA.add_unnamed_transition(self_trans)
        
        assert(not stateA.is_active())
        result = stateA.enter()
        assert(stateA.is_active())
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)

        result = stateA.process_event(fsm.State.UnnamedEvent)
        assert(stateA.is_active())
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateA == result.transition.target)

        stateB = TestState()
        self_trans_if_A_set = fsm.TransitionWithGuard(guard=self.is_A_set,
                                                      target=stateB)
        stateB.add_unnamed_transition(self_trans_if_A_set)
        
        assert(not stateB.is_active())
        result = stateB.enter()
        assert(stateB.is_active())
        assert(not result.activity.handler_triggered)
        assert(not result.transition.handler_triggered)
        assert(None == result.transition.target)
        
        self.set_A()
        assert(stateB.is_active())
        result = stateB.process_event(fsm.State.UnnamedEvent)
        assert(stateB.is_active())
        assert(not result.activity.handler_triggered)
        assert(result.transition.handler_triggered)
        assert(stateB == result.transition.target)

    def test17_FsmCtorXtor(self):
        set_A = fsm.Activity(self.set_A)
        set_B_if_C_set = fsm.ActivityWithGuard(guard=self.is_C_set, action=self.set_B)
        set_D = fsm.Activity(self.set_D)
        set_E_if_F_set = fsm.ActivityWithGuard(guard=self.is_F_set, action=self.set_E)
        
        sm = fsm.FSM()
        
        sm.add_start_activity(set_A)
        sm.add_start_activity(set_B_if_C_set)
        sm.add_stop_activity(set_D)
        sm.add_stop_activity(set_E_if_F_set)
        
        # Current state should be set to final after start() since the FSM does
        # not have any internal state.
        assert(    self.is_A_clr() and self.is_B_clr() and self.is_C_clr()
               and self.is_D_clr() and self.is_E_clr() and self.is_F_clr())
        result = sm.start()
        assert(not result.event_res.activity.handler_triggered)
        assert(not result.event_res.transition.handler_triggered)
        assert(None == result.event_res.transition.target)
        assert(sm.current == sm.final)
        assert(self.is_A_set() and self.is_B_clr() and self.is_C_clr())
        assert(self.is_D_set() and self.is_E_clr() and self.is_F_clr())
        
        result = sm.stop()
        #assert(not result.event_res.activity.handler_triggered)
        #assert(not result.event_res.transition.handler_triggered)
        #assert(None == result.event_res.transition.target)
        assert(sm.current == sm.final)
        assert(self.is_A_set() and self.is_B_clr() and self.is_C_clr())
        assert(self.is_D_set() and self.is_E_clr() and self.is_F_clr())

    def test18_FsmInit(self):
        set_A = fsm.Activity(self.set_A)
        set_B = fsm.Activity(self.set_B)
        set_E = fsm.Activity(self.set_E)
        set_F = fsm.Activity(self.set_F)
        
        state = TestState()
        sm = fsm.FSM([state])
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)
        state.add_enter_activity(set_E)
        state.add_exit_activity(set_F)
        
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_E_clr() and self.is_F_clr())
        #activity, transition, target = sm.start()
        result = sm.start()
        #assert(not activity)
        #assert(not transition)
        #assert(None == target)
        assert(sm.current == state)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_E_set() and self.is_F_clr())

        #activity, transition, target = sm.stop()
        result = sm.stop()
        #assert(not activity)
        #assert(not transition)
        #assert(None == target)
        assert(sm.current == sm.final)
        assert(self.is_A_set() and self.is_B_set())
        assert(self.is_E_set() and self.is_F_set())


    def test19_FsmTransition(self):
        set_A = fsm.Activity(self.set_A)
        set_B = fsm.Activity(self.set_B)
        set_C = fsm.Activity(self.set_C)
        set_D = fsm.Activity(self.set_D)
        set_E = fsm.Activity(self.set_E)
        set_F = fsm.Activity(self.set_F)
        
        event = fsm.Event()
        
        state1 = TestState()
        state2 = TestState()

        to_2 = fsm.Transition(state2)
        state1.add_transition(event, to_2)

        sm = fsm.FSM([state1, state2])
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)

        state1.add_enter_activity(set_C)
        state1.add_exit_activity(set_D)

        state2.add_enter_activity(set_E)
        state2.add_exit_activity(set_F)
        
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr()
               and self.is_E_clr() and self.is_F_clr())
        result = sm.start()
        #activity, transition, target = sm.start()
        #assert(not activity)
        #assert(not transition)
        #assert(None == target)
        assert(sm.current == state1)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_C_set() and self.is_D_clr())
        assert(self.is_E_clr() and self.is_F_clr())

        result = sm.process_event(event)
        #activity, transition, target = sm.process_event(event)
        #assert(not activity)
        #assert(not transition)
        #assert(None == target)
        assert(sm.current == state2)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_C_set() and self.is_D_set())
        assert(self.is_E_set() and self.is_F_clr())

        result = sm.stop()
        #activity, transition, target = sm.stop()
        #assert(not activity)
        #assert(not transition)
        #assert(None == target)
        assert(sm.current == sm.final)
        assert(self.is_A_set() and self.is_B_set())
        assert(self.is_C_set() and self.is_D_set())
        assert(self.is_E_set() and self.is_F_set())



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()