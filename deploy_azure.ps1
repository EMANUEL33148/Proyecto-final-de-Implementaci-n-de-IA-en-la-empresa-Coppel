$ErrorActionPreference = 'Stop'

$resourceGroup = 'coppelgrup'
$appName = 'coppel-emanuel-linux-2026'
$foundryProjectScope = '/subscriptions/25a3e2e1-a3cb-40d9-a5f7-b83aa73faf70/resourceGroups/cooppel01/providers/Microsoft.CognitiveServices/accounts/coppel73/projects/asistente-coppel'
$appUrl = "https://$appName.azurewebsites.net"
$sourceApp = Join-Path $PSScriptRoot 'App coppel.py'
$requirements = Join-Path $PSScriptRoot 'requirements.txt'
$stagingDirectory = Join-Path $env:TEMP ("coppel-deploy-" + [guid]::NewGuid().ToString('N'))
$zipPath = Join-Path $env:TEMP ("coppel-deploy-" + [guid]::NewGuid().ToString('N') + '.zip')

function Invoke-Az {
    param([Parameter(Mandatory)][string[]]$Arguments)

    & az @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI command failed: az $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $sourceApp -PathType Leaf) -or
    -not (Test-Path -LiteralPath $requirements -PathType Leaf)) {
    throw 'Faltan App coppel.py o requirements.txt en la carpeta del proyecto.'
}

try {
    Invoke-Az -Arguments @('account', 'show', '--output', 'none')

    $principalId = az webapp identity assign --resource-group $resourceGroup --name $appName --query principalId --output tsv
    if ($LASTEXITCODE -ne 0 -or -not $principalId) {
        throw 'No se pudo habilitar la identidad administrada de la aplicación.'
    }

    $hasAgentRole = az role assignment list `
        --scope $foundryProjectScope `
        --assignee-object-id $principalId `
        --query "[?roleDefinitionName=='Foundry Agent Consumer'] | length(@)" `
        --output tsv
    if ($LASTEXITCODE -ne 0 -or $null -eq $hasAgentRole) {
        throw 'No se pudieron comprobar los permisos de la identidad en el proyecto Foundry.'
    }

    if ([int]$hasAgentRole -eq 0) {
        Invoke-Az -Arguments @(
            'role', 'assignment', 'create',
            '--assignee-object-id', $principalId,
            '--assignee-principal-type', 'ServicePrincipal',
            '--role', 'Foundry Agent Consumer',
            '--scope', $foundryProjectScope,
            '--output', 'none'
        )
    }

    Invoke-Az -Arguments @(
        'webapp', 'config', 'appsettings', 'set',
        '--resource-group', $resourceGroup,
        '--name', $appName,
        '--settings',
        'SCM_DO_BUILD_DURING_DEPLOYMENT=true',
        'ENABLE_ORYX_BUILD=true',
        'WEBSITES_PORT=8000',
        'AZURE_INTERACTIVE_LOGIN=false',
        '--output', 'none'
    )

    Invoke-Az -Arguments @(
        'webapp', 'config', 'set',
        '--resource-group', $resourceGroup,
        '--name', $appName,
        '--startup-file', 'python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0',
        '--web-sockets-enabled', 'true',
        '--output', 'none'
    )
    Invoke-Az -Arguments @(
        'webapp', 'update',
        '--resource-group', $resourceGroup,
        '--name', $appName,
        '--https-only', 'true',
        '--output', 'none'
    )

    New-Item -ItemType Directory -Path $stagingDirectory | Out-Null
    Copy-Item -LiteralPath $sourceApp -Destination (Join-Path $stagingDirectory 'app.py')
    Copy-Item -LiteralPath $requirements -Destination (Join-Path $stagingDirectory 'requirements.txt')
    Compress-Archive -Path (Join-Path $stagingDirectory '*') -DestinationPath $zipPath -Force

    Invoke-Az -Arguments @(
        'webapp', 'deploy',
        '--resource-group', $resourceGroup,
        '--name', $appName,
        '--src-path', $zipPath,
        '--type', 'zip'
    )
    Invoke-Az -Arguments @('webapp', 'restart', '--resource-group', $resourceGroup, '--name', $appName)

    $deadline = (Get-Date).AddMinutes(10)
    do {
        Start-Sleep -Seconds 10
        try {
            $response = Invoke-WebRequest -Uri $appUrl -UseBasicParsing -TimeoutSec 20
            if ($response.StatusCode -eq 200) {
                Write-Host "Aplicación publicada y accesible en: $appUrl"
                return
            }
        }
        catch {
            if ($_.Exception.Response -and $_.Exception.Response.StatusCode -eq 403) {
                throw "Azure devolvió HTTP 403 en $appUrl. Revisa la configuración y los registros de App Service."
            }
        }
    } while ((Get-Date) -lt $deadline)

    throw "Azure aceptó el despliegue, pero la aplicación no respondió en $appUrl después de 10 minutos."
}
finally {
    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    if (Test-Path -LiteralPath $stagingDirectory) {
        Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
    }
}
