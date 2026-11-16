<#
.SYNOPSIS
Inicia o servidor Neo4j Community 5.x local (ou container Docker 'neo4j-demo') e aplica o seed.
#>
param(
    [string]$Senha = "senhaDemo123",
    [switch]$AplicarSeed,
    [switch]$UsarDocker,
    [switch]$Foreground
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LocalDir = Join-Path $RepoRoot ".neo4j-local"
$SeedPath = Join-Path $RepoRoot "db\seed.cypher"

if ($UsarDocker) {
    $docker = Get-Command docker -ErrorAction Stop
    $exists = docker ps -a --filter "name=^neo4j-demo$" --format "{{.Names}}"
    if ($exists -eq "neo4j-demo") {
        docker start neo4j-demo | Out-Null
    } else {
        docker run -d --name neo4j-demo -p 7474:7474 -p 7687:7687 -e "NEO4J_AUTH=neo4j/$Senha" neo4j:5 | Out-Null
    }
} else {
    $neoHome = Get-ChildItem -Path $LocalDir -Directory -Filter "neo4j-community-*" | Select-Object -First 1
    $jdkHome = Get-ChildItem -Path $LocalDir -Directory -Filter "jdk-21*" | Select-Object -First 1
    if (-not $neoHome) { throw "Neo4j Community nao encontrado em $LocalDir" }
    if (-not $jdkHome) { throw "OpenJDK 21 nao encontrado em $LocalDir" }

    $env:JAVA_HOME = $jdkHome.FullName
    $env:NEO4J_HOME = $neoHome.FullName
    $env:PATH = "$($jdkHome.FullName)\bin;$env:PATH"

    $listening = $false
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $ar = $c.BeginConnect("127.0.0.1", 7687, $null, $null)
        if ($ar.AsyncWaitHandle.WaitOne(300)) {
            $c.EndConnect($ar)
            $listening = $true
        }
        $c.Close()
    } catch { }

    if ($listening) {
        Write-Host "[OK] Neo4j ja esta ativo na porta 7687." -ForegroundColor Green
    } else {
        $authFile = Join-Path $neoHome.FullName "data\dbms\auth.ini"
        if (-not (Test-Path $authFile)) {
            Write-Host "Definindo senha inicial do Neo4j..." -ForegroundColor Yellow
            & (Join-Path $neoHome.FullName "bin\neo4j-admin.bat") dbms set-initial-password $Senha
        }

        if ($Foreground) {
            Write-Host "Iniciando Neo4j Community 5 em primeiro plano ($($neoHome.Name))..." -ForegroundColor Cyan
            Set-Location $neoHome.FullName
            & (Join-Path $neoHome.FullName "bin\neo4j.bat") console
            exit $LASTEXITCODE
        }

        $logOut = Join-Path $LocalDir "neo4j-stdout.log"
        $logErr = Join-Path $LocalDir "neo4j-stderr.log"
        Write-Host "Iniciando Neo4j Community 5 ($($neoHome.Name))..." -ForegroundColor Cyan
        $proc = Start-Process -FilePath "cmd.exe" `
            -ArgumentList "/c", "`"$($neoHome.FullName)\bin\neo4j.bat`" console" `
            -WorkingDirectory $neoHome.FullName `
            -WindowStyle Hidden `
            -RedirectStandardOutput $logOut `
            -RedirectStandardError $logErr `
            -PassThru
        $proc.Id | Out-File -FilePath (Join-Path $LocalDir "neo4j.pid") -Encoding ascii
    }
}

Write-Host "Aguardando Neo4j Browser (7474) e Bolt (7687)..."
$ready = $false
for ($i = 0; $i -lt 45; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:7474" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            $c = New-Object System.Net.Sockets.TcpClient
            $ar = $c.BeginConnect("127.0.0.1", 7687, $null, $null)
            if ($ar.AsyncWaitHandle.WaitOne(500)) {
                $c.EndConnect($ar)
                $c.Close()
                $ready = $true
                break
            }
            $c.Close()
        }
    } catch { }
    Start-Sleep -Seconds 2
}

if (-not $ready) {
    throw "Neo4j nao respondeu nas portas 7474/7687 dentro do tempo esperado. Veja .neo4j-local\neo4j-stdout.log"
}

Write-Host "[OK] Neo4j Browser ativo em http://localhost:7474 (usuario: neo4j)" -ForegroundColor Green

if ($AplicarSeed) {
    python (Join-Path $RepoRoot "scripts\verificar_projeto.py") --bolt "bolt://localhost:7687" --user "neo4j" --password $Senha
}
