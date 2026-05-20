# Safety & Guardrails
## Free AI Workbench | Veteran Fleet Technologies, LLC

This document tells you exactly how to use this app safely -- what it can do, what it cannot do, and what you must never put into it.

---

## What This App Is

Free AI Workbench is a **local tool that runs on your computer**. It sends your messages to AI models running on your own machine through Ollama. Nothing you type is sent to the internet unless you have added an optional cloud API key.

This app is NOT:
- A medical advisor
- A legal advisor
- A financial advisor
- A licensed professional of any kind

Do not use AI responses to make decisions that require a licensed professional. Always verify important information with the appropriate expert.

---

## The 10 Hard Safety Rules

**Rule 1 -- Never put private personal information in.**
Do not enter Social Security numbers, passport numbers, date of birth combined with full name, medical records, or any government ID numbers. If a model is connected to the cloud (you added an API key), that data leaves your machine.

**Rule 2 -- Never put financial credentials in.**
Do not enter bank account numbers, credit card numbers, routing numbers, brokerage login credentials, or wire transfer information. Ever. Under any circumstance.

**Rule 3 -- Never put passwords or API keys in the chat box.**
If you need to configure an API key, put it in `.env.local` only. Never paste a key into the chat. Never share your `.env.local` file with anyone.

**Rule 4 -- Never put confidential business data belonging to your employer in.**
This includes internal financial reports, proprietary research, unreleased product data, client lists, employee records, or anything marked confidential or proprietary. Your employer may have legal requirements (NDA, HIPAA, FERPA, trade secret law) that make this a serious liability.

**Rule 5 -- Never put another person's private information in without their consent.**
Do not paste someone else's email, medical information, address, phone number, or personal details into the AI. This can violate privacy laws (CCPA, GDPR) and expose you to legal risk.

**Rule 6 -- Do not use AI output as legal advice.**
AI does not know your jurisdiction, your contract, or your specific facts. Do not file, sign, or rely on anything an AI writes for legal purposes without a licensed attorney reviewing it first.

**Rule 7 -- Do not use AI output as medical advice.**
AI cannot diagnose, prescribe, or replace a physician. If you have a health concern, contact a licensed medical professional.

**Rule 8 -- Do not use AI output as financial advice.**
AI does not know your full financial picture, risk tolerance, or applicable regulations. Do not buy, sell, or commit money based solely on AI output.

**Rule 9 -- Verify before you act on AI output.**
AI models make mistakes, hallucinate facts, and can produce confident-sounding wrong answers. Any output that will affect a real decision -- a document you sign, a message you send, money you spend -- must be independently verified.

**Rule 10 -- Do not use this app to generate content that harms others.**
Do not use this app to write harassment, scams, impersonation, disinformation, malware, or any content designed to deceive or hurt people. This violates the terms of every model provider and exposes you to civil and criminal liability.

---

## Data Flow -- Where Your Data Goes

| Mode | Your message goes to... | Leaves your computer? |
|------|------------------------|----------------------|
| Local model only (default) | Ollama on your machine | NO |
| OpenAI key added | OpenAI servers | YES -- OpenAI's privacy policy applies |
| Anthropic key added | Anthropic servers | YES -- Anthropic's privacy policy applies |
| DeepSeek key added | DeepSeek servers (China) | YES -- Chinese infrastructure |
| Groq key added | Groq servers | YES -- Groq's privacy policy applies |

**Default mode is local only.** Your words go nowhere but your own computer.

If you add a cloud API key, treat that provider like you would any cloud service -- do not send them anything you would not put in an email.

---

## What Is Safe to Use This For

- Drafting documents you will review and edit before using
- Brainstorming ideas and getting a starting point
- Learning concepts and asking explanatory questions
- Code assistance (review the code before running it)
- Writing assistance (review and fact-check before submitting)
- Summarizing documents you already own
- Business planning drafts (not final legal or financial documents)
- Interview and career prep
- General research starting points (verify sources independently)

---

## Disclaimer (Include This in Any Public Distribution)

**Free AI Workbench is provided as-is for educational and productivity purposes. It is not a licensed professional service. Veteran Fleet Technologies, LLC makes no warranties, express or implied, about the accuracy, completeness, or fitness for a particular purpose of any AI output. Users assume full responsibility for how they use this tool and its outputs. This software does not provide legal, medical, financial, or professional advice of any kind. Always consult a qualified professional before making decisions based on AI-generated content.**

---

## For Developers and Anyone Who Shares This App

If you redistribute this app, you must:
1. Keep this safety document included
2. Keep the disclaimer visible in the interface
3. Not remove the local-only default behavior
4. Not modify the app to silently send data to external servers

---

*Veteran Fleet Technologies, LLC | Marcos Alvarez | 2026 | MIT License*
