import unittest
import hsm

class HSMTester(unittest.TestCase):
    
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
    
    def set_G(self, event=None):
        self.G = True
    
    def clr_G(self, event=None):
        self.G = False
    
    def is_G_set(self, event=None):
        return self.G
    
    def is_G_clr(self, event=None):
        return not self.G
    
    def set_H(self, event=None):
        self.H = True
    
    def clr_H(self, event=None):
        self.H = False
    
    def is_H_set(self, event=None):
        return self.H
    
    def is_H_clr(self, event=None):
        return not self.H
    
    def incr_cntr(self, event=None):
        self.cntr += 1
    
    def decr_cntr(self, event=None):
        self.cntr -= 1
    
    def is_cntr_eq_zero(self, event=None):
        return self.cntr == 0

    def is_cntr_gt_zero(self, event=None):
        return self.cntr > 0

    def setUp(self):
        self.clr_A()
        self.clr_B()
        self.clr_C()
        self.clr_D()
        self.clr_E()
        self.clr_F()
        self.clr_G()
        self.clr_H()
        self.cntr = 0

    def tearDown(self):
        pass
    
    class TestTransition(hsm.Transition):
        def __init__(self, target):
            hsm.Transition.__init__(self, target)
    
    class TestEvent(hsm.Event):
        def __init__(self):
            hsm.Event.__init__(self)
    
    class TestEvent2(hsm.Event):
        def __init__(self):
            hsm.Event.__init__(self)
    
    class TestSimpleState(hsm.SimpleState):
        def __init__(self):
            hsm.SimpleState.__init__(self)
    
    class TestCompositeState(hsm.CompositeState):
        def __init__(self, states=[]):
            hsm.CompositeState.__init__(self, states)
    
    class TestActivity(hsm.Activity):
        def __init__(self, action):
            hsm.Activity.__init__(self, action)
    
    def test02_SimpleState(self):
        event = HSMTester.TestEvent()
        state = HSMTester.TestSimpleState()
        response = state.process_event(event)
        assert(not response.did_act_or_requested_transition())
        
        set_A = HSMTester.TestActivity(self.set_A)
        state.add_activity(event, set_A)
        response = state.process_event(event)
        assert(response.did_act())
        assert(not response.was_transition_requested())
        assert(response.did_act_or_requested_transition())
        
        event2 = HSMTester.TestEvent2()
        stateB = HSMTester.TestSimpleState()
        to_B = HSMTester.TestTransition(stateB)
        state.add_transition(event2, to_B)
        response = state.process_event(event2)
        assert(not response.did_act())
        assert(response.was_transition_requested())
        assert(response.did_act_or_requested_transition())
    
    def test03_CompositeState(self):
        simple_state = HSMTester.TestSimpleState()
        composite_state = HSMTester.TestCompositeState([simple_state])
        assert(composite_state.current == composite_state.initial)
        
        set_A = hsm.Activity(self.set_A)
        set_B = hsm.Activity(self.set_B)
        set_C = hsm.Activity(self.set_C)
        set_D = hsm.Activity(self.set_D)
        set_E = hsm.Activity(self.set_E)
        set_F = hsm.Activity(self.set_F)
        
        composite_state.add_enter_activity(set_A)
        composite_state.add_start_activity(set_B)
        simple_state.add_enter_activity(set_C)
        simple_state.add_exit_activity(set_D)
        composite_state.add_stop_activity(set_E)
        composite_state.add_exit_activity(set_F)
        
        assert(self.is_A_clr() and self.is_F_clr())
        assert(self.is_B_clr() and self.is_E_clr())
        assert(self.is_C_clr() and self.is_D_clr())

        # Enter composite, don't start nor transition to simple_state
        response = composite_state.enter()
        assert(composite_state.current == composite_state.initial)
        assert(response.did_act())
        assert(not response.was_transition_requested())
        assert(response.did_act_or_requested_transition())
        assert(self.is_A_set() and self.is_F_clr())
        assert(self.is_B_clr() and self.is_E_clr())
        assert(self.is_C_clr() and self.is_D_clr())

        # Start composite and trigger transition to simple_state
        response = composite_state.start()
        assert(composite_state.current == simple_state)
        assert(not response.event_res.did_act())
        assert(not response.event_res.was_transition_requested())
        assert(not response.event_res.did_act_or_requested_transition())
        assert(self.is_A_set() and self.is_F_clr())
        assert(self.is_B_set() and self.is_E_clr())
        assert(self.is_C_set() and self.is_D_clr())

        # Stop composite which triggers transition to final state
        response = composite_state.stop()
        assert(composite_state.current == composite_state.final)
        assert(not response.event_res.did_act())
        assert(not response.event_res.was_transition_requested())
        assert(not response.event_res.did_act_or_requested_transition())
        assert(self.is_A_set() and self.is_F_clr())
        assert(self.is_B_set() and self.is_E_set())
        assert(self.is_C_set() and self.is_D_set())

        # Trigger composite_state's exit actions.
        response = composite_state.exit()
        assert(composite_state.current == composite_state.final)
        assert(response.did_act())
        assert(not response.was_transition_requested())
        assert(response.did_act_or_requested_transition())
        assert(self.is_A_set() and self.is_F_set())
        assert(self.is_B_set() and self.is_E_set())
        assert(self.is_C_set() and self.is_D_set())

    def test04_HsmCtorXtor(self):
        set_A = hsm.Activity(self.set_A)
        set_B = hsm.Activity(self.set_B)
        
        sm = hsm.HSM()
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)
        
        assert(self.is_A_clr() and self.is_B_clr())

        response = sm.start()
        assert(not response.event_res.did_act())
        assert(not response.event_res.was_transition_requested())
        assert(None == response.event_res.transition.target)
        assert(self.is_A_set() and self.is_B_set())

        response = sm.stop()
        assert(self.is_A_set() and self.is_B_set())
        assert(not response.event_res.did_act())
        assert(not response.event_res.was_transition_requested())
        assert(None == response.event_res.transition.target)
        assert(self.is_A_set() and self.is_B_set())
        
    
    def _test02_FsmInitWithSingleChild(self):
        set_A = hsm.Activity(self.set_A)
        set_B = hsm.Activity(self.set_B)
        set_E = hsm.Activity(self.set_E)
        set_F = hsm.Activity(self.set_F)
        
        state = hsm.SimpleState()
        sm = hsm.HSM([state])
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)
        state.add_enter_activity(set_E)
        state.add_exit_activity(set_F)
        
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_E_clr() and self.is_F_clr())
        activity, transition, target = sm.start()
        assert(activity)
        assert(transition)
        assert(state == target)
        assert(sm.current == state)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_E_set() and self.is_F_clr())

        activity, transition, target = sm.stop()
        assert(activity)
        assert(transition)
        assert(sm.final == target)
        assert(sm.current == sm.final)
        assert(    self.is_A_set() and self.is_B_set()
               and self.is_E_set() and self.is_F_set())

    def _test03_HsmInitWithCompositeChild(self):
        set_A = hsm.Activity(self.set_A)
        set_B = hsm.Activity(self.set_B)
        set_C = hsm.Activity(self.set_C)
        set_D = hsm.Activity(self.set_D)
        set_E = hsm.Activity(self.set_E)
        set_F = hsm.Activity(self.set_F)
        
        state2 = hsm.SimpleState()
        state1 = hsm.CompositeState([state2])
        sm = hsm.HSM([state1])
        
        sm.set_initial_state(state2)
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)
        state1.add_enter_activity(set_C)
        state1.add_exit_activity(set_D)
        state2.add_enter_activity(set_E)
        state2.add_exit_activity(set_F)
        
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr()
               and self.is_E_clr() and self.is_F_clr())
        activity, transition, target = sm.start()
        assert(activity)
        assert(transition)
        assert(state2 == target)
        assert(sm.current == state2)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_C_set() and self.is_D_clr())
        assert(self.is_E_set() and self.is_F_clr())

        activity, transition, target = sm.stop()
        assert(activity)
        assert(transition)
        assert(sm.final == target)
        assert(sm.current == sm.final)
        assert(    self.is_A_set() and self.is_B_set()
               and self.is_C_set() and self.is_D_set()
               and self.is_E_set() and self.is_F_set())


    def _test04_HsmTransitionOneLevelUp(self):
        set_A = hsm.Activity(self.set_A)
        set_B = hsm.Activity(self.set_B)
        set_C = hsm.Activity(self.set_C)
        set_D = hsm.Activity(self.set_D)
        set_E = hsm.Activity(self.set_E)
        set_F = hsm.Activity(self.set_F)
        set_G = hsm.Activity(self.set_G)
        set_H = hsm.Activity(self.set_H)
        
        state1 = hsm.SimpleState()
        state2a = hsm.SimpleState()
        state2 = hsm.CompositeState([state2a])
        sm = hsm.HSM([state1, state2])

        to_2a = hsm.Transition(state2a)
        
        event = hsm.Event()
        
        state1.add_handler(event, to_2a)
        
        sm.set_initial_state(state1)
        
        sm.add_start_activity(set_A)
        sm.add_stop_activity(set_B)
        state1.add_enter_activity(set_C)
        state1.add_exit_activity(set_D)
        state2.add_enter_activity(set_E)
        state2.add_exit_activity(set_F)
        state2a.add_enter_activity(set_G)
        state2a.add_exit_activity(set_H)
        
        assert(    self.is_A_clr() and self.is_B_clr()
               and self.is_C_clr() and self.is_D_clr()
               and self.is_E_clr() and self.is_F_clr()
               and self.is_G_clr() and self.is_H_clr())
        activity, transition, target = sm.start()
        assert(activity)
        assert(transition)
        assert(state1 == target)
        assert(sm.current == state1)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_C_set() and self.is_D_clr())
        assert(self.is_E_clr() and self.is_F_clr())
        assert(self.is_G_clr() and self.is_H_clr())

        activity, transition, target = sm.process_event(event)
        assert(activity)
        assert(transition)
        assert(state2a == target)
        assert(sm.current == state2a)
        assert(self.is_A_set() and self.is_B_clr())
        assert(self.is_C_set() and self.is_D_set())
        assert(self.is_E_set() and self.is_F_clr())
        assert(self.is_G_set() and self.is_H_clr())

        activity, transition, target = sm.stop()
        assert(activity)
        assert(transition)
        assert(sm.final == target)
        assert(sm.current == sm.final)
        assert(    self.is_A_set() and self.is_B_set()
               and self.is_C_set() and self.is_D_set()
               and self.is_E_set() and self.is_F_set()
               and self.is_G_set() and self.is_H_set())

    @staticmethod
    def exec_state_enter_and_assert_activity(state): 
        assert(not state.is_active())
        state.enter()
        assert(state.is_active())

    @staticmethod
    def exec_state_exit_and_assert_activity(state): 
        assert(state.is_active())
        state.exit()
        assert(not state.is_active())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()