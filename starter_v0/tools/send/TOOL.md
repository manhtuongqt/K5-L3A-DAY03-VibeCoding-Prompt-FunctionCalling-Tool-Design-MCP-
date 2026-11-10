---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# send

Posts text to a Telegram channel. The message is only sent when `confirmed` is
the boolean `true`; strings such as `"false"` and numbers are not confirmations.
The calling application must obtain confirmation of the exact message from the
user before setting this flag. The tool cannot itself verify conversation history.
