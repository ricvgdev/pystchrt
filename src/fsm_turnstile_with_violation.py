import fsm
from abc import ABCMeta, abstractmethod

class SimpleTurnstile(object):

    class FSM(fsm.FSM):
        '''
        Implementation of the FSM shown in [1]'s figure 3.

        [1] UML Tutorial: Finite State Machines
            http://www.objectmentor.com/resources/articles/umlfsm.pdf

                     Pass        Pass                 Coin/
                      ---     -- /alarm -----      -- unlock- -
                     |   |   |               |    |            |
        Reset/       |   V   V               |    |            V       Coin/
        resetAlarm  -----------             --------     -----------   thankyou
           ------->|           |           |        |   |           |------
          |        | Violation |           | Locked |   | Unlocked  |      |
           --------|           |           |        |   |           |<-----
                    -----------             --------     -----------
                     ^   |   |               ^    ^           |
                     |   |   |               |    |           |
                      ---     -- Ready/ -----      -- Pass/ --
                     Coin    (resetAlarm,lock)        lock
        '''
        
        def __init__(self):
            locked = SimpleTurnstile.FSM.LockedState()
            unlocked = SimpleTurnstile.FSM.UnlockedState()
            violation = SimpleTurnstile.FSM.ViolationState()
            
            trans_to_unlocked = SimpleTurnstile.FSM.TransitionAndAction(target=unlocked,
                                            action=self.unlock)
            trans_to_locked_and_lock = SimpleTurnstile.FSM.TransitionAndAction(target=locked,
                                            action=self.lock)
            trans_to_unlocked_with_thankyou = SimpleTurnstile.FSM.TransitionAndAction(
                                            target=unlocked,
                                            action=self.thankyou)
            trans_to_violation_with_alarm = SimpleTurnstile.FSM.TransitionAndAction(
                                                        target=violation,
                                                        action=self.alarm)
            
            locked.add_transition(SimpleTurnstile.FSM.EventCoin, trans_to_unlocked)
            locked.add_transition(SimpleTurnstile.FSM.EventPass, trans_to_violation_with_alarm)
            unlocked.add_transition(SimpleTurnstile.FSM.EventPass, trans_to_locked_and_lock)
            unlocked.add_transition(SimpleTurnstile.FSM.EventCoin, trans_to_unlocked_with_thankyou)

            trans_to_violation = SimpleTurnstile.FSM.Transition(target=violation)
            trans_to_violation_and_resetAlarm = SimpleTurnstile.FSM.TransitionAndAction(
                        target=violation, action = self.resetAlarm)
            trans_to_locked_and_resetAlarmAndLock = SimpleTurnstile.FSM.TransitionAndAction(
                        target=locked, action = self.resetAlarmAndLock)
            
            violation.add_transition(SimpleTurnstile.FSM.EventCoin, trans_to_violation)
            violation.add_transition(SimpleTurnstile.FSM.EventPass, trans_to_violation)
            violation.add_transition(SimpleTurnstile.FSM.EventReset, trans_to_violation_and_resetAlarm)
            violation.add_transition(SimpleTurnstile.FSM.EventReady, trans_to_locked_and_resetAlarmAndLock)

            fsm.FSM.__init__(self, states = [locked, unlocked])
            self.set_initial_state(locked)
            self.start()

        def unlock(self, event):
            pass
        
        def lock(self, event):
            pass
        
        def thankyou(self, event):
            print "Thank you!"
        
        def alarm(self, event):
            print "ALARM!"
        
        def resetAlarm(self, event):
            print "Alarm reseted"
        
        def resetAlarmAndLock(self, event):
            self.resetAlarm(event)
            self.lock(event)

        class TurnstileEvent(fsm.Event):
            '''
            Basic and abstract event used for SimpleTurnstile. It is
            recommended to define a general event, preferably as abstract,
            in order to implement general event functionality.
            '''
            __metaclass__ = ABCMeta
            @abstractmethod
            def __init__(self):
                fsm.Event.__init__(self)
        
        class EventCoin(TurnstileEvent):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileEvent.__init__(self)
        
        class EventPass(TurnstileEvent):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileEvent.__init__(self)
        
        class EventReset(TurnstileEvent):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileEvent.__init__(self)
        
        class EventReady(TurnstileEvent):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileEvent.__init__(self)
        
        class TransitionAndAction(fsm.TransitionWithAction):
            def __init__(self, target, action):
                fsm.TransitionWithAction.__init__(self, target=target, action=action)
        
        class Transition(fsm.Transition):
            def __init__(self, target):
                fsm.Transition.__init__(self, target=target)
        
        class TurnstileState(fsm.State):
            __metaclass__ = ABCMeta
            @abstractmethod
            def __init__(self):
                fsm.State.__init__(self)
            
            def enter(self):
                print 'Turnstile is now ', self
        
        class LockedState(TurnstileState):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileState.__init__(self)

        class UnlockedState(TurnstileState):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileState.__init__(self)
        
        class ViolationState(TurnstileState):
            def __init__(self):
                SimpleTurnstile.FSM.TurnstileState.__init__(self)
        

    def __init__(self):
        '''
        Constructor
        '''
        self.fsm = SimpleTurnstile.FSM()
    
    def work_until_q_key(self):
        key = None
        while key != 'q':
            key = self.__get_key()
            if key == 'c':
                self.dispatch_coin_event()
            elif key == 'p':
                self.dispatch_pass_event()
            elif key == 'r':
                self.dispatch_reset_event()
            elif key == 'a':
                self.dispatch_ready_event()
            
    def __get_key(self):
        return raw_input('> ')
    
    def dispatch_coin_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventCoin())
    
    def dispatch_pass_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventPass())
    
    def dispatch_reset_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventReset())
    
    def dispatch_ready_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventReady())
    
    def __dispatch_event(self, event):
        print 'Dispatching event: ', event
        self.fsm.process_event(event)


def main():
    turnstile = SimpleTurnstile()
    turnstile.work_until_q_key()

if __name__=='__main__':
    main()
