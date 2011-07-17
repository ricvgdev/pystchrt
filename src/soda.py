'''
A simple program that implements an FSM. Designed after a state machine
description somewhere in the Web.
'''

import fsm
import curses, traceback


class UI(object):
    
    def __init__(self, use_ncurses = False):
        self.use_ncurses = use_ncurses
        if use_ncurses:
            self.init_ncurses()
    
    def get_key(self):
        if self.use_ncurses:
            return self.screen.getkey()
        else:
            return raw_input('> ')
    
    def shutdown(self):
        if self.use_ncurses:
            self.shutdown_ncurses()

    def init_ncurses(self):
        try:
            # Initialize curses
            self.screen=curses.initscr()
            # Turn off echoing of keys, and enter cbreak mode,
            # where no buffering is performed on keyboard input
            curses.noecho()
            curses.cbreak()

            # In keypad mode, escape sequences for special keys
            # (like the cursor keys) will be interpreted and
            # a special value like curses.KEY_LEFT will be returned
            self.screen.keypad(1)
        except:
            self.shutdown_ncurses()
            traceback.print_exc()           # Print the exception
    
    def shutdown_ncurses(self):
        assert(self.use_ncurses)
        # Set everything back to normal
        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()                 # Terminate curses
    
    def set_screen_ready(self):
        if self.use_ncurses:
            self.ncurses_set_screen_ready()
        else:
            self.stdout_set_screen_ready()
    
    def ncurses_set_screen_ready(self):
        assert(self.use_ncurses)
        self.screen.border(0)
        self.screen.addstr(6,1,  'Keys:')
        self.screen.addstr(7,1,  '  1:  Deposit 10 cents')
        self.screen.addstr(8,1,  '  2:  Deposit 25 cents')
        self.screen.addstr(9,1,  '  5:  Deposit 50 cents')
        self.screen.addstr(10,1, '  l:  Deposit 1 dollar')
        self.screen.addstr(11,1, '  t:  Deposit 2 dollars')
        self.screen.addstr(12,1, '  s:  Select drink')
        self.screen.addstr(13,1, '  r:  Return money')
        self.screen.addstr(14,1, '  q:  Quit')
    
    def display_state(self, state):
        if self.use_ncurses:
            self.ncurses_display_state(state)
        else:
            self.stdout_display_state(state)

    def ncurses_display_state(self, state):
        assert(self.use_ncurses)
        self.screen.addstr(1,1, ' '*40)
        self.screen.addstr(1,1, state)
    
    def display_msg(self, msg):
        if self.use_ncurses:
            self.ncurses_display_msg(msg)
        else:
            self.stdout_display_msg(msg)
        
    def ncurses_display_msg(self, msg):
        assert(self.use_ncurses)
        self.screen.addstr(2,1, ' '*40)
        self.screen.addstr(2,1, msg)
    
    def display_msg2(self, msg):
        if self.use_ncurses:
            self.ncurses_display_msg2(msg)
        else:
            self.stdout_display_msg2(msg)
    
    def ncurses_display_msg2(self, msg):
        assert(self.use_ncurses)
        self.screen.addstr(3,1, ' '*40)
        self.screen.addstr(3,1, msg)
    
    def display_credit(self, credit):
        if self.use_ncurses:
            self.ncurses_display_credit(credit)
        else:
            self.stdout_display_credit(credit)

    def ncurses_display_credit(self, credit):
        assert(self.use_ncurses)
        self.screen.addstr(4,1, ' '*40)
        self.screen.addstr(4,1, 'Credit: $%.2f' % credit)

    def stdout_set_screen_ready(self):
        print('Keys:')
        print('  1:  Deposit 10 cents')
        print('  2:  Deposit 25 cents')
        print('  5:  Deposit 50 cents')
        print('  l:  Deposit 1 dollar')
        print('  t:  Deposit 2 dollars')
        print('  s:  Select drink')
        print('  r:  Return money')
        print('  q:  Quit')

    def stdout_display_state(self, state):
        print('New state:', state)
        
    def stdout_display_msg(self, msg):
        print(msg)
    
    def stdout_display_msg2(self, msg):
        print(msg)

    def stdout_display_credit(self, credit):
        print('Credit: $%.2f' % credit)


class Event(fsm.Event):
    pass

class State(fsm.State):
    pass

class FSM(fsm.FSM):
    pass


class CoinDeposited(Event):

    def __new__(cls, value):
        ev = Event.__new__(cls)
        ev.value = value
        return ev


class DrinkSelected(Event):
    pass

class ReturnMoney(Event):
    pass

class Idle(State):
    pass

class WaitingForFunds(State):
    pass

class WaitingForSelection(State):
    pass

class Dispensing(State):
    pass

class RefundingChange(State):
    pass

class SodaMachine(object):
    
    def __init__(self, ui):
        object.__init__(self)
        self.ui = ui
        self.drink_price = 1.50
        self.coin_bin = 0.0
        self.idle = Idle()
        self.waitingForFunds = WaitingForFunds()
        self.waitingForSelection = WaitingForSelection()
        self.dispensing = Dispensing()
        self.refundingChange = RefundingChange()

        self.sm = FSM([self.idle, self.waitingForFunds, self.waitingForSelection,
                       self.dispensing, self.refundingChange])
        
        do_display_state = fsm.Activity(self.display_state)
        self.sm.add_on_transition_completed_activity(do_display_state)
        
        do_set_screen_ready = fsm.Activity(self.set_screen_ready)

        self.idle.add_enter_activity(do_set_screen_ready)

        to_waitingForFunds_while_adding_funds = fsm.TransitionWithEffect(
                target=self.waitingForFunds,
                effect=self.add_coin_to_bin)
        self.idle.add_transition(event=CoinDeposited,
                                 transition=to_waitingForFunds_while_adding_funds)

        to_waitingForSelection_if_enough_money = fsm.TransitionWithGuard(
                guard=self.amount_in_bin_equal_or_greater_than_drink_price,
                target=self.waitingForSelection)
        to_refundingChange = fsm.Transition(target=self.refundingChange)

        do_add_coin = fsm.Activity(self.add_coin_to_bin)
        do_clear_screen_waitForFunds = fsm.Activity(self.wait_for_funds_clear_screen)

        self.waitingForFunds.add_enter_activity(do_clear_screen_waitForFunds)
        self.waitingForFunds.add_unnamed_transition(to_waitingForSelection_if_enough_money)
        self.waitingForFunds.add_transition(CoinDeposited, to_waitingForSelection_if_enough_money)
        self.waitingForFunds.add_transition(ReturnMoney, to_refundingChange)
        self.waitingForFunds.add_activity(CoinDeposited, do_add_coin)
        
        to_dispensing = fsm.Transition(target=self.dispensing)
        
        self.waitingForSelection.add_transition(ReturnMoney, to_refundingChange)
        self.waitingForSelection.add_activity(CoinDeposited, do_add_coin)
        self.waitingForSelection.add_transition(DrinkSelected, to_dispensing)
        
        do_dispense_and_charge_price = fsm.Activity(self.dispense_drink_and_extract_price_from_bin)
        
        self.dispensing.add_enter_activity(do_dispense_and_charge_price)
        self.dispensing.add_unnamed_transition(to_refundingChange)
        
        to_idle = fsm.Transition(self.idle)
        do_refund = fsm.Activity(self.refund_change)
        
        self.refundingChange.add_enter_activity(do_refund)
        self.refundingChange.add_unnamed_transition(to_idle)
    
    def wait_for_funds_clear_screen(self, event):
        self.ui.display_msg2(' ')
        self.display_amount_in_bin()
    
    def set_screen_ready(self, event):
        self.ui.set_screen_ready()

    def display_state(self, event):
        self.ui.display_state(self.sm.current.get_name())
        
    def display_msg(self, msg):
        self.ui.display_msg(msg)
    
    def display_msg2(self, msg):
        self.ui.display_msg2(msg)

    def display_credit(self):
        self.ui.display_credit(self.coin_bin)
    
    def refund_change(self, event):
        self.display_msg2('Refunding change $%.2f' % self.coin_bin)
        self.coin_bin = 0.0
        self.display_credit()

    def dispense_drink_and_extract_price_from_bin(self, event):
        self.display_msg('Drink dispensed ($%.2f)' % self.drink_price)
        self.coin_bin -= self.drink_price
        self.display_credit()
    
    def amount_in_bin_equal_or_greater_than_drink_price(self, event):
        return not self.amount_in_bin_is_less_than_drink_price(event)
    
    def amount_in_bin_is_less_than_drink_price(self, event):
        return self.drink_price > self.total_amount_in_bin()
    
    def add_coin_to_bin(self, event):
        if CoinDeposited == event:
            self.coin_bin += event.value
        self.display_credit()
    
    def total_amount_in_bin(self):
        return self.coin_bin
    
    def display_amount_in_bin(self):
        self.display_credit()
    
    def start(self):
        self.sm.start()
    
    def stop(self):
        self.sm.stop()
    
    def dispatch(self, event):
        if CoinDeposited == event:
            self.display_msg('Last amount: $%.2f' % (event.value))
        self.sm.stimulate(event)
    
    def process_key(self, key):
        event = None
        if key == '1':
            event = CoinDeposited(0.1)
        elif key == '2':
            event = CoinDeposited(0.25)
        elif key == '5':
            event = CoinDeposited(0.5)
        elif key == 'l':
            event = CoinDeposited(1.0)
        elif key == 't':
            event = CoinDeposited(2.0)
        elif key == 's':
            event = DrinkSelected()
        elif key == 'r':
            event = ReturnMoney()
        
        if None != event:
            self.dispatch(event)


def main(use_ncurses = False):
    key = None
    ui = UI(use_ncurses)
    soda_machine = SodaMachine(ui)
    soda_machine.start()
    while key != 'q':
        key = ui.get_key()
        soda_machine.process_key(key)
    soda_machine.stop()
    ui.shutdown()


if __name__=='__main__':
    main(use_ncurses=False)