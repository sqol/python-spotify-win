#! /usr/bin/python

################################################################################
## 	python-spotify-win
##  python-spotify-win.py                                      
##  Spotify Python library
##
##  sqol 03-jan-2017
################################################################################

## todo
# watch for changes in recently_played.bnk
# pull metadata for track
# pull audio analysis for track

import logging
import win32gui
import win32api
import win32process
import wmi
import os
import pprint
import spotipy
import sys
import watchdog
import time

## variable holding pen
SpotifyUsersDirectory = "Users"

## logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("python-spotify-win started, " + time.strftime("%c"))

c = wmi.WMI()
def get_app_path(hwnd):
    """Get applicatin path given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.ExecutablePath
            break
    except:
        return None
    else:
        return exe
	
def most_recently_modified_dir(path):
	"""Returns most recently modified directory in provided path"""
	try:
		dirlist = {}
		for dir in os.listdir(path):
			dirpath = os.path.join(path, dir) 
			dirlist[dir] = os.path.getmtime(dirpath)
			break
	except:
		logger.debug("Error in most_recently_modified_dir function")
		return None
	else:
		logger.debug("most_recently_modified_dir: %s" % max(dirlist))
		return max(dirlist)

	
def pull_latest_track_id(path):
	"""Returns the track id from recently_played.bnk"""
	with open(path) as infp: data = infp.read()
	data = data.split("spotify:")

	LatestTrack = data[2].replace("track:",'')
	LatestTrack = LatestTrack.split(' ')[0]
	logger.info("Latest track id: %s" % LatestTrack)
	return LatestTrack

def pull_artist_track_from_id(id):
	"""Retrieves track info from Spotify WebAPI"""
	sp = spotipy.Spotify()
	results = sp.track(id)
	with open("output.txt", "w") as fout:
		pprint.pprint(results, stream=fout)
	fout.close()
	t_results = []
	t_results.append(results['name'])
	t_results.append(results['artists'][0]['name'])
	return t_results

window_id = win32gui.FindWindow("SpotifyMainWindow", None)

SpotifyDirectory = os.path.dirname(get_app_path(window_id))
logger.debug("Working Spotify Directory: %s" % SpotifyDirectory)
SpotifyUsersDirectoryPath = os.path.join(SpotifyDirectory, SpotifyUsersDirectory)
logger.debug("SpotifyUsersDirectoryPath: %s" % SpotifyDirectory)

last_modified = most_recently_modified_dir(SpotifyUsersDirectoryPath)
spot_recently_played = os.path.join(SpotifyUsersDirectoryPath, last_modified)
logger.info("User directory: %s" % spot_recently_played)

spot_recently_played = os.path.join(spot_recently_played, 'recently_played.bnk')

trackId = pull_latest_track_id(spot_recently_played)
t_info = pull_artist_track_from_id(trackId)
logger.info("Arist: %s" % t_info[0])
logger.info("Track: %s" % t_info[1])