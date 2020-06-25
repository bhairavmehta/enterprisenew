# Store original IFS config, so we can restore it at various stages
if ($null -eq $env:KAFKA_ZOOKEEPER_CONNECT) {
    Write-Error "ERROR: missing mandatory config: KAFKA_ZOOKEEPER_CONNECT"
    exit 1
}

if ($null -eq $env:KAFKA_PORT) {
    $env:KAFKA_PORT = 9092
}

Start-Process powershell -ArgumentList @("$PSScriptRoot\create-topics.ps1")
$env:KAFKA_CREATE_TOPICS = $null

if (($null -eq $env:KAFKA_ADVERTISED_PORT) -and 
    ($null -eq $env:KAFKA_LISTENERS) -and 
    ($null -eq $env:KAFKA_ADVERTISED_LISTENERS)) {
    Write-Error "You must provide KAFKA_ADVERTISED_PORT, KAFKA_LISTENERS or KAFKA_ADVDRTISED_LISTENERS"
    exit 1
}

if ($null -eq $env:KAFKA_BROKER_ID) {
    if ($null -ne $env:BROKER_ID_COMMAND) {
        $env:KAFKA_BROKER_ID = (Invoke-Expression $env:BROKER_ID_COMMAND | Out-String)
    }
    else {
        # By default auto allocate broker ID
        $env:KAFKA_BROKER_ID = -1
    }
}

if ($null -eq $env:KAFKA_LOG_DIRS) {
    # Note: Even in Windows it is imported to use / instead of \ for log.dirs configuration for kafka
    $env:KAFKA_LOG_DIRS = "c:/kafka/kafka-logs-$($env:ComputerName)"
}

# Unsupported OPTS (still need to be done)
#
#if [[ -n "$KAFKA_HEAP_OPTS" ]]; then
#    sed -r -i 's/(export KAFKA_HEAP_OPTS)="(.*)"/\1="'"$KAFKA_HEAP_OPTS"'"/g' "$KAFKA_HOME/bin/kafka-server-start.sh"
#    unset KAFKA_HEAP_OPTS
#fi

# if [[ -n "$HOSTNAME_COMMAND" ]]; then
#     HOSTNAME_VALUE=$(eval "$HOSTNAME_COMMAND")

#     # Replace any occurences of _{HOSTNAME_COMMAND} with the value
#     IFS=$'\n'
#     for VAR in $(env); do
#         if [[ $VAR =~ ^KAFKA_ && "$VAR" =~ "_{HOSTNAME_COMMAND}" ]]; then
#             eval "export ${VAR//_\{HOSTNAME_COMMAND\}/$HOSTNAME_VALUE}"
#         fi
#     done
#     IFS=$ORIG_IFS
# fi

# if [[ -n "$PORT_COMMAND" ]]; then
#     PORT_VALUE=$(eval "$PORT_COMMAND")

#     # Replace any occurences of _{PORT_COMMAND} with the value
#     IFS=$'\n'
#     for VAR in $(env); do
#         if [[ $VAR =~ ^KAFKA_ && "$VAR" =~ "_{PORT_COMMAND}" ]]; then
# 	    eval "export ${VAR//_\{PORT_COMMAND\}/$PORT_VALUE}"
#         fi
#     done
#     IFS=$ORIG_IFS
# fi

# if [[ -n "$RACK_COMMAND" && -z "$KAFKA_BROKER_RACK" ]]; then
#     KAFKA_BROKER_RACK=$(eval "$RACK_COMMAND")
#     export KAFKA_BROKER_RACK
# fi

# Try and configure minimal settings or exit with error if there isn't enough information
if ("" -eq "$($env:KAFKA_ADVERTISED_HOST_NAME)$($env:KAFKA_LISTENERS)") {
    if ($null -ne $env:KAFKA_ADVERTISED_LISTENERS) {
        Write-Error "ERROR: Missing environment variable KAFKA_LISTENERS. Must be specified when using KAFKA_ADVERTISED_LISTENERS"
        exit 1
    }
    elseif ($null -eq $env:HOSTNAME_VALUE) {
        Write-Error "ERROR: No listener or advertised hostname configuration provided in environment."
        Write-Error "       Please define KAFKA_LISTENERS / (deprecated) KAFKA_ADVERTISED_HOST_NAME"
        exit 1
    }

    # Maintain existing behaviour
    # If HOSTNAME_COMMAND is provided, set that to the advertised.host.name value if listeners are not defined.
    $env:KAFKA_ADVERTISED_HOST_NAME = $env:HOSTNAME_VALUE
}

#Issue newline to config file in case there is not one already
Add-Content $env:KAFKA_HOME\config\server.properties "`n"

function UpdateConfig($key, $value, $file) {
    # Omit $value here, in case there is sensitive information
    Write-Host "[Configuring] '$key' in '$file'"

    # If config exists in file, replace it. Otherwise, append to file.
    if (Get-Content -Path $file | Select-String -Pattern "^#?$key=") {
        Write-Host "Replacing to $key=$value"
        Get-Content -Path $file | ForEach-Object { $_ -replace "^#?$key=.*", "$key=$value" } > "$file.tmp"
        Get-Content -Path "$file.tmp" | Set-Content $file 
    }
    else {
        Write-Host "Adding $key=$value"
        Add-Content $file "$key=$value`n" -NoNewline
    }
}

# KAFKA_VERSION + KAFKA_HOME + grep -rohe KAFKA[A-Z0-0_]* /opt/kafka/bin | sort | uniq | tr '\n' '|'
$exclusions = "|KAFKA_VERSION|KAFKA_HOME|KAFKA_DEBUG|KAFKA_GC_LOG_OPTS|KAFKA_HEAP_OPTS|KAFKA_JMX_OPTS|KAFKA_JVM_PERFORMANCE_OPTS|KAFKA_LOG|KAFKA_OPTS|"

# Read in env as a new-line separated array. This handles the case of env variables have spaces and/or carriage returns. See #313
foreach ($env_var in (Get-Childitem -Path Env:* | Select-Object -ExpandProperty Name)) {
    if ($exclusions.IndexOf("|$env_var|") -ge 0) {
        Write-Host "Excluding $env_var from broker config"
        continue
    }

    if ($env_var.IndexOf("KAFKA_") -eq 0) {
        $kafka_name = $env_var.SubString(6).ToLower().Replace("_", ".")
        $env_var_val = (Get-Item env:\$env_var).Value
        UpdateConfig $kafka_name $env_var_val "$env:KAFKA_HOME\config\server.properties"
    }

    if ($env_var.IndexOf("LOG4J_") -eq 0) {
        $log4j_name = $env_var.SubString(6).ToLower().Replace("_", ".")
        $env_var_val = (Get-Item env:\$env_var).Value
        UpdateConfig $log4j_name $env_var_val "$env:KAFKA_HOME\config\server.properties"
    }
}

if ($null -ne $env:CUSTOM_INIT_SCRIPT) {
    Invoke-Expression $env:CUSTOM_INIT_SCRIPT
}

# Wait for ZooKeeper for come online
$timeout=300
$start_timeout_exceeded=$false
$timeoutThreshold=(Get-Date).AddSeconds($timeout)
$sleepTime=10
$zkEndPoint = ($env:KAFKA_ZOOKEEPER_CONNECT).split(":")
Write-Host "Waiting for ZooKeeper Endpoint $($zkEndPoint[0]):$($zkEndPoint[1]) to become available ..."
while (-not $start_timeout_exceeded) {
    try {
        Test-NetConnection -ComputerName $zkEndPoint[0] -Port $zkEndPoint[1] -WarningAction Stop -ErrorAction Stop *>$null
        Write-Verbose "$($zkEndPoint[0]):$($zkEndPoint[1]) is open"
        break
    }
    catch {
        $remainingTimeout = ($timeoutThreshold - (Get-Date)).seconds
        if ($remainingTimeout -gt 0) {
            Write-Verbose " $($zkEndPoint[0]):$($zkEndPoint[1]) is not reachable, try again in $sleepTime seconds"
            Start-Sleep -Second $sleepTime
        } else {
            $start_timeout_exceeded = $false
        }
    }
}

if ($start_timeout_exceeded) {
    Write-Error "Not able to auto-create topic (waited for $timeout sec)"
    exit 1
}

# Start Kafka
& $env:KAFKA_HOME\bin\windows\kafka-server-start.bat "$env:KAFKA_HOME\config\server.properties" | Out-Default