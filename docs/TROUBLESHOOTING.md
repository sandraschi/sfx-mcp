# Troubleshooting

## API key not configured

Set `FREESOUND_API_KEY` in `.env`. Get a key at https://freesound.org/apiv2/apply.

## Rate limiting

FreeSound free tier: ~20 req/min. The client self-limits to 18 req/min with backoff.

## Port conflict

```powershell
Get-NetTCPConnection -LocalPort 11120 | Stop-Process -Id $_.OwningProcess
```
