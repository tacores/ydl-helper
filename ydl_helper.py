#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import glob
import json
import subprocess
import sys

class YdlPlaylistHelper(object):

    def __init__(self):
        pass

    def download_all_playlists(self):
        settings = helper.__get_donwload_setting()
        for setting in settings["download_playlists"]:
            self.__parse_setting(setting)
            before = self.__count_current_files()
            self.__download_one_playlist(setting)
            after = self.__count_current_files()
            self.__update_start_position(setting, after - before)
        self.__write_download_setting(settings)

    def __get_donwload_setting(self):
        with codecs.open('ydl_helper_list.json', 'r', 'utf-8') as f:
            setting_dict = json.load(f)
        return setting_dict

    def __parse_setting(self, setting):
        self.__url = setting["url"]
        self.__start_from = setting["start_from"]
        self.__file_format = setting["file_format"]
        self.__name_pettern = setting["file_name_pettern"]

    def __download_one_playlist(self, setting):
        if sys.platform == 'win32':
            args = ['youtube-dl.exe']
        else:
            args = ['youtube-dl']
        args.extend(['--playlist-start', str(self.__start_from)])
        if self.__file_format != '':
            args.extend(['-f', self.__file_format])
        args.append(self.__url)
        subprocess.call(args, shell=True)

    def __count_current_files(self):
        count = 0
        file_paths = glob.glob(self.__name_pettern)
        for file_path in file_paths:
            match = re.search(r"\.part$", file_path)
            if match is None:
                count += 1
                print file_path + ' matched.'
        return count

    def __update_start_position(self, setting, added):
        setting["start_from"] += added

    def __write_download_setting(self, settings):
        with codecs.open('ydl_helper_list.json', 'w', 'utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

helper = YdlPlaylistHelper()
helper.download_all_playlists()

