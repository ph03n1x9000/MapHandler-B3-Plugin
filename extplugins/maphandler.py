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
    _cycle2_options = []
    _cycle3_options = []
    _wait = 0
    _cronTab = None
    _testStage = 0
    _curCycle = 1
    true = True
    false = False
    _a = 0 # used in functioning
    _c = 1 # used in functioning

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_STOP)
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
            self._cycle3_maps.insert(1, cycle3maps)

        self._player_amount2 = self.config.getint('settings', 'player_amount2')
        self._player_amount3 = self.config.getint('settings', 'player_amount3')


	if self._cronTab:
            # remove existing crontab
            self.console.cron - self._cronTab
            
            self._cronTab = b3.cron.PluginCronTab(self, self.findCycle, '*/5')
            self.console.cron + self._cronTab


     def cycleOne(self):
        self._a = 0
        if self._usetxt == False:
            mapAmt = len(self._cycle1_maps[0])
            nxtMap = self._cycle1_maps[0][self._a]
            self.console.write('g_nextmap %s' % nxtMap)
            self._a += 1
            if self._a > mapAmt:
                self._a = 0
        elif self._usetxt == True:
            self.console.setCvar('g_mapcycle', self._maplist1)


     def cycleTwo(self):
        self._a = 0
        if self._usetxt == False:
            mapAmt = len(self._cycle2_maps[0])
            nxtMap = self._cycle2_maps[0][self._a]
            self.console.write('g_nextmap %s' % nxtMap)
            self._a += 1
            if self._a > mapAmt:
                self._a = 0
        elif self._usetxt == True:
            self.console.setCvar('g_mapcycle', self._maplist2)


     def cycleThree(self):
        self._a = 0
        if self._usetxt == False:
            mapAmt = len(self._cycle3_maps[0])
            nxtMap = self._cycle3_maps[0][self._a]
            self.console.write('g_nextmap %s' % nxtMap)
            self._a += 1
            if self._a > mapAmt:
                self._a = 0
        elif self._usetxt == True:
            self.console.setCvar('g_mapcycle', self._maplist3)


    def cycleAction(self):
        self._clients = 0
        for k in self.console.clients.getClientsByLevel(): # Get players
            self._clients += 1
        if self._clients >= self._player_amount2 or self._player_amount3
            if self._clients >= self._player_amount2 and < self._player_amount3:
                self._curCycle = 2
                self.cycleTwo()
            elif self._clients >= self._player_amount3:
                self._curCycle = 3
                self.cycleThree()
        elif self._clients < self._player_amount2 and self._curCycle != 1:
            self._curCycle = 1
            self.cycleOne()
        else:
            self.debug('Change cycle no longer required')
            

    def findCycle(self):
        self.debug('Checking if player count is high enough for cycle change')
        self._clients = 0
        for k in self.console.clients.getClientsByLevel(): # Get players
            self._clients += 1
        if self._clients >= self._player_amount2 or self._player_amount3
            t = threading.Timer(180, self.cycleAction)
            t.start()
        elif self._clients < self._player_amount2 and self._curCycle != 1:
            self._curCycle = 1
            self.cycleOne()

    def onEvent(self, event):
        if event.type == b3.events.EVT_CLIENT_AUTH:
            self._clients += 1
            self.findCycle()
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            self._clients -= 1
            self.findCycle()
        elif event.type == b3.events.EVT_GAME_ROUND_END:
            if self._curCycle = 2
            self.console.setCvar('%s', %s %(blah, blah))
            self.console.write('%s' % blah)
            
        

            
