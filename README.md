# ccdiscord

Claude Code の使用中に Discord のステータスへ Rich Presence を表示する Claude Code プラグイン。

## 必要条件

- [Claude Code](https://claude.ai/code)
- [uv](https://docs.astral.sh/uv/) (`pip install uv` または `brew install uv`)
- Discord デスクトップクライアント（ブラウザ版は不可）

## セットアップ

> 既定では同梱の Client ID（"Claude Code" として表示）と既定のテキストでそのまま動く。
> 表示名・アイコン・テキストを自分用にカスタマイズしたい人だけ Step 1, 2 を行う。それ以外は **Step 3 から**始めてよい。

### 1. （任意）Discord Application を作成して Client ID を取得

1. [discord.com/developers/applications](https://discord.com/developers/applications) を開く
2. **New Application** をクリックし、名前（例: `Claude Code`）を入力
3. 作成後、**OAuth2** メニューで **Client ID** をコピーする

### 2. （任意）Client ID をスクリプトに設定

このリポジトリをフォークし、`scripts/discord_rpc.py` の先頭にある定数を編集する。

```python
CLIENT_ID = "YOUR_CLIENT_ID_HERE"  # ← ここに取得した Client ID を貼り付ける
DETAILS = "Claude Code"            # 1行目に表示するテキスト（任意）
STATE = "AI assisted coding"       # 2行目に表示するテキスト（任意）
```

#### Discord 上の表示対応

各定数がどこに表示されるかを以下に示す。

**ユーザーリスト・プロフィールのステータス欄**

```
● [Application Name] をプレイ中
```

> `Application Name` = Discord Application 作成時に入力した名前（Client ID に紐づく）

**プロフィールカード（名前クリックまたはホバー時）**

```
┌─────────────────────────────────────┐
│ ゲームをプレイ中                      │
│  ┌──────────┐  [Application Name]   │ ← Discord Application の名前
│  │          │  [DETAILS]            │ ← DETAILS 定数
│  │  (画像)  │  [STATE]              │ ← STATE 定数
│  │          │  00:15 経過           │ ← セッション開始からの経過時間（自動）
│  └──────────┘                       │
└─────────────────────────────────────┘
```

> カード左の画像は Discord Application の **Rich Presence > Art Assets** でアップロード・設定した画像が表示される。設定しない場合は空欄。

**まとめ**

| 設定箇所 | 変数 / 設定 | Discord 上の表示位置 | コードから変更 |
|---------|------------|-------------------|:---:|
| Discord Application 名 | Application 作成時の名前 | 「〇〇をプレイ中」の〇〇、カード1行目 | ❌ |
| `CLIENT_ID` | Application の識別子 | 表示には出ないが画像・名前の紐付けに使用 | — |
| 「〇〇をプレイ中」の動詞部分 | `activity_type` パラメータ | ステータス欄・カードヘッダの動詞 | ✅ |
| `DETAILS` | `discord_rpc.py` の定数 | カード2行目 | ✅ |
| `STATE` | `discord_rpc.py` の定数 | カード3行目 | ✅ |
| `start=int(time.time())` | スクリプト固定値 | カード最下行（経過時間として自動表示） | ✅ |
| Art Assets（large_image等） | Discord Application の設定 | カード左の画像（設定した場合のみ） | ❌ |

**Application 名はコードから変更できない**

Discord の仕様上、「〇〇をプレイ中」の〇〇部分は `CLIENT_ID` に紐づく Developer Portal の Application 名から常に取得される。`update()` 呼び出しで上書きする手段はない。名前を変えたい場合は Developer Portal で Application 名を変更するか、別の Application を作成して Client ID を差し替える。

**動詞（「プレイ中」の部分）は変更できる**

`activity_type` パラメータで「プレイ中」を他の動詞に変えられる。

```python
from pypresence import Presence, ActivityType

rpc.update(
    details=DETAILS,
    state=STATE,
    start=int(time.time()),
    activity_type=ActivityType.WATCHING,  # 変更例
)
```

| `ActivityType` | ステータス欄の表示 |
|---------------|----------------|
| `PLAYING`（デフォルト） | 〇〇をプレイ中 |
| `WATCHING` | 〇〇を視聴中 |
| `LISTENING` | 〇〇を再生中 |
| `COMPETING` | 〇〇に参加中 |

`.claude-plugin/marketplace.json` の `repo` も自分のリポジトリに書き換える。

```json
"repo": "YOUR_GITHUB_USERNAME/ccdiscord"
```

変更を GitHub にプッシュしておく。

### 3. プラグインをインストール

Claude Code 内で以下を実行する。

```
/plugin marketplace add NS601023/ccpresence
/plugin install ccdiscord@ccdiscord
```

スコープを指定する場合（デフォルトはグローバル）：

```
/plugin install ccdiscord@ccdiscord --scope project   # このプロジェクトのみ
/plugin install ccdiscord@ccdiscord --scope user      # すべてのプロジェクト（デフォルト）
```

## ローカルで試す（フォーク前のテスト用）

```bash
claude --plugin-dir ./ccdiscord
```

## アンインストール

```
/plugin uninstall ccdiscord
```

## 既知の制限

- 複数セッションを同時起動した場合、それぞれが個別に Rich Presence を更新する。Discord は同一 Application について 1 件のアクティビティしか表示しないため、最後に Presence を更新したセッションの内容が表示される。各セッションの終了は独立して扱われる（自セッションぶんの Rich Presence のみ停止）。
