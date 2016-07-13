# Insta-pipe

Quickly iterate on complex shell commands.

Edit commands in the top pane, and each time you press enter the
first n lines will appear in the preview pane.

## TODO

 - Avoid blocking until the command completes, by reading the `Popen` pipe
   line by line. (Will require a working `flush`).
 - Do some basic caching to avoid recomputing repeated results.
 - If the user exits with ctrl-D, insert the final command into their
   shell session somehow. (Paste buffer?) For now, we just print it.

## Known Issues

 - all backends
   * terminal color escape codes aren't supported in the output frame.

 - `curses` backend
   * If you press enter with an empty input pane, instapipe exits.
   * Instant mode isn't supported.
