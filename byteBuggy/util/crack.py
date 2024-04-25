#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..config import Configuration
from ..model.handshake import Handshake
from ..model.wpa_result import CrackResultWPA
from ..model.pmkid_result import CrackResultPMKID
from ..util.process import Process
# from ..util.color import Color
from ..tools.aircrack import Aircrack
# from ..tools.cowpatty import Cowpatty
from ..tools.hashcat import Hashcat, HcxPcapTool
# from ..tools.john import John

from json import loads

import os


# TODO: Bring back the 'print' option, for easy copy/pasting. Just one-liners people can paste into terminal.

# TODO: --no-crack option while attacking targets (implies user will run --crack later)

class CrackHelper:
    '''Manages handshake retrieval, selection, and running the cracking commands.'''

    TYPES = {
        '4-WAY': '4-Way Handshake',
        'PMKID': 'PMKID Hash'
    }

    @classmethod
    def run(cls):
        Configuration.initialize(False)

        # Get wordlist
        if not Configuration.wordlist:
            print('\n Enter wordlist file to use for cracking: ')
            Configuration.wordlist = input()
            if not os.path.exists(Configuration.wordlist):
                print(' Wordlist %s not found. Exiting.' % Configuration.wordlist)
                return
            print('')

        # Get handshakes
        handshakes = cls.get_handshakes()
        if len(handshakes) == 0:
            print(' No handshakes found')
            return

        hs_to_crack = cls.get_user_selection(handshakes)
        all_pmkid = all([hs['type'] == 'PMKID' for hs in hs_to_crack])

        # Tools for cracking & their dependencies.
        available_tools = {
            'aircrack': [Aircrack],
            'hashcat':  [Hashcat, HcxPcapTool],
            # 'john':     [John, HcxPcapTool],
            # 'cowpatty': [Cowpatty]
        }
        # Identify missing tools
        missing_tools = []
        for tool, dependencies in available_tools.items():
            missing = [
                dep for dep in dependencies
                if not Process.exists(dep.dependency_name)
            ]
            if len(missing) > 0:
                available_tools.pop(tool)
                missing_tools.append( (tool, missing) )

        if len(missing_tools) > 0:
            print('\n Unavailable tools (install to enable):')
            for tool, deps in missing_tools:
                dep_list = ', '.join([dep.dependency_name for dep in deps])
                print('     * %s (%s)' % (tool, dep_list))

        if all_pmkid:
            print(' Note: PMKID hashes can only be cracked using hashcat')
            tool_name = 'hashcat'
        else:
            print('\n Enter the cracking tool to use (%s): ' % (
                ', '.join(available_tools.keys())))
            tool_name = input()
            if tool_name not in available_tools:
                print(' "%s" tool not found, defaulting to aircrack' % tool_name)
                tool_name = 'aircrack'

        try:
            for hs in hs_to_crack:
                if tool_name != 'hashcat' and hs['type'] == 'PMKID':
                    if 'hashcat' in missing_tools:
                        print(' Hashcat is missing, therefore we cannot crack PMKID hash')
                cls.crack(hs, tool_name)
        except KeyboardInterrupt:
            print('\n Interrupted')

    @classmethod
    def is_cracked(cls, file):
        if not os.path.exists(Configuration.cracked_file):
            return False
        with open(Configuration.cracked_file) as f:
            json = loads(f.read())
        if json is None:
            return False
        for result in json:
            for k in result.keys():
                v = result[k]
                if 'file' in k and os.path.basename(v) == file:
                    return True
        return False

    @classmethod
    def get_handshakes(cls):
        handshakes = []

        skipped_pmkid_files = skipped_cracked_files = 0

        hs_dir = Configuration.wpa_handshake_dir
        if not os.path.exists(hs_dir) or not os.path.isdir(hs_dir):
            print('\n directory not found: %s' % hs_dir)
            return []

        print('\n Listing captured handshakes from %s:\n' % os.path.abspath(hs_dir))
        for hs_file in os.listdir(hs_dir):
            if hs_file.count('_') != 3:
                continue

            if cls.is_cracked(hs_file):
                skipped_cracked_files += 1
                continue

            if hs_file.endswith('.cap'):
                # WPA Handshake
                hs_type = '4-WAY'
            elif hs_file.endswith('.16800'):
                # PMKID hash
                if not Process.exists('hashcat'):
                    skipped_pmkid_files += 1
                    continue
                hs_type = 'PMKID'
            else:
                continue

            name, essid, bssid, date = hs_file.split('_')
            date = date.rsplit('.', 1)[0]
            days,hours = date.split('T')
            hours = hours.replace('-', ':')
            date = '%s %s' % (days, hours)

            handshake = {
                'filename': os.path.join(hs_dir, hs_file),
                'bssid': bssid.replace('-', ':'),
                'essid': essid,
                'date': date,
                'type': hs_type
            }

            if hs_file.endswith('.cap'):
                # WPA Handshake
                handshake['type'] = '4-WAY'
            elif hs_file.endswith('.16800'):
                # PMKID hash
                handshake['type'] = 'PMKID'
            else:
                continue

            handshakes.append(handshake)

        if skipped_pmkid_files > 0:
            print(' Skipping %d *.16800 files because hashcat is missing.\n' % skipped_pmkid_files)
        if skipped_cracked_files > 0:
            print(' Skipping %d already cracked files.\n' % skipped_cracked_files)

        # Sort by Date (Descending)
        return sorted(handshakes, key=lambda x: x.get('date'), reverse=True)


    @classmethod
    def print_handshakes(cls, handshakes):
        # Header
        max_essid_len = max([len(hs['essid']) for hs in handshakes] + [len('ESSID (truncated)')])
        print('  NUM')
        print('  ' + 'ESSID (truncated)'.ljust(max_essid_len))
        print('  ' + 'BSSID'.ljust(17))
        print('  ' + 'TYPE'.ljust(5))
        print('  ' + 'DATE CAPTURED\n')
        print('  ---')
        print('  ' + ('-' * max_essid_len))
        print('  ' + ('-' * 17))
        print('  ' + ('-' * 5))
        print('  ' + ('-' * 19) + '\n')
        # Handshakes
        for index, handshake in enumerate(handshakes, start=1):
            print('  %s' % str(index).rjust(3))
            print('  %s' % handshake['essid'].ljust(max_essid_len))
            print('  %s' % handshake['bssid'].ljust(17))
            print('  %s' % handshake['type'].ljust(5))
            print('  %s\n' % handshake['date'])


    @classmethod
    def get_user_selection(cls, handshakes):
        cls.print_handshakes(handshakes)

        print(' Select handshake(s) to crack (%d-%d, select multiple with , or - or all): ' % (1, len(handshakes)))
        choices = input()

        selection = []
        for choice in choices.split(','):
            if '-' in choice:
                first, last = [int(x) for x in choice.split('-')]
                for index in range(first, last + 1):
                    selection.append(handshakes[index-1])
            elif choice.strip().lower() == 'all':
                selection = handshakes[:]
                break
            elif [c.isdigit() for c in choice]:
                index = int(choice)
                selection.append(handshakes[index-1])

        return selection


    @classmethod
    def crack(cls, hs, tool):
        print('\n Cracking %s %s (%s)' % (
            cls.TYPES[hs['type']], hs['essid'], hs['bssid']))

        if hs['type'] == 'PMKID':
            crack_result = cls.crack_pmkid(hs, tool)
        elif hs['type'] == '4-WAY':
            crack_result = cls.crack_4way(hs, tool)
        else:
            raise ValueError('Cannot crack handshake: Type is not PMKID or 4-WAY. Handshake=%s' % hs)

        if crack_result is None:
            # Failed to crack
            print(' Failed to crack %s (%s): Passphrase not in dictionary' % (
                hs['essid'], hs['bssid']))
        else:
            # Cracked, replace existing entry (if any), or add to
            print(' Cracked %s (%s). Key: "%s"' % (
                hs['essid'], hs['bssid'], crack_result.key))
            crack_result.save()


    @classmethod
    def crack_4way(cls, hs, tool):

        handshake = Handshake(hs['filename'],
                bssid=hs['bssid'],
                essid=hs['essid'])
        try:
            handshake.divine_bssid_and_essid()
        except ValueError as e:
            print(' Error: %s' % e)
            return None

        if tool == 'aircrack':
            key = Aircrack.crack_handshake(handshake, show_command=True)
        elif tool == 'hashcat':
            key = Hashcat.crack_handshake(handshake, show_command=True)
        # elif tool == 'john':
        #     key = John.crack_handshake(handshake, show_command=True)
        # elif tool == 'cowpatty':
        #     key = Cowpatty.crack_handshake(handshake, show_command=True)

        if key is not None:
            return CrackResultWPA(hs['bssid'], hs['essid'], hs['filename'], key)
        else:
            return None


    @classmethod
    def crack_pmkid(cls, hs, tool):
        if tool != 'hashcat':
            print(' Note: PMKID hashes can only be cracked using hashcat')

        key = Hashcat.crack_pmkid(hs['filename'], verbose=True)

        if key is not None:
            return CrackResultPMKID(hs['bssid'], hs['essid'], hs['filename'], key)
        else:
            return None


if __name__ == '__main__':
    CrackHelper.run()