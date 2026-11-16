<#
.SYNOPSIS
Encerra o servidor Neo4j local (processo nativo em .neo4j-local, portas 7474/7687 ou container Docker).
#>
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LocalDir = Join-Path $RepoRoot ".neo4j-local"
$PidFile = Join-Path $LocalDir "neo4j.pid"

if (Test-Path $PidFile) {
    $pidVal = (Get-Content $PidFile -Raw).Trim()
    if ($pidVal -match '^\d+$') {
        Write-Host "Encerrando arvore de processos do Neo4j (PID $pidVal)..." -ForegroundColor Yellow
        cmd /c "taskkill /PID $pidVal /T /F 2>nul" | Out-Null
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# Garante o encerramento de qualquer processo java/neo4j remanescente escutando nas portas 7474/7687
$conns = Get-NetTCPConnection -LocalPort 7474,7687 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
    foreach ($owningPid in ($conns.OwningProcess | Select-Object -Unique)) {
        if ($owningPid -gt 0) {
            Write-Host "Encerrando processo residual nas portas Neo4j (PID $owningPid)..." -ForegroundColor Yellow
            Stop-Process -Id $owningPid -Force -ErrorAction SilentlyContinue
        }
    }
}

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
    $running = docker ps --filter "name=^neo4j-demo$" --format "{{.Names}}" 2>$null
    if ($running -eq "neo4j-demo") {
        Write-Host "Parando container Docker 'neo4j-demo'..." -ForegroundColor Yellow
        docker stop neo4j-demo | Out-Null
    }
}

Write-Host "[OK] Comando de parada concluido." -ForegroundColor Green
