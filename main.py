# File control and browsing
import os
import random
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
# TTS engine
import pyttsx3

# Music/speech mixer and player
from pygame import mixer, _sdl2 as devicer

import json

run = True
playback = True
input_device = ''
engine_properties = ['rate', 'volume', 'voice']
try:
    mixer.init(devicename='CABLE Input (VB-Audio Virtual Cable)')
except:
    print('Could not find CABLE input device! Do you have VB-Audio Virtual Cable installed?')
    print('Link:')
    print('https://vb-audio.com/Cable/')
    print('Make sure you install the file marked as x64, unless you have a 32-bit operating system!')
    print('This window will close in 60 seconds.')
    time.sleep(60)
    quit()
engine = pyttsx3.init()

default_settings = {"rate": engine.getProperty('rate'),
                    "volume": engine.getProperty('volume'),
                    "voice": 0,
                    "playback": playback}
saved_settings: dict = default_settings


def load_settings():
    global saved_settings
    global playback

    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            saved_settings = json.loads(f.read())

        for setting in saved_settings.keys():
            if setting in engine_properties:
                change_engine_property(setting, str(saved_settings[setting]))
            elif setting == 'playback':
                playback = saved_settings['playback']

        print('Loaded saved settings.')

    else:
        print('No saved settings detected, using defaults.')


def save_settings():
    global saved_settings
    global playback

    if saved_settings is None:
        saved_settings = default_settings
    with open('settings.json', 'w') as f:
        f.write(json.dumps(saved_settings))

    print('Settings have been saved to \'settings.json\'')


# Command function
def print_commands():
    print('---=<[COMMANDS]>=---')
    print()
    print('-| !help - Shows this page')
    print()
    print('-| !playback on/off - Enable/disable audio playback')
    print('---| Playback on will allow you to hear a playback of the voice,')
    print('---| But you\'ll have to wait until playback is over to send the next message.')
    print('---| Playback is on by default')
    print()
    print('-| !speed <value> - Change the speed of the speech ')
    print('---| Example: !speed 200 - resets the speed')
    print()
    print('-| !volume <value> - Change the volume of the speech')
    print('---| Has to be between 0 and 1, else resets to 1')
    print('---| Example: !volume 1 - resets the volume')
    print()
    # noinspection PyTypeChecker
    print(f'-| !voice <0-{len(engine.getProperty("voices")) - 1}>')
    print('---| 0 - Male voice, 1 - British female voice, 2 - American female voice')
    print()
    print('-| !play <filename> - Play an audio file')
    print(f'---| Make sure to put the audio file within folder/directory {os.getcwd()}')
    print('---| Example: !play out.wav will repeat the last voice generated')
    print()
    print('-| !stop - stops the currently playing file')
    print()
    print('-| !pause - temporarily pauses the currently playing file')
    print()
    print('-| !resume - resumes the paused file')
    print()
    print('-| !deletesave - Deletes your saved settings')
    print('---| Use only if an error occurs while loading the saved settings.')
    print()
    print('-| !quit - Exit the program')
    print('---| If you exit without using !quit, your settings will not save!')
    print()
    print('---=+=---')


def print_splash():
    splashes = ['I am so tired',
                'Why did I decide to add splashes?',
                'Oh my GOD is asynchronous playback a pain in the ass',
                '"TTSMic worst program ever" says GaMeNu',
                '2am coding GO!']
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print(random.choice(splashes))
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print()


# Utility function to change an engine property
def change_engine_property(property_name: str, command: str):
    global engine
    if property_name not in engine_properties:
        print('Invalid property.')
        return

    old_value = engine.getProperty(property_name)
    index = command.find(' ')
    value_str: str

    if index == -1:
        value_str = command[0::]
    else:
        value_str = command[0:index:]

    try:
        if property_name == 'rate':
            new_value = int(value_str)
            saved_settings['rate'] = new_value
        elif property_name == 'volume':
            new_value = float(value_str)
            saved_settings['volume'] = new_value
        elif property_name == 'voice':
            # noinspection PyTypeChecker
            voices: list = engine.getProperty('voices')
            try:
                new_value = voices[int(value_str)].id
            except IndexError:

                print(f'Value provided is invalid. Use !voice [0-{len(voices) - 1}]')
                return

            saved_settings['voice'] = int(value_str)

        else:
            new_value = None

    except ValueError:
        print(f'Unable to recognize \"{value_str}\" as a valid option.')
    else:
        engine.setProperty(property_name, new_value)
        print(f'Changed {property_name} from {old_value} to {new_value}')


def cmd_help_logic():
    print_commands()


def cmd_speed_logic(command: str):
    change_engine_property('rate', command)


def cmd_volume_logic(command: str):
    change_engine_property('volume', command)


def cmd_voice_logic(command: str):
    change_engine_property('voice', command)


def cmd_playback_logic(command: str):
    global playback

    if command == 'on':
        playback = True
    elif command == 'off':
        playback = False
    else:
        print('Please use !playback on/off')
        return

    saved_settings['playback'] = playback
    print(f'Playback is now set to {playback}')


# Checks whether the file is in the directory,
# then stops the currently playing file and plays the new one
def cmd_play_logic(command: str):
    if command == '':
        print('Incorrect usage. Please use !play <filename> and make sure that:')
        print(f'A. The file is in this program\'s directory ({os.getcwd()})')
        print('B. You reference the file extension too (Example: "!play out.wav" ass opposed to "!play out")')
        return

    index = command.find(' ')
    if index == -1:
        filename = command[0::]
    else:
        filename = command[0:index:]

    path = os.path.join(os.getcwd(), filename)

    if not (os.path.exists(path)):
        print(f'No file found at path {path}')
        return
    mixer.music.stop()
    mixer.music.unload()
    try:
        mixer.music.load(filename)
        mixer.music.play()
    except pygame.error:
        print(f'Could not play file from path {path}')
        print('Please make sure to reference the exact file name including the file extension')
        print('Example: !play out.wav - will play the last generated TTS output')


def cmd_stop_logic():
    mixer.music.stop()
    mixer.music.unload()


def cmd_pause_logic():
    mixer.music.pause()


def cmd_resume_logic():
    mixer.music.unpause()


def cmd_deletesave_logic(command: str):
    global saved_settings
    if len(command) == 0:
        print('Are you sure you want to delete your saved settings?')
        print('This will delete all saved settings permanently!')
        print('Type "!deletesave confirm" to confirm deletion.')

    elif command == 'confirm':
        os.remove('settings.json')
        saved_settings = default_settings
        print('\'settings.json\' has been deleted.')

    else:
        print('Invalid argument. Please use "!deletesave" first.')


def cmd_quit_logic():
    save_settings()
    print('Goodbye, and thank you for using TTSMic!')
    quit()


def is_command(text_input: str, command_name: str) -> bool:
    return text_input.startswith(command_name + ' ') or text_input == command_name


# Main function to decide which command is running
def execute_command(command: str):
    if is_command(command, 'help'):
        cmd_help_logic()

    elif is_command(command, 'speed'):
        cmd_speed_logic(command[len('speed ')::])

    # volume command
    elif is_command(command, 'volume'):
        cmd_volume_logic(command[len('volume ')::])

    # voice command
    elif is_command(command, 'voice'):
        cmd_voice_logic(command[len('voice ')::])

    # playback command
    elif is_command(command, 'playback'):
        cmd_playback_logic(command[len('playback ')::])

    # play command
    elif is_command(command, 'play'):
        cmd_play_logic(command[len('play ')::])

    # stop command
    elif command == 'stop':
        cmd_stop_logic()

    # pause command
    elif command == 'pause':
        cmd_pause_logic()

    # resume command
    elif command == 'resume':
        cmd_resume_logic()

    # deletesave command
    elif is_command(command, 'deletesave'):
        cmd_deletesave_logic(command[len('deletesave ')::])

    # quit command
    elif command == 'quit':
        cmd_quit_logic()

    else:
        print('Unrecognized command.')
    # speed command


# Make sure user has CABLE installed
def check_input_devices():
    global input_device
    print(f'INPUT DEVICES: {devicer.get_audio_device_names(True)}')
    for device in devicer.get_audio_device_names(True):
        if 'CABLE' in device:
            input_device = device
    if input_device == '':
        print('Input device not detected! Quitting program...')
        quit()
    else:
        print(f'Input device found.')


if __name__ == '__main__':

    # Program starts here
    print('Welcome, and thanks for using TTSMic!')
    print('The program will now check that you have the proper input devices')
    print()
    check_input_devices()
    print()
    print_commands()
    print()
    print('---=<[NOTES]>=---')
    print()
    print('If you change your speaker device to CABLE,')
    print('anything played on your computer will be transmitted through your microphone!')
    print()
    print('If you play a message/file over an already playing message/file, the first message/file will stop')
    print()
    print('---=+=---')
    print()
    load_settings()
    print()
    print('Problem while loading settings? Try deleting the save data with "!deletesave"')
    print()
    print('vvvvvvvvvvvvvvvvvvvvvvv')
    print('Scroll up for commands!')
    print('^^^^^^^^^^^^^^^^^^^^^^^')
    print()
    print_splash()
    print('-| TTSMic')
    print('---| Terrible, horrific code by GaMeNu')
    print('---| GitHub: https://github.com/GaMeNu/TTSMic')
    print('---| Btw I am not accountable if you use or modify this program, I just made it for fun')
    print('---| If you distribute the program though, please keep it open source, and DO NOT charge people for it.')
    print()
    print('-| Encountered a bug or an issue? Have a suggestion?')
    print('-| DM me at GMsAlt#6086 on Discord!')
    print()

    while run:
        text = input("Enter text or a command: ")

        if len(text) >= 1:
            if text[0] == '!':
                execute_command(text[1::])
            else:

                # Stop mixer playback to microphone input
                mixer.music.stop()
                mixer.music.unload()

                # Delete the output file
                if os.path.exists(os.path.join(os.getcwd(), 'out.wav')):
                    os.remove('out.wav')

                # Create new output file
                engine.save_to_file(text, 'out.wav')
                engine.runAndWait()

                try:
                    mixer.music.load('out.wav')
                    mixer.music.play()
                except FileNotFoundError:
                    print('Could not find output file.')
                except pygame.error:
                    print('Could not play output file')

                if playback:
                    engine.say(text)
                    engine.runAndWait()

        print()
