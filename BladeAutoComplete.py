import sublime_plugin
import sublime
from os import path, walk
import fnmatch
import re


class BladeAutoComplete(sublime_plugin.EventListener):
    files = []
    blade_files = []

    def load_blade_files(self, view):
        self.blade_files = []

        views_folder = ''.join([
            view.window().folders()[0],
            path.sep,
            path.join('resources', 'views'),
            path.sep])

        matches = []
        for root, dirnames, filenames in walk(views_folder):
            for filename in fnmatch.filter(filenames, '*.blade.php'):
                matches.append(path.join(root, filename))
        self.files = matches

        for file in self.files:
            file_name = file.replace(views_folder, '')
            file_append_text = file_name.replace('.blade.php', '').replace(path.sep, '.')
            t = ('{} \tBlade Autocomplete'.format(file_name), file_append_text)
            self.blade_files.append(t)

    def find_yields_in_layout(self, layout):
        layout_path = None
        for file in self.files:
            if layout.replace('.', path.sep) in file:
                layout_path = file

        if layout_path is None:
            return []

        with open(layout_path, 'r') as file:
            content = file.read()
            file.close()
        matches = re.findall(r'\@yield\((?:\'|\")(.*?)(?:\'|\")\)', content, re.M | re.I)
        return matches

    def on_query_completions(self, view, prefix, locations):
        self.load_blade_files(view)
        line = view.substr(view.line(view.sel()[0])).strip()

        if line.startswith('@extends'):
            return self.blade_files

        elif line.startswith('@section'):
            # place search cursor one word back
            cursor = locations[0] - len(prefix) - 1

            body = view.substr(sublime.Region(0, cursor))

            matches = re.match(r'\@extends\((?:\'|\")(.*?)(?:\'|\")\)', body, re.M | re.I)
            if not matches:
                return []

            layout = matches.group(1)
            layout_yields = self.find_yields_in_layout(layout)

            return [('{} \tin {}'.format(section, layout), section) for section in layout_yields]

        return None
