VS Code: Make Explorer (Folders) selected at startup and apply workspace settings to User settings

Follow these steps to apply the recommended settings to your User settings so Explorer (Folders) is preferred on launch.

1) Open VS Code User Settings (JSON)
   - Menu: File > Preferences > Settings (or Ctrl+,)
   - Click the Open Settings (JSON) icon in the top-right (the {} button)

2) Add the following snippet to your User settings JSON (merge with existing keys):

{
  "workbench.startupEditor": "none",
  "workbench.editor.enablePreview": false,
  "workbench.editor.enablePreviewFromQuickOpen": false,
  "explorer.openEditors.visible": 0
}

3) Save the file. These settings will apply to all workspaces on this machine.

4) Make Explorer the active view before closing VS Code
   - Press Ctrl+Shift+E to open Explorer, then close VS Code; it usually restores the last active view on startup.

5) If Source Control keeps stealing focus
   - Right-click the Source Control icon in the Activity Bar and choose "Hide" (or move it lower).

Notes
- A workspace-specific file was created at .vscode/settings.json in this repository (it may be gitignored). If you prefer workspace-only configuration, copy the snippet into that file instead of User settings.

Generated on: 2025-12-05T07:00:14.483Z
