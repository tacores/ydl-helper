import unittest
import ydl_helper

setting = {'download_playlists' : []}
filenames = [[], []]
platform = 'darwin'

class SettingStub(ydl_helper.SettingProvider):
    def get_download_settings(self):
        return setting
    def save_download_settings(self, settings):
        self.arg = settings
    def get_save_arg(self):
        return self.arg

class FsStub(ydl_helper.FileSystemProvider):
    def __init__(self):
        self.index = 0
    def get_filenames_pettern_matched(self, pettern):
        self.arg = pettern
        self.index += 1
        return filenames[self.index - 1]
    def get_pettern_arg(self):
        return self.arg

class SubProcessSpy(ydl_helper.SubProcessCaller):
    def __init__(self):
        self.times = 0
    def call(self, args):
        self.times += 1
        self.args = args
    def get_args(self):
        return self.args
    def get_call_times(self):
        return self.times

class SystemStub(ydl_helper.SystemProvider):
    def get_platform(self):
        return platform

class YdlHelperTest(unittest.TestCase):
    def setUp(self):
        global setting, filenames, args, platform
        setting = {'download_playlist' : []}
        filenames = [[], []]
        platform = 'darwin'

        self.setting_stub = SettingStub()
        self.fs_stub = FsStub()
        self.subp_spy = SubProcessSpy()
        self.sys_stub = SystemStub()
        self.sut = ydl_helper.YdlPlaylistHelper(self.setting_stub, self.fs_stub,
                                                self.subp_spy, self.sys_stub)

    def test_subprocess_call_with_args(self):
        global setting
        setting = {"download_playlists" : [{\
                   "url" : "https://ydl-url",\
                   "--playlist-start" : 10,\
                   "file_name_pettern" : "*pettern*"\
        }]}

        self.sut.download_all_playlists()

        expect = ['youtube-dl', '--playlist-start', '10', 'https://ydl-url']
        self.assertEqual(expect, self.subp_spy.get_args())

    def test_subprocess_call_with_args_windows_exe(self):
        global setting, platform
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern*"\
        }]}
        platform = 'win32'    # Windows

        self.sut.download_all_playlists()

        expect = ['youtube-dl.exe', '--playlist-start', '10', 'https://ydl-url']
        self.assertEqual(expect, self.subp_spy.get_args())

    def test_subprocess_call_with_any_args(self):
        global setting
        setting = {"download_playlists" :[{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern*",\
            "-f" : "140"}]}    # An user want to download as m4a format.

        self.sut.download_all_playlists()

        expect = ['youtube-dl', '--playlist-start', '10', '-f', '140', 'https://ydl-url']
        self.assertEqual(expect, self.subp_spy.get_args())

    def test_subprocess_call_empty_value_option(self):
        global setting
        setting = {"download_playlists" :[{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern*",\
            "-c" : ""\
        }]}

        self.sut.download_all_playlists()

        expect = ['youtube-dl', '--playlist-start', '10', '-c', 'https://ydl-url']
        self.assertEqual(expect, self.subp_spy.get_args())

    def test_save_start_position_2files_downloaded(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*name*"\
        }]}
        filenames = [['videoname1', 'nextname2'],\
                     ['videoname1', 'nextname2', 'downname3', 'loadname4']]

        self.sut.download_all_playlists()

        expect = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 12,\
            "file_name_pettern" : "*name*"\
        }]}
        self.assertEqual(expect, self.setting_stub.get_save_arg())

    def test_not_count_uncomplete_file(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*name*"\
        }]}
        filenames = [['videoname1', 'nextname2'],\
                     ['videoname1', 'nextname2', 'downname3', 'loadname4.part']] # .part

        self.sut.download_all_playlists()

        expect = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 11,\
            "file_name_pettern" : "*name*"\
        }]}
        self.assertEqual(expect, self.setting_stub.get_save_arg())

    def test_get_filenames_pettern_matched(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern*"\
        }]}

        self.sut.download_all_playlists()

        self.assertEqual('*pettern*', self.fs_stub.get_pettern_arg())

    def test_run_ydl_2times(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url-1",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern-1*"\
            }, {\
            "url" : "https://ydl-url-2",\
            "--playlist-start" : 20,\
            "file_name_pettern" : "*pettern-2*"\
        }]}
        filenames = [[], [], [], []]

        self.sut.download_all_playlists()

        self.assertEqual(2, self.subp_spy.get_call_times())

    def test_not_run_ydl_when_url_is_not_set(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern-1*"\
        }]}

        self.sut.download_all_playlists()

        self.assertEqual(0, self.subp_spy.get_call_times())

    def test_run_ydl_only_once(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            # url is not set.
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern-1*"\
            }, {\
            "url" : "https://ydl-url-2",\
            "--playlist-start" : 20,\
            "file_name_pettern" : "*pettern-2*"\
        }]}
        filenames = [[], [], [], []]

        self.sut.download_all_playlists()

        expect = ['youtube-dl', '--playlist-start', '20', 'https://ydl-url-2']
        self.assertEqual(expect, self.subp_spy.get_args())
        self.assertEqual(1, self.subp_spy.get_call_times())

    def test_save_playliststart_as_integer_even_if_set_as_string(self):
        global setting, filenames
        setting = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : "10",\
            "file_name_pettern" : "*name*"\
        }]}
        filenames = [['videoname1', 'nextname2'],\
                     ['videoname1', 'nextname2', 'downname3', 'loadname4']]

        self.sut.download_all_playlists()

        expect = {"download_playlists" : [{\
            "url" : "https://ydl-url",\
            "--playlist-start" : 12,\
            "file_name_pettern" : "*name*"\
        }]}
        self.assertEqual(expect, self.setting_stub.get_save_arg())

    def test_ignore_comment(self):
        global setting
        setting = {"download_playlists" : [{\
            "comment" : "free description",\
            "url" : "https://ydl-url",\
            "--playlist-start" : 10,\
            "file_name_pettern" : "*pettern*"\
        }]}

        self.sut.download_all_playlists()

        expect = ['youtube-dl', '--playlist-start', '10', 'https://ydl-url']
        self.assertEqual(expect, self.subp_spy.get_args())

if __name__ == '__main__':
    unittest.main()

