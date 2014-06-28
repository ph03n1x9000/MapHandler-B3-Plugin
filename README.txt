MapHandler-B3-Plugin
====================

 ---------------- Description: ----------------

B3 plugin to assist with map handling. It can change cycles based on amount of players and also change cvars when cycle is changed.

Designed to work on Urban Terror only. Not tested on other games.

 ---------------- Installation: -----------------
 
 Copy maphandler.py to b3/extplugins/
 Copy maphandler.xml to b3/extplugins/conf
 Put your mapcycle lists in your server's q3ut4 folder (same folder with your server.cfg file)
 Edit maphandler.xml as wanted. Do NOT change setting names as this will break the plugin.
 Add the following line to b3.xml plugin section:
 
 <plugin name="maphandler" config="@b3/extplugins/conf/maphandler.xml"/>
 
 
 --------------- Usage: -----------------------
 
 !firstcycle - ll force the first cycle to activate unless it is already active
 !secondcycle - ll force the second cycle to activate unless it is already active
 !thirdcycle - ll force the third cycle to activate unless it is already active
 !admincycle - will activate the admin cycle unless it is already active
 !resetcycle - will reset all values and return to automatic cycling based on player amount
 
 NOTE: Activating fisrstcycle by force will not result in a reset, the game will remain in first cycle until a reset cycle command is issued.
 

