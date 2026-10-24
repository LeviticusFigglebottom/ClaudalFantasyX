# Keeps a Windows GPU worker's system and display awake while benchmarks and captures run (pc-gpu
# environment). If the display sleeps, Vulkan swapchain creation fails and Godot cannot open a window.
# Usage: powershell -ExecutionPolicy Bypass -File tools/dev/keep_display_on.ps1 [-Hours 10]
param([double]$Hours = 10)
Add-Type -Name P -Namespace W -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
# ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED, renewed every 30 s.
$end = (Get-Date).AddHours($Hours)
while ((Get-Date) -lt $end) { [W.P]::SetThreadExecutionState(0x80000003) | Out-Null; Start-Sleep -Seconds 30 }
