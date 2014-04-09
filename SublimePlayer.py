# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import subprocess
import threading


class RunAsync(threading.Thread):
    def __init__(self, cb):
        self.cb = cb
        threading.Thread.__init__(self)

    def run(self):
        self.cb()

def run_async(cb):
    res = RunAsync(cb)
    res.start()
    return res

class Player():
    url = None
    popen = None
    _enabled = False
    last_view = None

    def __init__(self, url=None):
        self.url = url

    def _play(self):
        self.popen = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", self.url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = self.popen.communicate()

    def play(self):
        if self.url is None:
            return
        self._enabled = True
        self.load_to_view(sublime.active_window().active_view())
        run_async(self._play)

    def stop(self):
        if self._enabled:
            self._enabled = False
            self.unload_view()
            self.popen.kill()
            self.popen = None

    def set_url(self, url):
        was_enabled = self._enabled
        self.stop()
        self.url = url
        if was_enabled:
            self.play()

    def enabled(self):
        return self._enabled

    def unload_view(self):
        if self.last_view is not None:
            self.last_view.erase_status("SublimePlayer")
            self.last_view = None

    def load_to_view(self, view):
        self.unload_view()
        if not self._enabled:
            return
        view.set_status("SublimePlayer", "Playing: %s" % (self.url))
        self.last_view = view



player = Player()

class SublimePlayerPlay(sublime_plugin.ApplicationCommand):
    def run(self):
        player.play()

    def is_enabled(self):
        return not player.enabled()

class SublimePlayerStop(sublime_plugin.ApplicationCommand):
    def run(self):
        player.stop()

    def is_enabled(self):
        return player.enabled()

class SublimePlayerSetUrl(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Select file:", "", self.set_url, None, None)
        
    def set_url(self, url):
        player.set_url(url)

def plugin_unloaded():
    player.stop()
