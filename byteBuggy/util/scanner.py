#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.color import Color
from ..tools.airodump import Airodump
from ..model.target import Target, WPSState
from ..config import Configuration
from ..util.process import Process

import sys,os
import hashlib

from time import sleep, time

class Scanner(object):
    ''' Scans wifi networks & provides menu for selecting targets '''

    # Console code for moving up one line
    UP_CHAR = '\x1B[1F'

    def __init__(self):
        '''
        Scans for targets via Airodump.
        Loops until scan is interrupted via user or config.
        Note: Sets this object's `targets` attrbute (list[Target]) upon interruption.
        '''
        self.last_sameline_length = 0
        self.previous_target_count = 0
        self.targets = []
        self.target = None # Target specified by user (based on ESSID/BSSID)
        self.last_hash = ''

        max_scan_time = Configuration.scan_time

        self.err_msg = None

        # Loads airodump with interface/channel/etc from Configuration
        try:
            with Airodump() as airodump:
                # Loop until interrupted (Ctrl+C)
                scan_start_time = time()

                while True:
                    if airodump.pid.poll() is not None:
                        return  # Airodump process died

                    self.targets = airodump.get_targets(old_targets=self.targets)

                    if self.found_target():
                        return  # We found the target we want

                    if airodump.pid.poll() is not None:
                        return  # Airodump process died

                    # for target in self.targets:
                    #     if target.bssid in airodump.decloaked_bssids:
                    #         target.decloaked = True

                    current_hash = self.targets_hash()
                    if current_hash != self.last_hash:
                        self.print_targets()
                        self.last_hash = current_hash

                    target_count = len(self.targets)
                    client_count = sum(len(t.clients) for t in self.targets)

                    outline = '\r Scanning'
                    if airodump.decloaking:
                        outline += ' & decloaking'
                    outline += '. Found'
                    outline += ' %d target(s),' % target_count
                    outline += ' %d client(s).' % client_count
                    outline += ' Ctrl+C when ready '
                    Color.clear_entire_line()
                    self.print_update(outline)

                    if max_scan_time > 0 and time() > scan_start_time + max_scan_time:
                        return

                    sleep(1)

        except KeyboardInterrupt:
            pass

    def print_update(self, text):
        '''Clears enough lines for the new text, then prints it on the same line.'''
        lines = text.count('\n') + 1  # Count how many lines we will need.
        # Clear lines
        print('\033[2K', end='')  # Clear the current line.
        for _ in range(lines - 1):
            print('\033[1A\033[2K', end='')  # Move up and clear line.
        print('\r' + text, end='')  # Carriage return and print the new text.
        sys.stdout.flush()  # Make sure the text appears immediately.
        self.last_sameline_length = len(text)
        
    def targets_hash(self):
        '''Generates a hash of the current targets list for comparison.'''
        targets_str = ''.join([f'{target.bssid}{target.essid}{target.channel}' for target in self.targets])
        return hashlib.md5(targets_str.encode()).hexdigest()

    def found_target(self):
        '''
        Detect if we found a target specified by the user (optional).
        Sets this object's `target` attribute if found.
        Returns: True if target was specified and found, False otherwise.
        '''
        bssid = Configuration.target_bssid
        essid = Configuration.target_essid

        if bssid is None and essid is None:
            return False  # No specific target from user.

        for target in self.targets:
            if Configuration.wps_only and target.wps not in [WPSState.UNLOCKED, WPSState.LOCKED]:
                continue
            if bssid and target.bssid and bssid.lower() == target.bssid.lower():
                self.target = target
                break
            if essid and target.essid and essid.lower() == target.essid.lower():
                self.target = target
                break

        if self.target:
            print('\n found target %s (%s)'
                % (self.target.bssid, self.target.essid))
            return True

        return False


    def print_targets(self):
        '''Prints targets selection menu (1 target per row).'''
        if len(self.targets) == 0:
            self.print_update('\r')
            return

        output = ''
        # terminal_height = Scanner.get_terminal_height()

        # if self.previous_target_count > 0:
        #     # We need to 'overwrite' the previous list of targets.
        #     if Configuration.verbose <= 1:
        #         # Don't clear screen buffer in verbose mode.
        #         if self.previous_target_count > len(self.targets) or \
        #            terminal_height < self.previous_target_count + 3:
        #             # Either:
        #             # 1) We have less targets than before, so we can't overwrite the previous list
        #             # 2) The terminal can't display the targets without scrolling.
        #             # Clear the screen.
        #             Process.call('clear')
        #         else:
        #             # We can fit the targets in the terminal without scrolling
        output = '\r'
                    
        # First row: columns
        output += 'NUM                     ESSID               BSSID   CH  ENCR  POWER  WPS?  CLIENT\n'
        # Second row: separator
        output += '---            --------------       -------------  ---  ----  -----  ----  ------\n'

        for idx, target in enumerate(self.targets, start=1):
            output += f"{str(idx).rjust(3)}  {target.to_str()}\n" 


        self.print_update(output.rstrip('\n'))


    @staticmethod
    def get_terminal_height():
        rows, _ = os.popen('stty size', 'r').read().split()
        return int(rows)


    @staticmethod
    def get_terminal_width():
        _, columns = os.popen('stty size', 'r').read().split()
        return int(columns)


    def select_targets(self):
        '''
        Returns list(target)
        Either a specific target if user specified -bssid or --essid.
        Otherwise, prompts user to select targets and returns the selection.
        '''

        if self.target:
            # When user specifies a specific target
            return [self.target]

        if len(self.targets) == 0:
            if self.err_msg is not None:
                print(self.err_msg)

            # TODO Print a more-helpful reason for failure.
            # 1. Link to wireless drivers wiki,
            # 2. How to check if your device supporst monitor mode,
            # 3. Provide airodump-ng command being executed.
            raise Exception('No targets found.'
                + ' You may need to wait longer,'
                + ' or you may have issues with your wifi card')

        # Return all targets if user specified a wait time ('pillage').
        if Configuration.scan_time > 0:
            return self.targets

        # Ask user for targets.
        self.print_targets()
        Color.clear_entire_line()

        if self.err_msg is not None:
            print(self.err_msg)

        input_str  = ' select target(s)'
        input_str += ' (1-%d)' % len(self.targets)
        input_str += ' separated by commas, dashes'
        input_str += ' or all: '

        chosen_targets = []

        for choice in input((input_str)).split(','):
            choice = choice.strip()
            if choice.lower() == 'all':
                chosen_targets = self.targets
                break
            if '-' in choice:
                # User selected a range
                (lower,upper) = [int(x) - 1 for x in choice.split('-')]
                for i in range(lower, min(len(self.targets), upper + 1)):
                    chosen_targets.append(self.targets[i])
            elif choice.isdigit():
                choice = int(choice) - 1
                chosen_targets.append(self.targets[choice])

        return chosen_targets


if __name__ == '__main__':
    # 'Test' script will display targets and selects the appropriate one
    Configuration.initialize()
    try:
        s = Scanner()
        targets = s.select_targets()
    except Exception as e:
        print('\r Error: %s' % str(e))
        Configuration.exit_gracefully(0)
    for t in targets:
        print('    Selected: %s' % t)
    Configuration.exit_gracefully(0)