#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script makes more useful downloading youtube playlists using the youtube-dl.
See https://github.com/tacores/ydl-helper"""

import codecs
import re
import glob
import json
import subprocess
import sys

class YdlPlaylistHelper(object):
    """Main class of this script"""

    def __init__(self, setting_provider, file_system_provider,
                 subprocess_caller, system_provider):
        self.setting_provider = setting_provider
        self.file_system_provider = file_system_provider
        self.subprocess_caller = subprocess_caller
        self.system_provider = system_provider
        self.__any_option_dict = {}

    def download_all_playlists(self):
        """Main class of this script"""
        settings = self.setting_provider.get_download_settings()
        for setting in settings["download_playlists"]:
            try:
                self.__parse_setting(setting)
                before = self.__count_current_files(setting)
                self.__download_one_playlist(setting)
                after = self.__count_current_files(setting)
                self.__update_start_position(setting, after - before)
            except KeyError as key_error:
                print(key_error, 'is not set.')
        self.setting_provider.save_download_settings(settings)

    def __parse_setting(self, setting):
        """parse setting of a plyalist"""
        # throw exception if necessary options are deleted.
        setting["url"]
        setting["--playlist-start"]
        setting["file_name_pettern"]

        self.__any_option_dict = {}
        for key in setting.keys():
            if self.__is_optional_setting(key):
                self.__any_option_dict[key] = setting[key]

    def __download_one_playlist(self, setting):
        """download files in a plyalist"""
        args = self.__generate_subprocess_args(setting)
        self.subprocess_caller.call(args)

    def __generate_subprocess_args(self, setting):
        """generate arguments passed to youtube-dl"""
        if self.system_provider.get_platform() == 'win32':
            args = ['youtube-dl.exe']
        else:
            args = ['youtube-dl']
        args.extend(['--playlist-start', str(setting['--playlist-start'])])
        for k, value in self.__any_option_dict.iteritems():
            if value != "":
                args.extend([k, value])
            else:
                args.append(k)
        args.append(setting['url'])
        return args

    def __count_current_files(self, setting):
        """how many files of the playlist are there in a current directory now?"""
        count = 0
        file_paths = self.file_system_provider.\
                get_filenames_pettern_matched(setting['file_name_pettern'])
        for file_path in file_paths:
            match = re.search(r"\.part$", file_path)
            if match is None:
                count += 1
        return count

    @staticmethod
    def __is_optional_setting(key):
        """is the key optional?"""
        if key in ["url", "--playlist-start", "file_name_pettern", "comment"]:
            return False
        else:
            return True

    @staticmethod
    def __update_start_position(setting, added):
        """update --playlist-start value in memory"""
        old = int(setting["--playlist-start"])
        setting["--playlist-start"] = old + added

class SettingProvider(object):
    """provide information about download settings an user edits"""
    @staticmethod
    def get_download_settings():
        """provide settings"""
        with codecs.open('ydl_helper_list.json', 'r', 'utf-8') as setting_file:
            setting_dict = json.load(setting_file)
        return setting_dict

    @staticmethod
    def save_download_settings(settings):
        """save new settings"""
        with codecs.open('ydl_helper_list.json', 'w', 'utf-8') as setting_file:
            json.dump(settings, setting_file, ensure_ascii=False, indent=4)

class FileSystemProvider(object):
    """provide information about the file system"""
    @staticmethod
    def get_filenames_pettern_matched(pettern):
        """how many files that are matched with the pettern?"""
        return glob.glob(pettern)

class SubProcessCaller(object):
    """wrapper of the subprocess class"""
    @staticmethod
    def call(args):
        """execute the youtube-dl"""
        subprocess.call(args, shell=True)

class SystemProvider(object):
    """provide information about the system"""
    @staticmethod
    def get_platform():
        """what platform this script runs on?"""
        return sys.platform

def main():
    """main"""
    helper = YdlPlaylistHelper(SettingProvider(), FileSystemProvider(),
                               SubProcessCaller(), SystemProvider())
    helper.download_all_playlists()

if __name__ == '__main__':
    main()

