<#
.SYNOPSIS
Utilitario de verificacao e preparacao de ambiente local do Neo4j no Windows.

.DESCRIPTION
Verifica a disponibilidade de Docker, Neo4j Desktop e Java no computador atual.
Se o Docker estiver instalado, inicia o container `neo4j-demo` (Neo4j 5) nas portas
7474 (Browser HTTP) e 7687 (Bolt) com senha padrao `senhaDemo123` e aplica o seed
automaticamente caso o container esteja pronto.
#>

param(
    [switch]$IniciarDocker,
    [string]$Senha = "senhaDemo123"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SeedPath = Join-Path $RepoRoot "db\seed.cypher"

Write-Host "=== Diagnostico de Ambiente Neo4j (Projeto 3 NoSQL) ===" -ForegroundColor Cyan

# 1. Verifica Docker
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
$dockerPath = if ($dockerCmd) { $dockerCmd.Source } elseif (Test-Path "C:\Program Files\Docker\Docker\resources\bin\docker.exe") { "C:\Program Files\Docker\Docker\resources\bin\docker.exe" } else { $null }
if ($dockerPath) {
    Write-Host "[OK] Docker encontrado: $dockerPath" -ForegroundColor Green
    if ($IniciarDocker) {
        & (Join-Path $PSScriptRoot "iniciar_neo4j.ps1") -UsarDocker -Senha $Senha -AplicarSeed
    }
} else {
    Write-Host "[AVISO] Docker nao encontrado neste PC." -ForegroundColor Yellow
}

# 1b. Verifica instalacao local portatil (.neo4j-local)
$localDir = Join-Path $RepoRoot ".neo4j-local"
$localNeo = Get-ChildItem -Path $localDir -Directory -Filter "neo4j-community-*" -ErrorAction SilentlyContinue | Select-Object -First 1
$localJdk = Get-ChildItem -Path $localDir -Directory -Filter "jdk-21*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($localNeo -and $localJdk) {
    Write-Host "[OK] Neo4j 5 nativo + JDK 21 prontos em .neo4j-local ($($localNeo.Name))" -ForegroundColor Green
}

# 2. Verifica Neo4j Desktop
$desktopPaths = @(
    "$env:LOCALAPPDATA\Programs\Neo4j Desktop\Neo4j Desktop.exe",
    "$env:ProgramFiles\Neo4j Desktop\Neo4j Desktop.exe"
)
$foundDesktop = $desktopPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($foundDesktop) {
    Write-Host "[OK] Neo4j Desktop encontrado em: $foundDesktop" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Neo4j Desktop nao encontrado." -ForegroundColor Yellow
}

# 3. Verifica Java
try {
    $javaOut = cmd /c "java -version 2>&1"
    Write-Host "[INFO] Java detectado: $($javaOut[0])" -ForegroundColor Gray
    Write-Host "       Nota: Neo4j 5.x exige Java 17 ou Java 21 se executado diretamente sem Docker." -ForegroundColor Gray
} catch {
    Write-Host "[AVISO] Java nao encontrado no PATH." -ForegroundColor Yellow
}

# 4. Verifica se ha instancia Neo4j ativa localmente nas portas 7474/7687
$listening = Get-NetTCPConnection -LocalPort 7474,7687 -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    Write-Host "[OK] Servico escutando em porta Neo4j (7474/7687)." -ForegroundColor Green
} else {
    Write-Host "`nComo subir o ambiente neste Windows:" -ForegroundColor Cyan
    Write-Host "  Opcao 1 (Neo4j 5 nativo local - imediato):"
    Write-Host "    .\scripts\iniciar_neo4j.ps1 -AplicarSeed"
    Write-Host "  Opcao 2 (Docker Desktop):"
    Write-Host "    .\scripts\iniciar_neo4j.ps1 -UsarDocker -AplicarSeed"
    Write-Host "  Opcao 3 (Nuvem gratuita - AuraDB Free):"
    Write-Host "    1) Acesse https://console.neo4j.io e crie uma instancia Free"
    Write-Host "    2) Conecte no Query/Browser e execute db\seed.cypher"
    Write-Host "  Para encerrar o servidor local:"
    Write-Host "    .\scripts\parar_neo4j.ps1"
}
