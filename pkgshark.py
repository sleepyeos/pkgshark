#!/usr/bin/env python3

import os
import time
import webbrowser
import urllib.parse
import PySimpleGUI as sg

class PackageShark:

  def __init__(self):
    sg.change_look_and_feel('Reddit')

    self.title = 'PKG SHARK 2.1'
    self.base_query_url = 'https://duckduckgo.com/?q='

    self.mainListBox = sg.Listbox(values=([]), size=(50,30),key='-LIST-', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)

    self.layout = [ [sg.InputText(key='-QUERY-', size=(40,1),change_submits=True), sg.Button('  Filter ')],
            [self.mainListBox, sg.Column([[sg.Output(key='-OUT-', size=(50,32))]])],
            [sg.Button('Connect'), sg.Button('Lookup'), sg.Button('Remove'), sg.Button('Help'), sg.Exit()],
            [sg.Button(' Freeze '), sg.Button('Disable'), sg.Button('Reboot')] ]

    self.window = sg.Window(self.title, self.layout)

    self.help_text = '''Warning! You can break stuff if you are reckless. Do not remove packages if you don't know what they do.
Uninstallations are reversible via adb, and a log is kept of uninstalled packages in case you need to revert.

To use:

1. Ensure USB Debugging is enabled on your device.
2. Ensure ADB is available on your env path
3. Connect the device and verify connection with \'adb devices\'.
4. Press \'Connect\' button.


This software is FLOSS provided under the MIT License.

Version 2.3
'''

  def load_pkgs(self):
    print('Attempting to load packages...')
    command = 'adb shell cmd package list packages --user 0'
    package_list = os.popen(command).read().replace('package:','').strip().split()
    package_list = [p for p in package_list if values['-QUERY-'] in p]
    print('[+] ' + str(len(package_list)) + ' Packages Found')
    package_list.insert(0,'SELECT PACKAGE(S)')
    self.window['-LIST-'].update(package_list)

  def log_uninstall(pkg_name):
    with open('uninst.log', 'a') as f:
      f.write('%s\n' % pkg_name)

  def log_freeze(pkg_name):
    with open('freeze.log', 'a') as f:
      f.write('%s\n' % pkg_name)

  def reboot(self):
      os.popen('adb reboot').read()
      print('[+] Requesting reboot...')

  def uninstall(self):
    for p in values['-LIST-']:
      if not p.startswith('SELECT P'):
        uninstall_command = 'adb shell pm uninstall -k --user 0 ' + p
        print('Running "' + uninstall_command + '"...')
        self.window['-OUT-'].update()
        result = os.popen(uninstall_command).read()
        print('[+] ' + result)
        PackageShark.log_uninstall(p)
      self.load_pkgs()

  def freeze(self):
    for p in values['-LIST-']:
      if not p.startswith('SELECT P'):
        command = 'adb shell cmd appops set %s RUN_IN_BACKGROUND ignore' % p
        print('Running "' + command + '"...')
        self.window['-OUT-'].update()
        result = os.popen(command).read()
        if not result:
            result = 'Success'
        print('[+] ' + result)
        PackageShark.log_freeze(p)
      self.load_pkgs()

  def disable(self):
    for p in values['-LIST-']:
      if not p.startswith('SELECT P'):
        command = 'adb shell pm disable-user %s' % p
        print('Running "' + command + '"...')
        self.window['-OUT-'].update()
        result = os.popen(command).read()
        if not result:
            result = 'Success'
        print('[+] ' + result)
        PackageShark.log_freeze(p)
      self.load_pkgs()

  def web_search(self):
    for p in values['-LIST-']:
      if not p.startswith('SELECT P'):
        query = urllib.parse.quote_plus(p)
        url = self.base_query_url + query
        webbrowser.open_new_tab(url)

  def show_help(self):
    sg.Popup('Help', self.help_text)

if __name__ == '__main__':
  ps = PackageShark() 

  # Event Loop
  while True:             
    event, values = ps.window.Read()
    if event in (None, 'Cancel'):
      break

    if event in ('Connect', '  Filter '):
      ps.load_pkgs()

    if event == 'Remove':
      ps.uninstall()

    if event == ' Freeze ':
      ps.freeze()

    if event == 'Disable':
      ps.disable()

    if event == 'Lookup':
      ps.web_search()

    if event == 'Exit':
      ps.window.Close()

    if event == 'Help':
      ps.show_help()

    if event == 'Reboot':
      ps.reboot()

ps.window.Close()
