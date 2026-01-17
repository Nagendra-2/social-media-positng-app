# Gmail to Social Media n8n Workflow

This workflow automatically converts newsletter emails into social media posts for Twitter and LinkedIn.

---

## 📋 Workflow Overview

```
Gmail Trigger → Get Message → Extract Text → Parse Sections → AI Agent → Post to Queue
```

### Nodes

1. **Gmail Trigger** - Monitors inbox for emails from `hi@mail.theresanaiforthat.com`
2. **Get a message** - Fetches full email content
3. **Edit Fields** - Extracts text content
4. **Code in JavaScript2** - Parses newsletter into individual items (title, description, link)
5. **AI Agent1** - Generates Twitter and LinkedIn posts using AI
6. **Structured Output Parser** - Ensures consistent JSON output format
7. **Edit Fields5** - Maps AI output to final format
8. **HTTP Request2** - Sends posts to the automation API queue

---

## 🔧 Required Credentials

### Gmail OAuth2

- Name: `Gmail account`
- Used by: Gmail Trigger, Get a message

### Google Gemini API

- Name: `Google Gemini(PaLM) Api account 2`
- Used by: Google Gemini Chat Model, Google Gemini Chat Model1

### Mistral Cloud API

- Name: `Mistral Cloud account`
- Used by: Mistral Cloud Chat Model

---

## ⚙️ Configuration

### Gmail Filter

- Sender: `hi@mail.theresanaiforthat.com`
- Includes drafts: Yes
- Read status: Both

### AI System Prompt

The AI Agent uses a professional social media copywriter persona with strict rules:

- No meta-talk ("Here is the post")
- No labels ("Title:", "Tweet:")
- Professional, punchy voice
- LinkedIn: Short paragraphs, bullet points, takeaways
- Twitter: Under 280 chars, strong hooks
- 2-3 relevant hashtags (no generic #Tech)

### Output Schema

```json
{
  "Twitter": {
    "post_text": "Tweet content with hashtags"
  },
  "LinkedIn": {
    "post_text": "LinkedIn post content with hashtags"
  }
}
```

---

## 🔗 API Endpoint

Posts are sent to:

```
http://host.docker.internal:8000/queue
```

Body parameters:

- `twitter_text` - Tweet content
- `linkedin_text` - LinkedIn post content

---

## 📥 How to Import

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from File**
3. Select `gmail-to-social-media.json`
4. Update credentials for Gmail and AI models
5. Activate the workflow

---

## 🔄 Flow Diagram

```
┌─────────────────┐
│  Gmail Trigger  │  (New email from newsletter)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Get a message  │  (Fetch full content)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Edit Fields   │  (Extract text)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JavaScript     │  (Parse into items)
│  Parser         │  [title, description, link]
└────────┬────────┘
         │
         ▼ (Loop for each item)
┌─────────────────┐
│   AI Agent      │  (Generate posts)
│  + Gemini       │
│  + Mistral      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Edit Fields5   │  (Map output)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  → API Queue
└─────────────────┘
```

---

## 📝 Notes

- The JavaScript parser extracts markdown links `[title](url)` from the newsletter
- Each extracted item is processed separately by the AI
- The AI has a fallback model (Gemini) if the primary (Mistral) fails
- Posts are queued, not posted immediately (scheduler handles timing)
