# Social Media Automation System

Automated posting to Twitter (X) and LinkedIn via n8n integration.

---

## 🚀 Quick Start

### Start the System

```powershell
cd d:\automation
docker-compose up -d
```

### Stop the System

```powershell
cd d:\automation
docker-compose down
```

### Restart the System

```powershell
cd d:\automation
docker-compose restart
```

---

## 🔍 Monitoring

### Check if Containers are Running

```powershell
docker ps
```

### View Scheduler Logs (Live)

```powershell
docker logs social-automation-scheduler -f
```

*Press `Ctrl+C` to exit*

### View Last 20 Log Lines

```powershell
docker logs social-automation-scheduler --tail 20
```

### Check Queue Size

```powershell
cd d:\automation
(Get-Content content_queue.json | ConvertFrom-Json).Count
```

### View Queue Items

```powershell
cd d:\automation
Get-Content content_queue.json | ConvertFrom-Json | Select-Object -First 5
```

---

## 🔧 Maintenance

### Rebuild After Code Changes

```powershell
cd d:\automation
docker-compose down
docker-compose up -d --build
```

### Clear the Queue

```powershell
cd d:\automation
"[]" | Set-Content content_queue.json
```

### View API Logs

```powershell
docker logs social-automation-api --tail 20
```

---

## ⚙️ Configuration

### Posting Interval

Edit `docker-compose.yml` and change:

```yaml
POSTING_INTERVAL_MINUTES=5
```

### API Credentials

Edit `.env` file with your credentials:

- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`
- `LINKEDIN_TOKEN`
- `LINKEDIN_PERSON_URN`

---

## 📁 File Structure

```
d:\automation\
├── .env                  # API credentials (secret)
├── .gitignore            # Git ignore rules
├── api.py                # FastAPI server
├── content_queue.json    # Pending posts queue
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Docker build file
├── env.example           # Template for .env
├── requirements.txt      # Python dependencies
├── social_post.py        # Twitter/LinkedIn clients
├── timer_post.py         # Scheduler script
└── README.md             # This file
```

---

## 🔄 How It Works

1. **n8n** generates content and sends it to the API (`http://localhost:8000/queue`)
2. **API** receives content and adds it to `content_queue.json`
3. **Scheduler** picks one item every 5 minutes and posts to both platforms
4. Posts go out to **Twitter** and **LinkedIn** simultaneously

---

## 🆘 Troubleshooting

### Containers Won't Start

```powershell
docker-compose down
docker-compose up -d --build
```

### API Not Responding

```powershell
docker restart social-automation-api
```

### Check Container Status

```powershell
docker ps -a
```

### View Full Logs

```powershell
docker logs social-automation-api
docker logs social-automation-scheduler
```

---

## 📌 Important Notes

- System auto-restarts when Docker Desktop starts
- Queue persists between restarts
- Both Twitter and LinkedIn post from the same queue item
- Default interval: 1 post every 5 minutes
