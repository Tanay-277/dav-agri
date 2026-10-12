$outFile = "C:\Projects\dav-agri\verify_result.txt"  
' | Out-File -FilePath $outFile -Encoding utf8 
$r = & curl.exe -m 5 -s -w "HTTP:%{http_code}" "http://127.0.0.1:8001/health"  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 http://127.0.0.1:8001/health`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
$r = & curl.exe -m 5 -s -w "HTTP:%{http_code}" "http://127.0.0.1:8001/otp_http"  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 http://127.0.0.1:8001/otp_http`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
$r = & curl.exe -m 5 -s -w "HTTP:%{http_code}" -X POST "http://127.0.0.1:8001/login" -H "Content-Type: application/json" -d "{\"phone\":\"9876543210\",\"password\":\"password123\"}"  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 -X POST http://127.0.0.1:8001/login -d phone=9876543210,password=password123`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
$TOKEN = ""  
if ($code -eq "200") {  
$TOKEN = ""  
if ($code -eq "200") {  
"  $data = $body | ConvertFrom-Json"  
"  $TOKEN = $data.access_token"  
"  if (-not $TOKEN) { $TOKEN = $data.token }"  
}  
if (-not $TOKEN) { $TOKEN = "" } 
$r = & curl.exe -m 5 -s -w "HTTP:%{http_code}" -X POST "http://127.0.0.1:8001/login" -H "Content-Type: application/json" -d "{\"phone\":\"9876543210\",\"password\":\"wrong\"}"  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 -X POST http://127.0.0.1:8001/login -d phone=9876543210,password=wrong`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
if ($TOKEN) {  
"  $r = & curl.exe -m 5 -s -w \"HTTP:%{http_code}\" -H \"Authorization: Bearer $TOKEN\" \"http://127.0.0.1:8001/crop-income?language=en\""  
} else { $r = "HTTP:000" }  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 -H \"Authorization: Bearer [token]\" http://127.0.0.1:8001/crop-income?language=en`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
if ($TOKEN) {  
"  $r = & curl.exe -m 5 -s -w \"HTTP:%{http_code}\" -H \"Authorization: Bearer $TOKEN\" \"http://127.0.0.1:8001/expenses/breakdown?language=en\""  
} else { $r = "HTTP:000" }  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 -H \"Authorization: Bearer [token]\" http://127.0.0.1:8001/expenses/breakdown?language=en`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
if ($TOKEN) {  
"  $r = & curl.exe -m 5 -s -w \"HTTP:%{http_code}\" -H \"Authorization: Bearer $TOKEN\" \"http://127.0.0.1:8001/weather/current?language=en\""  
} else { $r = "HTTP:000" }  
$code = $r -replace ".*HTTP:(\d+)$", "$1"  
$body = $r -replace "HTTP:\d+$", ""  
"$ curl.exe -m 5 -H \"Authorization: Bearer [token]\" http://127.0.0.1:8001/weather/current?language=en`n$body`nhttp=$code`n`n" | Out-File -FilePath $outFile -Append -Encoding utf8 
Write-Host "LIVE_VERIFY_WROTE_FILE" 
