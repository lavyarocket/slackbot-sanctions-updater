# 🛡️ Slackbot Sanctions Updater 🚀

![Sanctions Bot Cloud Architecture](assets/sanctions-bot.drawio.svg)

## 🌐 Overview

This project is a proof-of-concept Slackbot and AWS-based automation for monitoring and surfacing updates to the [OFAC SDN (Specially Designated Nationals) List](https://www.treasury.gov/ofac/downloads/sdn.csv). It is designed to help compliance teams stay up to date with sanctions changes and enable quick lookups directly from Slack.

✨ Features:
- 📥 **Automated fetching** of the SDN list with change detection
- 💬 **Slack slash command** for real-time SDN queries
- ☁️ **AWS-native architecture**: Lambda, Step Functions, S3, API Gateway, CDK
- 🛠 **Internal use**: Secure and private for compliance teams

---

## 🎥 Demo

*[Loom Video Demo](https://www.loom.com/share/6068dbc273fb48a08e3f91711098e5cc?sid=a992f7b7-97fc-4d98-a6ae-cc2e9699e930)

---

## 🏗 Architecture

The system is fully serverless and orchestrated via AWS CDK. The main components are:

- 🪣 **S3 Bucket**: Stores current and previous SDN lists
- ⚙️ **Fetch Lambda**: Downloads, compares, and notifies Slack about SDN updates
- 🔍 **Search Lambda**: Responds to Slack slash commands for on-demand lookups
- 🧩 **Step Functions**: Orchestrates workflows between fetch/search operations
- 🌐 **API Gateway**: Exposes HTTP endpoints for Slack integration
- 🔐 **Secrets Manager**: Stores and secures Slack credentials

📊 *See the diagram above for a visual representation.*

---

## 📄 SDN List Schema

| Column      | Name        | Type   | Description                        |
|-------------|-------------|--------|------------------------------------|
| 1           | ent_num     | number | Unique record/listing identifier   |
| 2           | SDN_Name    | text   | Name of SDN                        |
| 3           | SDN_Type    | text   | Type of SDN                        |
| 4           | Program     | text   | Sanctions program name             |
| 5–12        | Other fields | mixed | Vessel and individual metadata     |

🔎 *Used fields in this project:* `ent_num`, `SDN_Name`, `SDN_Type`, `Program`

---

## 💡 Use Cases

- ✅ **Compliance Monitoring**: Ensure real-time awareness of sanctions updates
- 🧠 **Slack Integration**: Run `/check_sdn <name>` in Slack to query entities
- 📈 **Change Tracking**: View added/removed entities over time in Slack

---

## 🧠 Design Decisions

- 🪶 **Serverless-first**: All compute done with AWS Lambda
- 🔄 **Step Functions**: Decouple Slack from long-running fetch/search jobs
- 🔐 **Secrets Manager**: Tokens are securely managed, not hardcoded
- 🧼 **Clean schema**: Minimal JSON stored for performance

---

## 🚀 Deployment

CI/CD is managed by GitHub Actions ([`.github/workflows/deploy.yaml`](.github/workflows/deploy.yaml)).

📦 On push to `master`, it:
1. Installs dependencies and CDK
2. Bootstraps the environment
3. Deploys all infrastructure

📝 *Note: Slack token must exist in AWS Secrets Manager as* `sanctions-bot-slack-token`.

---

## ⚙️ How It Works

### 1️⃣ Scheduled Fetching & Slack Notification

- 🕒 Triggered 3× daily or can be triggered manually by `/trigger` in Slack
- 📥 Downloads new SDN list → compares with previous → saves to S3
- 📢 Posts summary + stats + chart to Slack

### 2️⃣ Real-time Slack Search

- 🧑‍💻 Run `/check_sdn <name>` in Slack
- 🌐 Hits API Gateway → Lambda loads list → finds matches → responds

---

## 📁 Project Structure

```
.
├── fetch_lambda/      # Downloads and compares OFAC SDN list
├── search_lambda/     # Slack slash command search handler
├── infra/             # AWS CDK stacks for full architecture
├── assets/            # Architecture diagrams and visual assets
├── .github/           # GitHub Actions config for CI/CD
└── README.md          # This beautiful file 😄
```

---

## 🔐 Security Considerations

- 🔒 Slack tokens retrieved from **Secrets Manager**
- 🧾 S3 is versioned and access-controlled
- ✅ No secrets or keys stored in repo

---

## 🔮 Future Enhancements

- 🌍 Support multiple sanctions lists (e.g., EU, UN, UK, Canada) for broader compliance coverage
- ✨ Add fuzzy search, pagination, advanced filters to Slack command
- 📄 Show full SDN metadata in search results
- 🚀 Publish for public use (e.g., via Slack App Directory)
- 📬 Email or webhook alerting on major SDN changes

---

## 📜 License

This project is for internal demo and compliance prototyping. Not currently open for public use.

---

🙋‍♂️ *Questions, feedback, or want a demo? Ping the maintainer!*

---
