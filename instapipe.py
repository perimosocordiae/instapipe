#!/usr/bin/python
'''
Insta-pipe: A tool for rapid development of complicated shell commands.

See the simple, bash-based prototype for an idea of how it works.
'''
import cmd
import curses
import subprocess
from argparse import ArgumentParser
from curses import ascii, textpad, wrapper
from subprocess import check_output, CalledProcessError


class InstaPipe(cmd.Cmd):
  def __init__(self, txt_box, out_win):
    cmd.Cmd.__init__(self, stdin=TextpadFile(txt_box),
                           stdout=CursesFile(out_win))
    self.prompt = ''  # No prompt
    self.use_rawinput = False  # Use the provided stdin/stdout
    self.last_cmd = ''  # The last successful command

  def default(self, line):
    cmd = line + '|head'
    try:
      result = check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except CalledProcessError as e:
      self.stdout.write(str(e))
    else:
      self.stdout.write(result)
      self.last_cmd = line

  def emptyline(self):
    return False

  def do_EOF(self, line):
    return True

  def postcmd(self, stop, line):
    curses.doupdate()
    return stop


class TextpadFile(object):
  '''Read-only file-like object that gets text from a textpad.'''
  def __init__(self, pad):
    self.txtpad = pad
    self.last_pos = 0,0

    def validator(ch):
      # Convert newlines (enter key) to terminators (ctrl-G)
      if ch in (ascii.BEL, ascii.NL, ascii.CR):
        self.last_pos = pad.win.getyx()
        return ascii.BEL
      # Make EOTs (ctrl-D) send the ctrl-D to the repl
      if ch == ascii.EOT:
        pad.win.erase()
        curses.ungetch(ch)
        return ascii.BEL
      return ch
    self.validator = validator

  def readline(self):
    text = self.txtpad.edit(self.validator)
    # set the cursor where it was before the submission
    self.txtpad.win.move(*self.last_pos)
    return text


class CursesFile(object):
  '''Write-only file-like object that writes text to a curses window.'''
  def __init__(self, win):
    self.win = win

  def write(self, txt):
    if not txt:
      return
    self.win.erase()
    self.win.addstr(0, 0, txt)
    self.win.noutrefresh()

  def flush(self):
    pass


def make_textbox(scr, h, w, y, x, deco, init_txt, text_color, deco_color):
  win_x,win_y,win_w,win_h = x,y,w,h
  if deco == 'frame':
    win_x += 1
    win_y += 1
    h += 2
    win_w -= 2
  elif deco == 'underline':
    h += 1
  win = curses.newwin(win_h, win_w, win_y, win_x)
  box = textpad.Textbox(win, insert_mode=True)
  if deco == 'frame':
    scr.attron(deco_color)
    textpad.rectangle(scr, y, x, y+h-1, x+w-1)
    scr.attroff(deco_color)
  elif deco == 'underline':
    scr.hline(y+h-1, x, curses.ACS_HLINE, w, deco_color)
  win.attron(text_color)
  scr.move(win_y, win_x)
  win.noutrefresh()
  win.addstr(0, 0, init_txt)
  return box, h


def make_gui(scr, txt_h, deco, init_cmd, text_color, deco_color):
  scr_h, scr_w = scr.getmaxyx()
  txt_box, tot_h = make_textbox(scr, txt_h, scr_w, 0, 0, deco, init_cmd,
                                text_color, deco_color)
  out_win = curses.newwin(scr_h-tot_h, scr_w, tot_h, 0)
  out_win.noutrefresh()
  return txt_box, out_win


def gui_main(scr, init_cmd, txt_h, deco):
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  txt_box, out_win = make_gui(scr, txt_h, deco, init_cmd,
                              curses.color_pair(0),
                              curses.color_pair(1))
  repl = InstaPipe(txt_box, out_win)
  scr.refresh()
  try:
    repl.cmdloop()
  except KeyboardInterrupt:
    return
  return repl.last_cmd


def main():
  ap = ArgumentParser()
  ap.add_argument('--input-lines', type=int, default=1, metavar='N',
                  help='Number of lines for input pane [%(default)s]')
  ap.add_argument('--input-deco', default='frame',
                  choices=('none', 'underline', 'frame'),
                  help='Decoration for input pane [%(default)s]')
  args, init_cmd = ap.parse_known_args()
  final_cmd = wrapper(gui_main, ' '.join(init_cmd), args.input_lines,
                      args.input_deco)
  if final_cmd:
    print final_cmd


if __name__ == '__main__':
  main()

