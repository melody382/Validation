# captain-turn.ps1 - drive the Ethikal Outcomes Captain with full, untruncated history.
#
# Why this exists: each chat_with_*_advisor call opens a NEW server session (finding E4).
# advisors-ask.ps1 --chat works around that by resending the last 8 turns truncated to
# 700 chars, which cannot carry a 121-answer instrument. This client resends everything
# and posts JSON-RPC directly, so the message is not subject to command-line length limits.
#
#   .\captain-turn.ps1 -Message "..."          send a turn
#   .\captain-turn.ps1 -Message "..." -Reset   start a fresh transcript
#   .\captain-turn.ps1 -Show                   print the transcript so far

param(
  [string]$Message,
  [switch]$Reset,
  [switch]$Show,
  [string]$Advisor = 'Outcomes Captain',
  [string]$Tier    = 'platform'
)

$ErrorActionPreference = 'Stop'
$here       = Split-Path -Parent $MyInvocation.MyCommand.Path
$transcript = Join-Path $here 'transcript.json'
$logfile    = Join-Path $here 'captain-run.md'

if ($Reset -and (Test-Path $transcript)) { Remove-Item $transcript -Force }

$history = @()
if (Test-Path $transcript) {
  $loaded = Get-Content $transcript -Raw | ConvertFrom-Json
  if ($loaded) { $history = @($loaded) }
}

if ($Show) {
  foreach ($t in $history) { "### Me`n$($t.q)`n`n### Captain`n$($t.a)`n`n---`n" }
  exit 0
}
if (-not $Message) { Write-Error "No -Message supplied."; exit 1 }

# --- endpoint + auth -------------------------------------------------------
$Endpoint = if ($env:INTERNAL_MCP_URL) { $env:INTERNAL_MCP_URL.TrimEnd('/') } else { 'http://advisors-internal-mcp.tailbca6b5.ts.net/internal-mcp' }
if ($Endpoint -notmatch '/internal-mcp$') { $Endpoint += '/internal-mcp' }
$Key = $env:ADVISORS_API_KEY
if (-not $Key) {
  $kp = Join-Path $env:USERPROFILE '.advisors\key'
  if (Test-Path $kp) { $Key = (Get-Content $kp -Raw).Trim() }
}
if (-not $Key) { Write-Error "No API key (ADVISORS_API_KEY or ~\.advisors\key)."; exit 1 }
$Headers = @{ Authorization = "Bearer $Key"; Accept = 'application/json, text/event-stream' }

function Invoke-Rpc($Method, $Params, [switch]$Notif) {
  $body = @{ jsonrpc = '2.0'; method = $Method }
  if (-not $Notif)        { $body['id'] = 1 }
  if ($null -ne $Params)  { $body['params'] = $Params }
  $json = $body | ConvertTo-Json -Depth 20 -Compress
  try {
    (Invoke-WebRequest -Uri $Endpoint -Method Post -Headers $Headers `
       -ContentType 'application/json' -Body $json -UseBasicParsing -TimeoutSec 600).Content
  } catch {
    $code = $null; try { $code = $_.Exception.Response.StatusCode.value__ } catch {}
    if ($code -in 401,403) { Write-Error "Auth failed (HTTP $code)." }
    else { Write-Error "Request failed: $($_.Exception.Message) (Tailscale up? endpoint=$Endpoint)" }
    exit 1
  }
}

function Parse-Result($raw) {
  $s = $raw.Trim()
  if ($s.StartsWith('{')) { try { return $s | ConvertFrom-Json } catch { return $null } }
  $obj = $null
  foreach ($ln in ($raw -split "`n")) {
    if ($ln.TrimStart().StartsWith('data:')) {
      try { $obj = ($ln.Substring($ln.IndexOf('data:') + 5).Trim() | ConvertFrom-Json) } catch {}
    }
  }
  return $obj
}

function Extract-Text($d) {
  if ($null -eq $d) { Write-Error "could not parse server response"; exit 1 }
  if (($d.PSObject.Properties.Name -contains 'error') -and $d.error) {
    Write-Error ("server error: " + ($d.error | ConvertTo-Json -Compress)); exit 1
  }
  $res = $d.result; $parts = @()
  if ($res -and $res.content) { foreach ($c in $res.content) { if ($c.type -eq 'text') { $parts += $c.text } } }
  if ($parts.Count -gt 0) { ($parts -join '') } else { ($res | ConvertTo-Json -Depth 20) }
}

# --- compose the turn, carrying ALL prior history --------------------------
$sent = $Message
if ($history.Count -gt 0) {
  $lines = @('[Conversation so far - oldest first. This is context you already said or I already answered. Do not restart the session; continue from where we left off.]','')
  foreach ($t in $history) { $lines += @(("Me: "   + $t.q), ("You: " + $t.a), '') }
  $lines += @('[Now continue. My next answer:]', ("Me: " + $Message))
  $sent = ($lines -join "`n")
}

[void](Invoke-Rpc 'initialize' @{ protocolVersion='2025-06-18'; capabilities=@{}; clientInfo=@{ name='captain-turn-ps'; version='1' } })
[void](Invoke-Rpc 'notifications/initialized' @{} -Notif)

$raw   = Invoke-Rpc 'tools/call' @{ name = "chat_with_${Tier}_advisor"; arguments = @{ advisor = $Advisor; message = $sent } }
$reply = Extract-Text (Parse-Result $raw)

$history += @{ q = $Message; a = $reply }
($history | ConvertTo-Json -Depth 10) | Out-File $transcript -Encoding utf8
"`n### Turn $($history.Count) - Me`n`n$Message`n`n### Turn $($history.Count) - Captain`n`n$reply`n`n---`n" |
  Out-File $logfile -Encoding utf8 -Append

"[turn $($history.Count) | sent $($sent.Length) chars | received $($reply.Length) chars]"
""
$reply
