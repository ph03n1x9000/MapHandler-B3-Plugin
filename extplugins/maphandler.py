# MapHandler Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2014 ph03n1x
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__version__ = '1.0.0'
__author__ = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin
import b3.cron
import shutil
import os


class MaphandlerPlugin(b3.plugin.Plugin):
    _clients = 0
    _player_amount2 = 6
    _player_amount3 = 24
    _usetxt = True
    _gamefolder = ""
    _maplist1 = 0
    _maplist2 = 0
    _maplist3 = 0
    _cycle1_maps = []
    _cycle2_maps = []
    _cycle3_maps = []
    _cycle1_options = []
    _cycle2_options = []
    _cycle3_options = []
    _wait = 0
    _cronTab = None
    _testStage = 0
    _curCycle = 1
    _manual = False # used to find if the mapcycle was manually altered
    _nextmap = ""
    true = True
    false = False
    _a = 0 # used for map order sequence
    _c = 1 # used in functioning
    _r = 0 # Used in cvar activation

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_GAME_WARMUP)
        self._adminPlugin = self.console.getPlugin('admin')

        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        # Register commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

    def onLoadConfig(self):
        for cvar in self.config.get('maplist2_options/cvar'):
            optCvar2 = cvar.find('cvar').text
            self._cycle2_options.insert(1, optCvar2)

        for cvar in self.config.get('maplist3_options/cvar'):
            optCvar3 = cvar.find('cvar').text
            self._cycle3_options.insert(1, optCvar3)

        for cvar in self.config.get('original_options/cvar'):
            optCvar1 = cvar.find('cvar').text
            self._cycle1_options.insert(1, optCvar1)


        self._usetxt = self.config.get('settings', 'usetxt')
        if self._usetxt == True:
            self._gamefolder = self.config.get('settings', 'gamefolder')
            self._maplist1 = self.config.get('settings', 'maplist1')
            self._maplist2 = self.config.get('settings', 'maplist2')
            self._maplist3 = self.config.get('settings', 'maplist3')
        elif self.usetxt == False:
            cycle1maps = self.config.get('settings', 'cycle1_maps')
            cycle1maps = cycle1maps.split(', ')
            cycle2maps = self.config.get('settings', 'cycle2_maps')
            cycle2maps = cycle2maps.split(', ')
            cycle3maps = self.config.get('settings', 'cycle3_maps')
            cycle3maps = cycle3maps.split(', ')
            self._cycle1_maps.insert(1, cycle1maps)
            self._cycle2_maps.insert(1, cycle2maps)
            if cycle3maps != 0:
                self._cycle3_maps.insert(1, cycle3maps)

        self._player_amount2 = self.config.getint('settings', 'player_amount2')
        self._player_amount3 = self.config.getint('settings', 'player_amount3')


        #if self._cronTab:
        #    # remove existing crontab
        #    self.console.cron - self._cronTab    
        #    self._cronTab = b3.cron.PluginCronTab(self, self.findCycle, '*/8')
        #    self.console.cron + self._cronTab


    def cycleOne(self):
        if self._usetxt == False:
           mapAmt = len(self._cycle1_maps[0])
           nxtMap = self._cycle1_maps[0][self._a]
           self.console.write('g_nextmap %s' % nxtMap)
           self._a += 1
           if self._a > mapAmt:
               self._a = 0
        elif self._usetxt == True and self._curCycle != 1:
            self.console.setCvar('g_mapcycle', self._maplist1)
            self._curCycle = 1


    def cycleTwo(self):
        if self._usetxt == False:
            mapAmt = len(self._cycle2_maps[0])
            nxtMap = self._cycle2_maps[0][self._a]
            self.console.write('g_nextmap %s' % nxtMap)
            self._a += 1
            if self._a > mapAmt:
                self._a = 0
        elif self._usetxt == True and self._curCycle != 2:
            self.console.setCvar('g_mapcycle', self._maplist2)
            self._curCycle = 2


    def cycleThree(self):
        if self._usetxt == False:
            mapAmt = len(self._cycle3_maps[0])
            nxtMap = self._cycle3_maps[0][self._a]
            self.console.write('g_nextmap %s' % nxtMap)
            self._a += 1
            if self._a > mapAmt:
                self._a = 0
        elif self._usetxt == True and self._curCycle != 3:
            self.console.setCvar('g_mapcycle', self._maplist3)
            self._curCycle = 3


    def cycleAction(self):
        self._manual = False
        self._clients = 0
        for k in self.console.clients.getClientsByLevel(): # Get players
            self._clients += 1
        if self._clients >= self._player_amount2 or self._player_amount3:
            if self._clients >= self._player_amount2 and self._clients < self._player_amount3:
                self._curCycle = 2
                self._r = 1
                self._a = 0
                self.cycleTwo()
            elif self._clients >= self._player_amount3:
                self._curCycle = 3
                self._r = 1
                self._a = 0
                self.cycleThree()
        elif self._clients < self._player_amount2 and self._curCycle != 1:
            self._curCycle = 1
            self._r = 1
            self._a = 0
            self.cycleOne()
        else:
            self.debug('Change cycle no longer required')
            return
            

    def findCycle(self):
        self.debug('Checking if player count is high enough for cycle change')
        self._clients = 0
        for k in self.console.clients.getClientsByLevel(): # Get players
            self._clients += 1
        if self._clients >= self._player_amount2 or self._player_amount3:
            t = threading.Timer(180, self.cycleAction)
            t.start()
        elif self._clients < self._player_amount2 and self._curCycle != 1:
            self._curCycle = 1
            self._a = 0
            self.cycleOne()
            

    def onEvent(self, event):
        if event.type == b3.events.EVT_CLIENT_AUTH:
            self._clients += 1
            if self._manual == False:
                q1 = range(int(self._player_amount2))
                q2 = range(int(self._player_amount2), int(self._player_amount3))
                if self._clients in q1 and self._curCycle != 1:
                    self.findCycle()
                elif self._clients in q2 and self._curCycle != 2:
                    self.findCycle()
                elif self._clients >= self._player_amount3 and self._curCycle != 3:
                    self.findCycle()
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            self._clients -= 1
            if self._manual == False:
                q1 = range(int(self._player_amount2))
                q2 = range(int(self._player_amount2), int(self._player_amount3))
                if self._clients in q1 and self._curCycle != 1:
                    self.findCycle()
                elif self._clients in q2 and self._curCycle != 2:
                    self.findCycle()
                elif self._clients >= self._player_amount3 and self._curCycle != 3:
                    self.findCycle()
        elif event.type == b3.events.EVT_GAME_WARMUP:
            if self._curCycle == 2:
                self.cycleTwo()
                if self._r == 1:
                    for m in range(len(self._cycle2_options)):
                        # self.console.setCvar('%s', '%s') %(blah, blah)
                        self.console.write('%s' % (self._cycle2_options[m]))
                    self._r = 0
            elif self._curCycle == 3:
                self.cycleThree()
                if self._r == 1:
                    for m in range(len(self._cycle3_options)):
                        self.console.write('%s' % (self._cycle3_options[m]))
                    self._r = 0
            elif self.curCycle == 1:
                self.cycleOne()
                if self._r == 1:
                    for m in range(len(self._cycle1_options)):
                        self.console.write('%s' % (self._cycle1_options[m]))
                    self._r = 0

# ---------------- Commands ---------------------------------------

    def cmd_firstcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to first cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        self._manual = True
        if not input:
            self._curCycle = 1
            self.cycleOne()
            client.message('^7Mapcycle changed to first cycle permanently')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t2 = threading.Timer((time * 60), self.cycleAction)
            t2.start()
            client.message('^7You changed to ^5first ^7map cycle for ^5%s ^7minutes' % time)
            client.message('^7Use ^2!resetcycle ^7to return to normal cycle')

    def cmd_secondcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to second cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        self._manual = True
        if not input:
            self._curCycle = 2
            self.cycleTwo()
            client.message('^7Mapcycle changed to second cycle permanently')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t2 = threading.Timer((time * 60), self.cycleAction)
            t2.start()
            client.message('^7You changed to ^5second ^7map cycle for ^5%s ^7minutes' % time)
            client.message('^7Use ^2!resetcycle ^7to return to normal cycle')

    def cmd_thirdcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to third cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        self._manual = True
        if not input:
            self._curCycle = 3
            self.cycleThree()
            client.message('^7Mapcycle changed to third cycle permanently')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t2 = threading.Timer((time * 60), self.cycleAction)
            t2.start()
            client.message('^7You changed to ^5third ^7map cycle for ^5%s ^7minutes' % time)
            client.message('^7Use ^2!resetcycle ^7to return to normal cycle')

    def cmd_resetcycle(self, data, client, cmd=None):
        """\
        Return map cycle to normal and turn on automatic cycle switching
        """
        self.cycleAction()
        client.message('^7You have reset the map cycle')
          
