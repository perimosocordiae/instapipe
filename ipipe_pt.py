from __future__ import print_function, unicode_literals
from prompt_toolkit import Application, CommandLineInterface
from prompt_toolkit.layout.controls import FillControl
from prompt_toolkit.shortcuts import (
    Buffer, BufferControl, DEFAULT_BUFFER, KeyBindingManager, Keys, Window,
    HSplit, Token, LayoutDimension as D, create_eventloop)
from traceback import print_exc


def instapipe(runner, init_cmd, instant=False, input_lines=1, input_deco=''):
  layout = HSplit([
      Window(content=BufferControl(buffer_name=DEFAULT_BUFFER),
             height=D.exact(1)),
      Window(content=FillControl('-', token=Token.Line), height=D.exact(1)),
      Window(content=BufferControl(buffer_name='OUTPUT'))
  ])
  buffers, keybinds = _setup_buffers(runner, layout.children[-1], instant)
  app = Application(layout=layout, buffers=buffers, mouse_support=True,
                    key_bindings_registry=keybinds, use_alternate_screen=True)

  eventloop = create_eventloop()
  final_cmd = ''
  try:
    final_cmd = CommandLineInterface(application=app, eventloop=eventloop).run()
  except:
    print_exc()
  finally:
    eventloop.close()
    return final_cmd


def _setup_buffers(runner, output_window, instant_mode):
  input_buffer = Buffer(is_multiline=False)
  output_buffer = Buffer(is_multiline=True)

  def _run(_):
    n_head = output_window.render_info.window_height
    result, returncode = runner(input_buffer.text, n_head)
    output_buffer.text = unicode(result, 'utf8')

  reg = KeyBindingManager().registry
  if instant_mode:
    # run the command on every edit
    input_buffer.on_text_changed += _run
  else:
    # run after each carriage return
    reg.add_binding(Keys.ControlJ, eager=True)(_run)

  @reg.add_binding(Keys.ControlC, eager=True)
  @reg.add_binding(Keys.ControlQ, eager=True)
  def _exit(event):
    event.cli.set_return_value(None)

  @reg.add_binding(Keys.ControlD, eager=True)
  def _exit_with_value(event):
    event.cli.set_return_value(input_buffer.text)

  bufmap = {DEFAULT_BUFFER: input_buffer, 'OUTPUT': output_buffer}
  return bufmap, reg
