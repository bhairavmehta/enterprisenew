#!/bin/bash

if ($null -eq $env:KAFKA_CREATE_TOPICS) {
    exit 0
}

if ($null -eq $env:START_TIMEOUT) {
    $env:START_TIMEOUT = 600
}

$port = $env:KAFKA_PORT

$start_timeout_exceeded=$false
$timeoutThreshold=(Get-Date).AddSeconds($env:START_TIMEOUT)
$sleepTime=10
while (-not $start_timeout_exceeded) {
    try {
        Test-NetConnection -ComputerName localhost -Port $port -WarningAction Stop -ErrorAction Stop *>$null
        Write-Verbose "$port is open"
        break
    }
    catch {
        $remainingTimeout = ($timeoutThreshold - (Get-Date)).seconds
        if ($remainingTimeout -gt 0) {
            Write-Verbose "$port is not reachable, try again in $sleepTime seconds"
            Start-Sleep -Second $sleepTime
        } else {
            $start_timeout_exceeded = $false
        }
    }
}

if ($start_timeout_exceeded) {
    Write-Error "Not able to auto-create topic (waited for $START_TIMEOUT sec)"
    exit 1
}

# We assume the version is > 0.10 here for Windows Container versions
KAFKA_0_10_OPTS="--if-not-exists"

# Expected format:
#   name:partitions:replicas:cleanup.policy
$sep = ","
if ($null -ne $env:KAFKA_CREATE_TOPICS_SEPARATOR) {
    $sep = $env:KAFKA_CREATE_TOPICS_SEPARATOR
}

foreach ($topicToCreate in $env:KAFKA_CREATE_TOPICS.split($sep)) {
    write-host "creating topics: $topicToCreate"
    $topicConfig = $topicToCreate.split(":")
    $config=""
    if ($null -ne $topicTokens[3]) {
        $config="--config=cleanup.policy=$($topicConfig[3])"
    }
    $proc = "${env:KAFKA_HOME}\bin\windows\kafka-topics.bat"
    $params = @("--create",
		"--zookeeper", $env:KAFKA_ZOOKEEPER_CONNECT,
		"--topic", $topicConfig[0], 
		"--partitions", $topicConfig[1],
		"--replication-factor", $topicConfig[2], 
		$config,
		$KAFKA_0_10_OPTS) 
    Start-Process -FilePath $proc -ArgumentList $params -Wait -NoNewWindow
}
