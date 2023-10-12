#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Project Title: FGML (Filegame Markup Language)
# Description: An extension to HTML that lets you pack web games into single files.

import os,sys,shutil,zipfile,base64,random,math,subprocess,platform,re,requests

# Tags: <source-[url]> <-- gets the source code from a url and bases64 encodes it into a data uri

MIMETYPES = {
    "html": "text/html",
    "js": "text/javascript",
    "css": "text/css",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "ico": "image/x-icon",
    "txt": "text/plain",
    "mp3": "audio/mpeg"
}

class FGMLParser():
    def __init__(self,file):
        self.file = file
    
    def parse(self):
        self.file = self.file.replace("\r","")
        self.file = self.file.replace("\t","")
        self.file = self.file.replace("\n", "")
        
        # Parse <source-[url]> tags
        self.file = re.sub(r"<source-(.+?)>", self.get_source, self.file)

        # Parse <include-[url]> tags
        self.file = re.sub(r"<include-(.+?)>", self.get_include, self.file)

        # Parse <metaclone-[url]> tags (clones the <title> and favicon)
        self.file = re.sub(r"<metaclone-(.+?)>", self.get_metaclone, self.file)

    def get_source(self, match):
        url = match.group(1)
        mime = url.split(".")[-1]
        r = requests.get(url)
        if r.status_code == 200:
            return f"data:{mime};base64," + base64.b64encode(r.text.encode("utf-8")).decode("utf-8")
        else:
            return "<!-- Error: Unable to get source from " + url + " -->"
    
    def get_include(self, match):
        url = match.group(1)
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        else:
            return "<!-- Error: Unable to include " + url + " -->"
    
    def get_metaclone(self, match):
        url = match.group(1)
        r = requests.get(url)
        if r.status_code == 200:
            title = re.search(r"<title>(.+?)</title>", r.text)
            favicon = re.search(r"<link rel=\"icon\" href=\"(.+?)\" />", r.text)
            if title:
                title = title.group(1)
                return f"<title>{title}</title>\n<link rel=\"icon\" href=\"data:image/x-icon;base64," + base64.b64encode(requests.get(favicon.group(1)).content).decode("utf-8") + "\" />"
            else:
                return "<!-- Error: Unable to clone meta from " + url + " -->"
        else:
            return "<!-- Error: Unable to clone meta from " + url + " -->"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: builder.py [input file] [output file]")
        sys.exit(1)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        if not os.path.exists(input_file):
            print("Error: Input file does not exist.")
            sys.exit(1)
        else:
            with open(input_file, "r") as f:
                parser = FGMLParser(f.read())
                parser.parse()
                with open(output_file, "w") as f:
                    f.write(parser.file)
                    print("Done!")
                    sys.exit(0)