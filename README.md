# pyPacker
A python script for sprite sheets.

NOTE: this project is depreciated and will no longer be maintained! Instead check out my new packer, [nPacker](https://github.com/austin0209/npacker). It's pretty much the same thing, but faster, better, and written in node.js.

## Usage
usage:  python pypacker.py <path to image folder> [optional params]
availiable parameters:
        {-h --help}:
                open this dialogue
        {-o --output} <path to directory>:
                set folder to output to, must be an existing directory.
                default: current working directory.
        {-f --filename} <name>:
                set filename of outputs (filename.png, filename.json). do not include the file extension here.
                default: "result".
        {-b --border} <integer value>:
                set space between each sprite.
                default: 0
        {-nt --notrim}:
                if used, transparent padding will not be trimmed. can be useful if the script is too slow.
