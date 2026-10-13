# Per-repo fleet start config for sfx-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'sfx-mcp'
    BackendPort  = 11120
    FrontendPort = 11121
    HealthPath   = '/api/health'
    WebRoot      = 'webapp\frontend'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'sfx_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '11120' }
    }
    Frontend = @{
        Kind = 'vite'
    }
}
