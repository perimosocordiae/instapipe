# Insta-pipe

Quickly iterate on complex shell commands.

Edit commands in the top pane, and each time you press enter the
first n lines will appear in the preview pane.

## TODO

 - Avoid blocking until the command completes, by using `Popen`
   and reading the result line by line. (Will require a working `flush`).
 - Add an 'instant' mode, where commands are sent on every character.
 - Do some basic caching to avoid recomputing repeated results.
 - If the user exits with ctrl-D, insert the final command into their
   shell session somehow. (Paste buffer?) For now, we just print it.
 - Prevent backspacing past the start of input.

## Known Issues

 - If you press enter with an empty input pane, instapipe exits.

