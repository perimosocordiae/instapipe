# Insta-pipe

Quickly iterate on complex shell commands.

Edit commands in the top pane, and each time you press enter the
first n lines will appear in the preview pane.

## TODO

 - Avoid blocking until the command completes, by using `Popen`
   and reading the result line by line. (Will require a working `flush`).
 - Instead of 10 lines, fill the preview pane dynamically.
 - Add an 'instant' mode, where commands are sent on every character.
 - Do some basic caching to avoid recomputing repeated results.
 - Allow new commands to interrupt running ones.
 - If the user exits with ctrl-D, insert the final command into their
   shell session somehow. (Paste buffer?) For now, we just print it.

## Known Issues

 - If you press enter with an empty input pane, instapipe exits.

