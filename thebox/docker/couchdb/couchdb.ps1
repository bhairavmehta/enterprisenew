# Powershell

# Script to start CouchDB instance
# Ported from following example:
#   https://github.com/frodenas/docker-couchdb/tree/master/scripts

# Initialize first run
if (Test-Path c:\firstrun.txt) {
  Write-Host "Invoke first-run script ..."
  Invoke-Expression -Command $PSScriptRoot\firstrun.ps1 -ErrorAction Stop -WarningAction Stop
}

# Start CouchDB
Write-Host "Starting CouchDB ..."
$cdbsvc = Get-Service "Apache CouchDB"
if ($cdbsvc.Status -ne "Running") {
  Start-Service -Name "Apache CouchDB"
  $timeout = (Get-Date).AddSeconds(300)
  while ((Get-Service "Apache CouchDB").Status -ne "Running") {
    if ((Get-Date) -le $timeout) {
      Write-Verbose "."
      Start-Sleep -Seconds 5
    }
    else {
      throw [System.ApplicationException] "Cannot start Apache CouchDB"
    }
  }
}

# Successfully started, wait for it to terminate ...
while ((Get-Service "Apache CouchDB").Status -eq "Running") {
  Start-Sleep -Seconds 10
}
