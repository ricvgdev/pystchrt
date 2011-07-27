import fsm
from abc import ABCMeta, abstractmethod

class SimpleTurnstile(object):

    class FSM(fsm.FSM):
        '''
        Implementation of the FSM shown in [1]'s figure 2.

        [1] UML Tutorial: Finite State Machines
            http://www.objectmentor.com/resources/articles/umlfsm.pdf

                        --- Coin / unlock ---
                       |                     |
                       |                     V
        Pass / Alarm  --------              ----------
               ------|        |            |          |------
              |      | Locked |            | Unlocked |      | Coin / Thankyou
               ----->|        |            |          |<-----
                      --------              ----------
                         ^                     |
                         |                     |
                          ---- Pass / lock ----
        '''
        
        def __init__(self):
            locked = SimpleTurnstile.FSM.LockedState()
            unlocked = SimpleTurnstile.FSM.UnlockedState()
            
            trans_to_unlocked = SimpleTurnstile.FSM.Transition(target=unlocked,
                                            action=self.unlock)
            trans_to_locked = SimpleTurnstile.FSM.Transition(target=locked,
                                            action=self.lock)
            trans_to_unlocked_with_thankyou = SimpleTurnstile.FSM.Transition(
                                            target=unlocked,
                                            action=self.thankyou)
            trans_to_locked_with_alarm = SimpleTurnstile.FSM.Transition(
                                                        target=locked,
                                                        action=self.alarm)
            
            locked.add_transition(SimpleTurnstile.FSM.EventCoin, trans_to_unlocked)
            locked.add_transition(SimpleTurnstile.FSM.EventPass, trans_to_locked_with_alarm)
            unlocked.add_transition(SimpleTurnstile.FSM.EventPass, trans_to_locked)
            unlocked.add_transition(SimpleTurnstile.FSM.EventCoin, trans_to_unlocked_with_thankyou)

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
        
        class Transition(fsm.TransitionWithAction):
            def __init__(self, target, action):
                fsm.TransitionWithAction.__init__(self, target=target, effect=action)
        
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
            
    def __get_key(self):
        return raw_input('> ')
    
    def dispatch_coin_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventCoin())
    
    def dispatch_pass_event(self):
        self.__dispatch_event(SimpleTurnstile.FSM.EventPass())
    
    def __dispatch_event(self, event):
        print 'Dispatching event: ', event
        self.fsm.process_event(event)


def main():
    turnstile = SimpleTurnstile()
    turnstile.work_until_q_key()

if __name__=='__main__':
    main()
