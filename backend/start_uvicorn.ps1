$env:DEBUG = $null
$env:PYTHONPATH = "C:\Projects\dav-agri\backend"
$s = New-Object System.Diagnostics.ProcessStartInfo
$s.FileName='py'
$s.Arguments='-m uvicorn main:app --host 127.0.0.1 --port 8000'
$s.RedirectStandardOutput='C:\Projects\dav-agri\backend\uvicorn.log'
$s.RedirectStandardError='C:\Projects\dav-agri\backend\uvicorn.log'
$s.UseShellExecute=$false
$s.CreateNoWindow=$true
[System.Diagnostics.Process]::Start($s) | Out-Null
