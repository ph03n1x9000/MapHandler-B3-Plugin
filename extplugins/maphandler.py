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
    _gamefolder = ""
    _mapfile1 = ""
    _mapfile2 = ""
    _mapfile3 = ""
    _adminfile = ""
    _player_amount2 = 6
    _player_amount3 = 10
    _cycle2_options = []
    _cycle3_options = []
    _original_options = []
    _currentCycle = 1
    _clients = 0
    _forced = 0
    _a1 = 0 #Used for map order sequence
    _a2 = 0 #Used to activate options and change cvars on cycle change
    _a3 = 0 #Used in event functioning


    def onStartup(self):
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
        self._loadSettings()


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func
        
        return None


    def onEvent(self, event):
        if event.type == b3.events.EVT_CLIENT_AUTH:
            self._clients += 1
            if self._forced == 0:
                self._checkPhaseTwo()
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            self._clients -= 1
            if self._forced == 0:
                self._checkPhaseTwo()
        elif event.type == b3.events.EVT_GAME_WARMUP:
            self._activateOptions()
       

    def _loadSettings(self):
        self._mapfile1 = self.config.get('settings', 'mapfile1')
        self._mapfile2 = self.config.get('settings', 'mapfile2')
        self._mapfile3 = self.config.get('settings', 'mapfile3')
        self._adminfile = self.config.get('settings', 'admin_mapfile')
        self._player_amount2 = self.config.getint('settings', 'player_amount2')
        self._player_amount3 = self.config.getint('settings', 'player_amount3')
        opt1 = self.config.get('options', 'original_options')
        self._original_options = opt1.split(', ')
        opt2 = self.config.get('options', 'cycle2_options')
        self._cycle2_options = opt2.split(', ')
        opt3 = self.config.get('options', 'cycle3_options')
        self._cycle3_options = opt3.split(', ')

    def cycleOne(self):
        if self._currentCycle != 1:
            self._currentCycle = 1 
        self.console.setCvar('g_mapcycle', self._mapfile1)
            
    def cycleTwo(self):
        if self._currentCycle != 2:
            self._currentCycle = 2
        self.console.setCvar('g_mapcycle', self._mapfile2)

    def cycleThree(self):
        if self._currentCycle != 3:
            self._currentCycle = 3
        self.console.setCvar('g_mapcycle', self._mapfile3)

    def adminCycle(self):
        if self._currentCycle != 4:
            self._currentCycle = 4
        self.console.setCvar('g_mapcycle', self._adminfile)


    def _checkPhaseTwo(self):
        self.debug('Phase two checking: Started')
        self._clients = len(self.console.clients.getList())
        q1 = self._player_amount2
        q2 = self._player_amount3
        if self._clients < q2 and self._currentCycle != 1:
            self._a1 = 0
            self._a2 = 1
            self.cycleOne()
        elif self._clients >= q1 and self._clients < q2:
            if self._currentCycle != 2:
                self._a1 = 0
                self._a2 = 1
                self.cycleTwo()
        elif self._clients >= q2 and self._currentCycle != 3:
            self._a1 = 0
            self._a2 = 1
            self.cycleThree()
    

    def _checkPhaseOne(self):
        if self._forced == 0:
            self.debug('Phase one checking: Started')
            self._clients = len(self.console.clients.getList())
            if self._clients >= self._player_amount2 and self._clients < self._player_amount3:
                if self._currentCycle != 2:
                    t = threading.Timer(180, self._checkPhaseTwo)
                    t.start()
            elif self._clients >= self._player_amount3 and self._currentCycle != 3:
                t = threading.Timer(180, self._checkPhaseTwo)
                t.start()
            elif self._clients < self._player_amount2 and self._currentCycle != 1:
                t = threading.Timer(180, self._checkPhaseTwo)
                t.start()

    def _activateOptions(self):
        if self._currentCycle == 1 and self._a2 == 1:
            k1 = 0
            k2 = len(self._original_options)
            self._a2 = 0
            while k1 < k2:
                self.console.write('%s' % (self._original_options[k1]))
                k1 += 1
        elif self._currentCycle == 2 and self._a2 == 1:
            k1 = 0
            k2 = len(self._cycle2_options)
            self._a2 = 0
            while k1 < k2:
                self.console.write('%s' % (self._cycle2_options[k1]))
                k1 += 1
        elif self._currentCycle == 3 and self._a2 == 1:
            k1 = 0
            k2 = len(self._cycle3_options)
            self._a2 = 0
            while k1 < k2:
                self.console.write('%s' % (self._cycle3_options[k1]))
                k1 += 1

    def _resetPhase(self):
        #self._clients = len(self.console.clients.getList())
        self._clients = 0
        for k in self.console.clients.getClientsByLevel(): # Get players
            self._clients += 1
        self._forced = 0
        self._checkPhaseTwo()
        self._activateOptions()
        self.console.say('Map cycling returned to normal')
        


#------------ COMMANDS --------------------------

    def cmd_firstcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to first cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        if self._currentCycle == 1:
            client.message('^7First mapcycle is already active.')
            return
        elif self._currentCycle != 1:
            self._forced = 1
            self._a2 = 1
            self.cycleOne()
            client.message('^7Mapcycle changed to first cycle')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        
        if input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t3 = threading.Timer((time * 60), self._resetPhase)
            t3.start()
            client.message('^7Cycle will reset in ^5%s ^7minutes' % time)
            

    def cmd_secondcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to second cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        if self._currentCycle == 2:
            client.message('^7Second mapcycle is already active.')
            return
        elif self._currentCycle != 2:
            self._forced = 1
            self._a2 = 1
            self.cycleTwo()
            client.message('^7Mapcycle changed to second cycle')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        
        input = self._adminPlugin.parseUserCmd(data)
        if input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t3 = threading.Timer((time * 60), self._resetPhase)
            t3.start()
            client.message('^7Cycle will reset in ^5%s ^7minutes' % time)


    def cmd_thirdcycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to third cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        if self._currentCycle == 3:
            client.message('^7Third mapcycle is already active.')
            return 
        elif self._currentCycle != 3:
            self._forced = 1
            self._a2 = 1
            self.cycleThree()
            client.message('^7Mapcycle changed to third cycle')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        
        if input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t3 = threading.Timer((time * 60), self._resetPhase)
            t3.start()
            client.message('^7Cycle will reset in ^5%s ^7minutes' % time)


    def cmd_admincycle(self, data, client, cmd=None):
        """\
        <number> Manually change map cycle to admin cycle for <number> minutes. Omit number for permanent change.
        """
        input = self._adminPlugin.parseUserCmd(data)
        if self._currentCycle == 4:
            client.message('^7Admin mapcycle is already active.')
            return
        elif self._currentCycle != 4:
            self._forced = 1
            self.adminCycle()
            client.message('^7Mapcycle changed to admin cycle')
            client.message('^7Use ^2!resetcycle ^7to return to normal')
        if input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t3 = threading.Timer((time * 60), self._resetPhase)
            t3.start()
            client.message('^7Cycle will reset in ^5%s ^7minutes' % time)
        

    def cmd_resetcycle(self, data, client, cmd=None):
        input = self._adminPlugin.parseUserCmd(data)
        if input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t3 = threading.Timer((time * 60), self._resetPhase)
            t3.start()
            client.message('^7Cycle will reset in ^5%s ^7minutes' % time)
        if not input:
            self._resetPhase()
            client.message('^2Mapcycle has been reset')
            
            




            




    
        


