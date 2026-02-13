# Slack_auto_reminder

A bot that extracts posts on Slack made by members of a specific group whose names start with a number, and sends reminders via mentions.

Slack上の特定グループかつ数字から始まる名前のメンバーによる投稿を抽出し、メンションにてリマインドを行うボット

# How to use 使い方
## OAuth & Permissions（権限の設定）
左サイドメニューの "OAuth & Permissions" を開き、"Scopes" セクションまでスクロールします。"Bot Token Scopes" に以下の権限を追加してください。
- channels:history 
- channels:read
- chat:write
- users:read

## アプリのインストールとトークンの取得
権限を追加したら、同じページの上部にある "Install to Workspace" ボタンをクリックします。
インストールが完了すると、xoxb- で始まる "Bot User OAuth Token" が表示されます。
SLACK_BOT_TOKENをコピーして、以下の手順でトークンを設定します。

- GitHubリポジトリ
- Settings
- Secrets and variables
- Actions
- New repository secret

## チャンネルIDの取得
scripts/notify_non_reporters.pyに、Channel IDを設定する。
REPORT_CHANNEL_IDには、レポートを読み取るチャンネルのIDを設定する。
GROUP_CHANNELSはリマインドを行うチャンネルのIDを設定する。複数のグループを設定することが可能。


## アプリをチャンネルに招待する
APIの設定を完了後、ボットをSlackのチャンネルに招待する。
