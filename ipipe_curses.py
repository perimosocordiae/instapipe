from __future__ import print_function, unicode_literals
import cmd
import curses
from curses import ascii, textpad, wrapper


def instapipe(runner, cmd, instant=False, input_lines=1, input_deco='frame'):
  if instant:
    raise ValueError('--instant mode not supported by the curses interface')
  return wrapper(gui_main, cmd, input_lines, input_deco, runner)


def gui_main(scr, init_cmd, txt_h, deco, runner):
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  gui_args = make_gui(scr, txt_h, deco, init_cmd, curses.color_pair(0),
                      curses.color_pair(1))
  repl = InstaPipe(runner, *gui_args)
  scr.refresh()

  if init_cmd:
    repl.default(init_cmd)

  try:
    repl.cmdloop()
  except KeyboardInterrupt:
    return
  return repl.last_cmd


class InstaPipe(cmd.Cmd):
  def __init__(self, runner, txt_box, out_win, out_lines):
    cmd.Cmd.__init__(self, stdin=TextpadFile(txt_box),
                     stdout=CursesFile(out_win))
    self.prompt = ''  # No prompt
    self.use_rawinput = False  # Use the provided stdin/stdout
    self.last_cmd = ''  # The last successful command
    self.runner = lambda line: runner(line, out_lines)

  def default(self, line):
    result, returncode = self.runner(line)
    self.stdout.write(result)

    if returncode == 0:
      # successful command, save the input line
      self.last_cmd = line
    elif not result:
      # failed command with no output, write an error message
      self.stdout.write("Command '%s' returned non-zero exit status %d" % (
                        line, returncode))

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
    self.last_pos = (0, 0)

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
    try:
      self.win.addstr(0, 0, txt)
    except curses.error:
      pass
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
  out_lines = scr_h - tot_h
  out_win = curses.newwin(out_lines, scr_w, tot_h, 0)
  out_win.noutrefresh()
  return txt_box, out_win, out_lines
