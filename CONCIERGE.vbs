Set WshShell = CreateObject("WScript.Shell")
' Launch the agent without any console window
WshShell.Run "pythonw.exe web_ui.py", 0
' The browser will open automatically via the python script
Set WshShell = Nothing
