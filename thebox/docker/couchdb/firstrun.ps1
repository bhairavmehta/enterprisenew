# Powershell

# Script to run once on first image boot
# Ported from following example:
#   https://github.com/frodenas/docker-couchdb/tree/master/scripts
# Additional information on first-run configurations
#   http://docs.couchdb.org/en/stable/setup/single-node.html

# Default parameter values
$user_default = "admin"
$password_default = "couchdb"
$db_port_default = 5984
$db_port_admin = 5986
$db_check_interval = 5

# Set admin user / pw info
$user = if ( (-not $env:COUCHDB_USER) -or ($env:COUCHDB_USER -eq "") ) { $user_default } else { $env:COUCHDB_USER }
$password = if ( (-not $env:COUCHDB_PASSWORD) -or ($env:COUCHDB_PASSWORD -eq "") ) { $password_default } else { $env:COUCHDB_PASSWORD }
$db = if ( (-not $env:COUCHDB_DBNAME) -or ($env:COUCHDB_DBNAME -eq "") ) { $null } else { $env:COUCHDB_DBNAME }

# Update config
$conf_file = "$($env:COUCHDB_HOME)\etc\local.ini"

function UpdateConfig($key, $value, $file) {
  # Omit $value here, in case there is sensitive information
  Write-Host "[Configuring] '$key' in '$file'"

  # If config exists in file, replace it. Otherwise, append to file.
  if (Get-Content -Path $file | Select-String -Pattern "^;?$key = ") {
      Write-Host "Replacing to $key = $value"
      Get-Content -Path $file | ForEach-Object { $_ -replace "^;?$key = .*", "$key = $value" } > "$file.tmp"
      Get-Content -Path "$file.tmp" | Set-Content $file 
  }
  else {
      Write-Host "Adding $key=$value"
      Add-Content $file "$key=$value`n" -NoNewline
  }
}

UpdateConfig "bind_address" "0.0.0.0" $conf_file
UpdateConfig "port" $db_port_default $conf_file

# Start CouchDB service
$cdbsvc = Get-Service "Apache CouchDB"
if ($cdbsvc.Status -ne "Running") {
  Start-Service -Name "Apache CouchDB"
  $timeout = (Get-Date).AddSeconds(300)
  # wait for service to start
  do {
    try {
      Test-NetConnection -ComputerName "localhost" -Port $db_port_default -WarningAction Stop -ErrorAction Stop *>$null
      Write-Verbose "$actualhost : $actualport is open"
      break
    }
    catch {
      # connection failure handling
      $errorMessage = $_.Exception.Message
      Write-Verbose "Apache CouchDB port $db_port_default is not responding, error: $errorMessage"
      if ((Get-Date) -le $timeout) {
        Start-Sleep -Second $db_check_interval
      }
      else {
        throw [System.ApplicationException] "Apache CouchDB port $db_port_default is not responding, error: $errorMessage"
      }
    }
  } while ((Get-Date) -le $timeout)
}

# Create User
Write-Host "Creating user: $user..."
Invoke-RestMethod -Method PUT -Uri http://127.0.0.1:$db_port_admin/_config/admins/$user -Body "`"$password`""

# Create Database
if ($db) {
  Write-Host "Creating database: $db..."
  Invoke-RestMethod -Method PUT http://${user}:${password}@127.0.0.1:$db_port_default/$db
}

# Stop CouchDB service
Stop-Service -Name "Apache CouchDB"

Write-Host "========================================================================"
Write-Host "CouchDB User: $user"
Write-Host "CouchDB Password: $password"
if ($db) {
  Write-Host "CouchDB Database: $db"
}
Write-Host "========================================================================"

Remove-Item c:\firstrun.txt
