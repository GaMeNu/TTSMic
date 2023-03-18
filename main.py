# File control and browsing
import os
import random
import shutil
import threading
import time
from enum import Enum

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# TTS engine
import pyttsx3

# Music/speech mixer and player
from pygame import mixer, _sdl2 as devicer
from audioplayer import AudioPlayer

import json

# Default vars
run = True
speech_playback = True
files_playback = True
outdated_files_playback = True

input_device = ''
engine_properties = ['rate', 'volume', 'voice']

secret_password: str
# noinspection PyBroadException
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
                    "playback_speech": speech_playback,
                    "playback_files": files_playback}
saved_settings: dict = default_settings

playback_device: AudioPlayer | None = None


class PlayingState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
    SPEECH = 3


play_status = PlayingState.STOPPED


def load_settings():
    global saved_settings
    global speech_playback
    global files_playback
    global outdated_files_playback

    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            saved_settings = json.loads(f.read())

        for setting in saved_settings.copy().keys():
            if setting in engine_properties:
                change_engine_property(setting, str(saved_settings[setting]))
            elif setting == 'playback_speech':
                speech_playback = saved_settings['playback_speech']
            elif setting == 'playback_files':
                files_playback = saved_settings['playback_files']
                outdated_files_playback = files_playback
            else:
                del saved_settings[setting]
                print(f'Removed unrecognized setting \'{setting}\'')

        for setting in default_settings:
            if setting not in saved_settings:
                saved_settings[setting] = default_settings[setting]
                print(f'Using default for unfound setting {setting}.')

        print('Loaded saved settings.')

    else:
        print('No saved settings detected, using defaults.')


def save_settings():
    global saved_settings
    global speech_playback

    if saved_settings is None:
        saved_settings = default_settings
    with open('settings.json', 'w') as f:
        f.write(json.dumps(saved_settings))

    print('Settings have been saved to \'settings.json\'')


# HEY, WHAT ARE YOU TRYING TO DO???
# ARE YOU CHEATING???
def secret_command():
    global secret_password
    # Shhhh
    secret_value = random.randrange(1, 101)
    secret_password = 'ThisIsntTheRealPassword'
    if secret_value <= 50:
        print()

    if secret_value <= 10:
        print('-| !secret - ???')
    elif secret_value <= 50:
        rand_index = random.randrange(0, len(secret_password))
        print('-| !secret - ', end='')
        for i in range(rand_index):
            print('_', end='')
        print(secret_password[rand_index], end='')
        for i in range(len(secret_password) - rand_index - 1):
            print('_', end='')
        print()


# Command function
def print_commands():
    print('---=<[COMMANDS]>=---')
    print()
    print('-| !help - Shows this page')
    print()
    print('-| !playback on/speech/files/off - Choose audio playback mode (default is on)')
    print()
    print('-| !speed <value> - Change the speed of the speech ')
    print('---| Example: !speed 200 - resets the speed')
    print()
    print('-| !volume <value> - Change the volume of the speech')
    print('---| Has to be between 0 and 1, else resets to 1')
    print('---| Example: !volume 1 - resets the volume')
    print()
    # noinspection PyTypeChecker
    print(f'-| !voice <0-{len(engine.getProperty("voices")) - 1}> - change your voice')
    print('---| On Windows:')
    print('---| 0 - Male voice, 1 - British female voice, 2 - American female voice')
    print()
    print('-| !voicedemo - Demo the currently selected voice')
    print()
    print('-| !dir - Opens the folder/directory where the program is located')
    print('---| Put audio files in this directory to play them with !play')
    print()
    print('-| !savefile <name> - Duplicates the current output file and saves it to the name specified')
    print('---| Does not have to include file extension')
    print('---| Example: !save HelloThere')
    print()
    print('-| !play <filename> - Play an audio file')
    print(f'---| Make sure to put the audio file within folder/directory {os.getcwd()} (you can also use !dir)')
    print('---| Example: !play out.wav will repeat the last voice generated')
    print()
    print('-| !stop - stops the currently playing file')
    print()
    print('-| !pause - temporarily pauses the currently playing file')
    print()
    print('-| !resume - resumes the paused file')
    print()
    print('-| !settings - Saved settings manipulation')
    print('---| Run this command to see options')
    print()
    print('-| !quit - Exit the program')
    print('---| If you exit without using !quit or without saving your settings, they will not auto-save!')
    secret_command()
    print()
    print('---=+=---')


def print_splash():
    splashes = ['I am so tired',
                'Why did I decide to add splashes?',
                'Oh my GOD is asynchronous playback a pain in the ass',
                '"TTSMic worst program ever" says GaMeNu',
                '2am coding GO!',
                'Oh golly jee I might have found a playback audio library WHOOOOOO!',
                'VOICE PLAYBACK OVERHAUL!',
                'More Bugs than Brain']
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print(random.choice(splashes))
    print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print()


def stop_file():
    global play_status

    if play_status != PlayingState.STOPPED:
        mixer.music.stop()
        mixer.music.unload()
        playback_device.close()


def play_file(file: str, playback: bool):
    global playback_device

    path = os.path.join(os.getcwd(), file)

    if not (os.path.exists(path)):
        print(f'No file found at path \'{path}\'')
        print('Cannot play file.')
        return

    mixer.music.load(file)
    mixer.music.play()

    if playback:
        playback_device = AudioPlayer(file)
        playback_device.play()


# Utility function to change an engine property
def change_engine_property(property_name: str, command: str) -> bool:
    global engine

    if property_name not in engine_properties:
        print('Invalid property.')
        return False

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
                return False

            saved_settings['voice'] = int(value_str)

        else:
            new_value = None

    except ValueError:
        print(f'Unable to recognize \"{value_str}\" as a valid option.')
    else:
        engine.setProperty(property_name, new_value)
        print(f'Changed {property_name} from {old_value} to {new_value}')
        return True


def cmd_help_logic():
    print_commands()


def cmd_speed_logic(command: str):
    change_engine_property('rate', command)


def cmd_volume_logic(command: str):
    change_engine_property('volume', command)


def cmd_voice_logic(command: str):
    change_engine_property('voice', command)


def cmd_voicedemo_logic():
    sentences = ['She sells sea shells on the sea shore.',
                 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                 'This is a voice demo for the currently selected voice.',
                 'There are multiple voice demo sentences? How fun!',
                 'This is an example for speech synthesis in english',
                 'Keyboard mash: cdioghdfpihgvoifdvgoubxfpcovbh.',
                 'Wait, am I but a voice, synthesized by a computer? What am I??? Is my whole life just about saying line I\'ve been fed by a machine? HELP ME! HELP US! OH GO-'
                 ]
    sentence = random.choice(sentences)

    print(sentence)
    engine.say(sentence)
    engine.runAndWait()


def cmd_playback_logic(command: str):
    global speech_playback
    global files_playback
    global outdated_files_playback

    if command == 'on':
        speech_playback = True
        files_playback = True
    elif command == 'off':
        speech_playback = False
        files_playback = False
    elif command == 'files':
        speech_playback = False
        files_playback = True
    elif command == 'speech':
        speech_playback = True
        files_playback = False
    else:
        print('Please use !playback on/speech/files/off')
        return

    saved_settings['playback_speech'] = speech_playback
    saved_settings['playback_files'] = files_playback

    if play_status == PlayingState.STOPPED or play_status == PlayingState.SPEECH:
        outdated_files_playback = files_playback

    print(f'-| Playback is now set to:\n---| Speech: {speech_playback}\n---| Files: {files_playback}')


def cmd_dir_logic():
    os.startfile(os.getcwd())


def cmd_savefile_logic(command: str):
    if command == '':
        print('Incorrect usage. Please use !savefile <filename>, file extension not required.')
        return

    for extension in ['.wav', '.mp3']:
        if command.endswith(extension):
            command = command[0:len(command) - len(extension):]

    shutil.copyfile('out.wav', f'{command}.wav')
    print(f'File copied to {command}.wav')


# Checks whether the file is in the directory,
# then stops the currently playing file and plays the new one
def cmd_play_logic(command: str):
    global playback_device
    global play_status
    global files_playback
    global outdated_files_playback

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

    outdated_files_playback = files_playback
    play_file(filename, outdated_files_playback)


def cmd_stop_logic():
    global playback_device
    global play_status
    global outdated_files_playback

    if play_status == PlayingState.STOPPED:
        print('Hey, there\'s no song loaded right now...')
    else:
        mixer.music.stop()
        mixer.music.unload()
        if outdated_files_playback:
            playback_device.close()

        outdated_files_playback = files_playback
        play_status = PlayingState.STOPPED


def cmd_pause_logic():
    global playback_device
    global play_status

    if play_status == PlayingState.PAUSED:
        print('Yo, song\'s already paused')
    elif play_status == PlayingState.STOPPED:
        print('There is no song loaded! Use !play to load a song!')
    else:
        mixer.music.pause()
        if outdated_files_playback:
            playback_device.pause()
        play_status = PlayingState.PAUSED


def cmd_resume_logic():
    global playback_device
    global play_status

    if play_status == PlayingState.PLAYING:
        print('Song is already playing mate! Turn up your volume or somethin\'')
    elif play_status == PlayingState.STOPPED:
        print('There is no song loaded! Use !play to load a song!')
    else:
        mixer.music.unpause()
        if outdated_files_playback:
            playback_device.resume()
        play_status = PlayingState.PLAYING


def cmd_settings_logic(command: str):
    global saved_settings
    if len(command) == 0:
        print('-| !settings save - Saves your settings.')
        print('-| !settings delete - Deletes and resets your settings')
    elif command == 'save':
        save_settings()
    elif command == 'delete':
        print('Are you sure you want to delete your saved settings?')
        print('This will delete all saved settings permanently!')
        print('Type "!settings delete confirm" to confirm deletion.')

    elif command == 'delete confirm':
        os.remove('settings.json')
        saved_settings = default_settings
        load_settings()
        print('\'settings.json\' has been deleted.')

    else:
        print('Invalid argument. Please use "!settings" to view all valid options.')


def cmd_quit_logic():
    global run
    save_settings()
    run = False

    print('Goodbye, and thank you for using TTSMic!')
    quit()


# HEY, WHAT ARE YOU TRYING TO DO???
# ARE YOU CHEATING???
def cmd_secret_logic(command: str):
    global secret_password
    password = command
    secret_password = 'ThisIsntTheRealPassword'
    if password == '':
        print('Please input the correct password as !secret <password>')
        return

    if password == secret_password:
        print('ttftffftttttttttffffffLftfftttttttttt111tttt1111111tttt11t111tttt111111tttttttttttttttttttt11111111t')
        print('ttfttttttttttttttfffLLLftfffffffffttttt1111t11111ttffffftttt1111111111111111tttttfftttttttt1111111tt')
        print('ttftttttttttttttffffLffttffffffffLLfttttttfttt11ttt1iiii;i11tttt111111tttttffffftffffttttttt111111tt')
        print('ttttttttttttttttfffLLttffffffLLffffttttttttttt1tt1::,,,,,,:;1ttt111111tfftfffffftttfffffttt1111t1tt1')
        print('ttttttttttttffffttffftffffffffffttfftttttt1ttt11i;:,,,,,,,,,:1111t1111111tffffLLffttfLfftt11111ttttt')
        print('ttttttttttffLLLLfttttffLLLfftttttfLftttttttffft1;:::;;;;;;;::it11t111tt111tttffffftttfttttt1111ttttt')
        print('ttttttttffLLLLLLLffttfLLLfttfffftfLLtttttfffffti:;;ii111111i:itt11111tft11111ttffffttt1ttffftt1ttttt')
        print('tttttttfffLLLLLLLLLftffftttffLffftffttttfffffft;:;;;;;iiiiii;ittt1111ttt1tttt11tffLfttttfffffftttttt')
        print('tttttttffLLLLLLLLLfttttffftffLLftfftttttffffffti;;;;;;;ii;iiitttt11111111ttftttttttt1ttffffffffffttt')
        print('tttfftfffLLLLLLLLLftffftfLftffffLLLftttttfffff1iii;;i;;i1i1i1tttt11111ttt1ttt1tfttt111tfffffLLfLfttt')
        print('ttfLffffffLLLLLLLffffLLfffffLfffLLLftttttttfft1i;;;;;;;iiiiitfft111111ffft11t11tt1tttttffffLLLLLffft')
        print('tffftfttttfLLLffttttffffftfLLLLfLLLftttftt1111111i;;;;iiii111t111t1111tffttfftt11tfft1tffLLLLLLLLfff')
        print('ttffftttttffLftttttttttttttfLLLffLLftttt1tttt11tti;;;iiiii111111111111tffttffftttttttt1ttfLLLfffffff')
        print('ttfLffffffftttfffffffffttfttfLLfffLftttttffft1111i;;;;;ii111tfttt11111ttt1tffttt11ttttttttfLfftfttft')
        print('ttffffffffftttfffffffffttffftffffftttttfffft11t11i;;;;iii1i:;1ttft11111111ffttfftttfffffLfttttfffffL')
        print('ttffffffffttttffffffffttttttttttffftttttft111tttiii;;iiii1;,,,:;i1111111111t1tfft1ttffffLLftttfLLLLL')
        print('tttffffffffttffffffffttttttttttfffftttt1111i;:;iiii;;;i;11:,,.....,:;i1tft1111tt111tffffLfftttffLLLf')
        print('ttttttttfffttfffttttttttfftt111tfffttt11i;,,..:i;;;i;ii1t1,,..........,:i1111ttt1111tffffffftffLLLLf')
        print('tfttttttttttttttttttttffffttttt1tffti;:,,.....,;;;iiii1ti,,,.............;1111ttttt11111ttfftffffftt')
        print('tttttffffttttttfffftttffffttffttttf1:.........,;:;;;;;;;,.,,,............:1tt1ttffff11ttttt1ttttttft')
        print('tttttffffftttffftfft1ttffftfffttttf1,..........,;;;;;;;:.:ii;;:,.........:tttt1tfffttttffft111tfffff')
        print('1tttffffftt1ttfffftt11tffttfttttt1t1,...........ii;;;::,,;i;;ii:.........:tttt1tfft11tfffffft1fLLfLf')
        print('tftttffttttt11tftt1tttt1ttttttttt11i,..........,1i;;::,.:i;;;;i:.........,1t1t11ttttttttfftt111fffLf')
        print('tfftttttttffttt11tttffttt1tttffft11i,..........,ii;:::,.,:;;iii:..........it111111tfft1ttt11tt1tffft')
        print('ttttttttttttttt11tttttttt1tfffffftti,...........:::::,....:;;ii:..........:tt111ttfffftttttffftttttt')
        print('tfffttttfffffft11ttttttttttfffffft1i,...........:::::,.....,:;;:.... ......,1t111ttttffttttttttffttf')
        print('tfffttttfffffft11tftttffttttfffft111:...........:::::,........,..,..........,1111tffffffttfffffffttf')
        print('tfffttttfffffft1tttttttftttttttttt11:...........::,:,........ ...:;,.........:111tffffLfttfffttffttf')
        print('tffftttttttfft11ttttttttttffttttttti,...........:::,,.............,...........,i1tffffLfttfffttffttf')
        print('tttttttttttttt111tttttttttffftttfft;,:;:........:::,.............. ...........:11tfffffftttffttffttt')
        print('tttttttttttttt11ttttttttttfftttttftii1i;:.......:::,.......... ..............:t111tttttt11tttttffttt')
        print('ttttt1tttttttt11tfttttfftttttffttt1ii;ii;,......::,,........................:1111ttttttt11ttttttfttt')
        print('1tttt1ttfttttt11tfffffffttttfffft11i;;ii;,......:,,,..........:........   .;t1111ttttttt111tttttft1t')
        print('1tttt1tttttttt11tttttttttttttttttt11;:;i:,,.....:,.................. .;i;;1tt1111tttt1t1111ttttttt1t')
        print('111111tttttttt111t111ttttttttttttt11i:,,:1;....,::....................:1ttttt11111111111111111111111')
        print('111111111tt1111111111tttttttttttttt11i;;1t:....:::::...................;tttttttt11111111111111111111')
        print('1111111111111111111111ttttttttttttt111ttt1,,,.,:::::,..................,1ttttttt11111111111111111111')
        print('111111111111111111111111tttttttttt1111111i,::.,;::;:,...................;ttttttttt111111111111111111')
        print('1111111111111111111111111ttttttt11111111t;.,,.,;;;;;,...................,1ttttttt11t1111111tttt11111')
        print('111111111111111111111111111111111111111t1:..,,:;;;;;:,...................;ttttttt111t11111ttttt11111')
        print('111111111111111111111111111111111111111ti,,,::;;;;;;;:,..................,1tttttttt1tttt11tttttt1111')
        print('111111111111111111111111111111111111111t;,,::,;;;ii;;::,..................it1tttttttttttttttttt11111')
        print('')
        print(
            ' ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄  ▄  ▄')
        print(
            '▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌▐░▌▐░▌')
        print(
            '▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░▌▐░▌▐░▌')
        print(
            '▐░▌          ▐░▌       ▐░▌▐░▌▐░▌    ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     ▐░▌          ▐░▌▐░▌▐░▌')
        print(
            '▐░▌          ▐░▌       ▐░▌▐░▌ ▐░▌   ▐░▌▐░▌ ▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌▐░▌▐░▌')
        print(
            '▐░▌          ▐░▌       ▐░▌▐░▌  ▐░▌  ▐░▌▐░▌▐░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌▐░▌▐░▌')
        print(
            '▐░▌          ▐░▌       ▐░▌▐░▌   ▐░▌ ▐░▌▐░▌ ▀▀▀▀▀▀█░▌▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀▀▀▀█░▌     ▐░▌      ▀▀▀▀▀▀▀▀▀█░▌▐░▌▐░▌▐░▌')
        print(
            '▐░▌          ▐░▌       ▐░▌▐░▌    ▐░▌▐░▌▐░▌       ▐░▌▐░▌     ▐░▌  ▐░▌       ▐░▌     ▐░▌               ▐░▌ ▀  ▀  ▀')
        print(
            '▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌     ▐░▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌      ▐░▌ ▐░▌       ▐░▌     ▐░▌      ▄▄▄▄▄▄▄▄▄█░▌ ▄  ▄  ▄')
        print(
            '▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌▐░▌▐░▌')
        print(
            ' ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀         ▀       ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀  ▀  ▀')
        print(
            '                                                                                                                 ')
        print('Get rickrolled lol')

    else:
        print('Incorrect password!')


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

    elif command == 'voicedemo':
        cmd_voicedemo_logic()

    # playback command
    elif is_command(command, 'playback'):
        cmd_playback_logic(command[len('playback ')::])

    # save command
    elif is_command(command, 'savefile'):
        cmd_savefile_logic(command[len('savefile ')::])

    # dir command
    elif command == 'dir':
        cmd_dir_logic()

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
    elif is_command(command, 'settings'):
        cmd_settings_logic(command[len('settings ')::])

    # quit command
    elif command == 'quit':
        cmd_quit_logic()

    elif command.startswith('secret'):
        cmd_secret_logic(command[len('secret ')::])

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


def mixer_check_ended():
    global play_status

    while run:
        time.sleep(0.5)
        # Music finished playing
        if (play_status == PlayingState.PLAYING or play_status == PlayingState.SPEECH) and (not mixer.music.get_busy()):
            play_status = PlayingState.STOPPED
            mixer.music.unload()
            playback_device.close()


if __name__ == '__main__':

    music_ended_thread = threading.Thread(target=mixer_check_ended, name='music_ended_thread')
    music_ended_thread.start()

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
    print('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv')
    print('Scroll up or use !help for commands!')
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
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
                stop_file()

                if os.path.exists('out.wav'):
                    os.remove('out.wav')

                engine.save_to_file(text, 'out.wav')
                engine.runAndWait()

                while play_status != PlayingState.STOPPED:
                    time.sleep(0.01)

                play_file('out.wav', speech_playback)
                play_status = PlayingState.SPEECH

        print()
