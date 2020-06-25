
<#
 .Synopsis
  Powershell version of Wait-For-It tool

 .Description
  Given a host and port, wait for when it is available and run an optional command if specified

 .Parameter hostname
  The name of the host to test against

 .Parameter port
  The port of to test against

 .Parameter strict
  If true, it will only execute the command if host:port test suceeds, otherwise, it will run once wait is over.

 .Parameter quiet
  Don't output any status messages

 .Parameter timeout
  Max seconds to wait until service is available. Default to 0 (not waiting at all)

 .Example
   # Wait for maximally 300 seconds for a service running on localhost:8080
   Wait-For-It localhost:8080 -t 300

 .Example
   # Immediate test if localhost:8080 is listening, and if succeeded, run dir command
   Wait-For-It -hostname localhost -port 8080 -strict -cmd -- dir
#>
  
Function Wait-For-It {
  [CmdletBinding()]
  param
  (
    [Parameter(Position = 0)]
    [string]$hostnameport = $null,
    [string]$hostname = $null,
    [int]$port = $null,
    [switch]$strict,
    [int]$timeout = 0,
    [string] $cmd = $null
  )

  Begin { }

  Process { 
    if (-not $hostnameport -and (-not $hostname -or -not $port)) {
      throw [System.ArgumentException] "You should provide Host:Port to be checked"
    }

    if ($hostnameport) {
      $tokens = $hostnameport.split(":")
      if ($tokens.Count -ne 2) {
        throw [System.ArgumentException] "Invalid Host:Port format: $hostport"
      }
      $actualhost = $tokens[0]
      $actualport = $tokens[1]
    }
    else {
      $actualhost = $hostname
      $actualport = $port
    }
  
    if (-not $actualhost -or -not $actualport) {
      throw [System.ArgumentException] "Must provide both Host and Port"
    }

    $timeoutThreshold = (Get-Date).AddSeconds($timeout)
    $maxSleep = 5 # max interval before retrying
    $remainingTimeout = $timeout
    $oneMoreTry = $true

    while ($remainingTimeout -gt 0 -or $oneMoreTry) {
      try {
        Test-NetConnection -ComputerName $actualhost -Port $actualport -WarningAction Stop -ErrorAction Stop *>$null
        if ($cmd) {
          Write-Verbose "$actualhost : $actualport is open, executing command: $cmd"
          & $cmd
        }
        else {
          Write-Verbose "$actualhost : $actualport is open"
        }
        break
      }
      catch {
        # connection failure handling
        $errorMessage = $_.Exception.Message
        Write-Verbose "Check connection failed for $actualhost : $actualport, error: $errorMessage"

        $remainingTimeout = ($timeoutThreshold - (Get-Date)).seconds
        $sleepTime = if ($remainingTimeout -lt $maxSleep) { $remainingTimeout } else { $maxSleep }
        if ($sleepTime -gt 0) {
          Write-Verbose "$actualhost : $actualport is not reachable, try again in $sleepTime seconds"
          Start-Sleep -Second $sleepTime
        }
        else {
          $oneMoreTry = $false
        }

        if (-not ($remainingTimeout -gt 0 -or $oneMoreTry)) {
          if ((-not $strict) -and $cmd) {
            # if not in strict mode run the command when timeout has expired regardless of the outcome, then throw the error
            Write-Verbose "$actualhost : $actualport is not reachable, but executing command anyway: $cmd"
            & $cmd
          }
          throw [System.ApplicationException] "Timed out waiting for $actualhost : $actualport"
        }
      }
    }
  }

  End { }
}

Export-ModuleMember -Function Wait-For-It