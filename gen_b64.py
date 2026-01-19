import base64

cmd_startup = 'Get-WinEvent -LogName Security -FilterXPath "*[System[(EventID=4624 or EventID=4625 or EventID=4647)]]" -MaxEvents 1 -ErrorAction SilentlyContinue | Select-Object RecordId | ConvertTo-Json'
cmd_poll = 'Get-WinEvent -LogName Security -FilterXPath "*[System[(EventID=4624 or EventID=4625 or EventID=4647)]]" -MaxEvents 10 -ErrorAction SilentlyContinue | Select-Object RecordId, Id, Message, TimeCreated | ConvertTo-Json'

print("STARTUP_B64:")
print(base64.b64encode(cmd_startup.encode('utf-16le')).decode('utf-8'))
print("POLL_B64:")
print(base64.b64encode(cmd_poll.encode('utf-16le')).decode('utf-8'))
