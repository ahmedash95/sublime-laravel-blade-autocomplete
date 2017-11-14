import sublime_plugin
import sublime
import os
import fnmatch
import re

class BladeAutoComplete(sublime_plugin.EventListener):
    
    files = []
    blade_files = []
    
    def load_blade_files(self,view):
        self.blade_files = []
        path = view.window().folders()[0] + "/resources/views/"
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.blade.php'):
                matches.append(os.path.join(root, filename))
        self.files = matches

        for file in self.files:
            file_name = file.replace(path,'')
            file_append_text = file_name.replace('.blade.php','').replace('/','.')
            t = ("%s \tBlade Autocomplete" % file_name, file_append_text)
            self.blade_files.append(t)

    def find_yields_in_layout(self,layout):
        layout_path = None
        for file in self.files:
            if layout.replace('.','/') in file:
                layout_path = file
        
        if layout_path == None: return []

        file = open(layout_path,"r")
        content = file.read()
        file.close()
        matches = re.findall( r'\@yield\((?:\'|\")(.*?)(?:\'|\")\)', content, re.M|re.I)
        return matches

    def on_query_completions(self, view, prefix, locations):
        self.load_blade_files(view)
        line = view.substr(view.line(view.sel()[0])).strip()

        if line.startswith('@extends'):
            # Cursor is inside a quoted attribute
            # Now check if we are inside the class attribute

            # max search size
            LIMIT  = 250

            # place search cursor one word back
            cursor = locations[0] - len(prefix) - 1

            # dont start with negative value
            start  = max(0, cursor - LIMIT - len(prefix))

            # get part of buffer
            line   = view.substr(sublime.Region(start, cursor))

            # split attributes
            parts  = line.split('=')

            # is the last typed attribute a class attribute?
            return self.blade_files

        elif line.startswith("@section"):
            # place search cursor one word back
            cursor = locations[0] - len(prefix) - 1
            body = view.substr(sublime.Region(0, cursor))
            matches = re.match( r'\@extends\((?:\'|\")(.*?)(?:\'|\")\)', body, re.M|re.I)
            if not matches: return []
            
            layout = matches.group(1)
            layout_yields = self.find_yields_in_layout(layout)
            return [("%s \tin %s" % (s,layout), s) for s in layout_yields]

        else:
            return []
