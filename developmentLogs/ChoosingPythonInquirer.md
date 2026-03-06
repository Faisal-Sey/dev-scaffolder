# Python Inquirer Selection

I had two options

- InquirerPy - https://pypi.org/project/inquirerpy/
- inquirer - https://pypi.org/project/inquirer/

## InquirerPy had issues on Pycharm Windows

```
Traceback (most recent call last):
  File "D:\Codebase\Projects\template\scripts\scaffolder\scaffolder.py", line 12, in <module>
    result = prompt(questions)
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\InquirerPy\resolver.py", line 213, in prompt
    result[question_name] = question_mapping[question_type](
                            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        **args, **question
        ^^^^^^^^^^^^^^^^^^
    ).execute()
    ^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\InquirerPy\prompts\input.py", line 163, in __init__
    self._session = PromptSession(
                    ~~~~~~~~~~~~~^
        message=self._get_prompt_message,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<15 lines>...
        else None,
        ^^^^^^^^^^
    )
    ^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\shortcuts\prompt.py", line 483, in __init__
    self.app = self._create_application(editing_mode, erase_when_done)
               ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\shortcuts\prompt.py", line 744, in _create_application
    application: Application[_T] = Application(
                                   ~~~~~~~~~~~^
        layout=self.layout,
        ^^^^^^^^^^^^^^^^^^^
    ...<36 lines>...
        output=self._output,
        ^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\application\application.py", line 267, in __init__
    self.output = output or session.output
                            ^^^^^^^^^^^^^^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\application\current.py", line 67, in output
    self._output = create_output()
                   ~~~~~~~~~~~~~^^
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\output\defaults.py", line 91, in create_output
    return Win32Output(stdout, default_color_depth=color_depth_from_env)
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\output\win32.py", line 115, in __init__
    info = self.get_win32_screen_buffer_info()
  File "D:\Codebase\Projects\template\venv\Lib\site-packages\prompt_toolkit\output\win32.py", line 219, in get_win32_screen_buffer_info
    raise NoConsoleScreenBufferError
prompt_toolkit.output.win32.NoConsoleScreenBufferError: No Windows console found. Are you running cmd.exe?

```
### Which can be fixed using
https://stackoverflow.com/questions/63543251/no-windows-console-found-are-you-running-cmd-exe



### Inquirer
- Using the play button on Pycharm displays the first statement but not the rest
- Works fine in the terminal section