from os.path import expanduser,exists
import sys
import socket
import yaml

if socket.gethostname()=='vouga':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='compute':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='ubuntuserver':
    home = {
        'home' : expanduser("~"),
        'scratch' : 'None',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='MEKONG':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
else:
    home = {
        'home' : expanduser("~"),
        'scratch' : '/mnt/scratch/martinsd',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}


proj = home['proj']
scratch= home['scratch']

sardir=scratch+"/s1a_scenes"

sarIn=sardir+"/in"
sarOut=sardir+"/out"

polOut=scratch + "/watermasks"
procOut=scratch + "/processed_watermasks"

orbits_url = 'http://aux.sentinel1.eo.esa.int/RESORB/'

sys.path.insert(0, home['parameters'])

with open(home['parameters']+'/location.yml', 'r') as stream:
    location=yaml.load(stream)

if exists(home['proj']+'/buhayra/credentials.py'):
    from buhayra.credentials import *
