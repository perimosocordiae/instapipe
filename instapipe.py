#!/usr/bin/python
'''
Insta-pipe: A tool for rapid development of complicated shell commands.
'''
from __future__ import print_function, unicode_literals
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from subprocess import Popen, PIPE, STDOUT


def main():
  SHELL = os.environ.get('SHELL', '/bin/bash')
  ap = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
  ap.add_argument('--instant', action='store_true',
                  help='Run the input command on every keystroke.')
  ap.add_argument('--input-lines', type=int, default=1, metavar='N',
                  help='Number of lines for input pane')
  ap.add_argument('--input-deco', default='frame',
                  choices=('none', 'underline', 'frame'),
                  help='Decoration for input pane')
  ap.add_argument('--shell', default=SHELL, help='Shell to run commands with.')
  ap.add_argument('--display', default='best', choices=('best', 'pt', 'curses'),
                  help='Display backend to use. "best" uses pt if available.')
  args, init_cmd = ap.parse_known_args()

  def run_input(line, out_len):
    if not line:
      return b'No input.', 0
    cmd = [args.shell, '-o', 'pipefail', '-c', '%s|head -n%d' % (line, out_len)]
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    try:
      result, _ = p.communicate()
    except KeyboardInterrupt:
      result = b'Killed by user.'
    return result, p.returncode

  if args.display == 'best':
    try:
      from ipipe_pt import instapipe
    except ImportError:
      from ipipe_curses import instapipe
  elif args.display == 'pt':
    from ipipe_pt import instapipe
  else:
    from ipipe_curses import instapipe

  final_cmd = instapipe(run_input, ' '.join(init_cmd), instant=args.instant,
                        input_lines=args.input_lines,
                        input_deco=args.input_deco)

  if final_cmd:
    # TODO: make this easier to use in the user's shell
    print(final_cmd)


if __name__ == '__main__':
  main()
