# インストール検証手順

このプラグインを実際に GitHub に公開し、Claude Code の標準コマンド (`/plugin marketplace add`, `/plugin install`) で導入できることを検証するためのチェックリスト。
検証が通った後で、結果に応じて README を必要に応じて修正する。

## 事前準備

1. GitHub にこのリポジトリを `<user>/ccdiscord` として作成し、`main` をプッシュする
2. `.claude-plugin/marketplace.json` の `repo` を `<user>/ccdiscord` に書き換えて push しておく
   - 同ファイルの `owner.name`、`.claude-plugin/plugin.json` の `author.name` も任意で更新
3. Discord デスクトップクライアントを起動しておく

## 1. インストールが通ること

別ディレクトリで Claude Code セッションを起動し、以下を順に実行する。

```
/plugin marketplace add <user>/ccdiscord
/plugin install ccdiscord@ccdiscord
```

- [ ] `marketplace add` がエラーなく完了する
- [ ] `install` がエラーなく完了する
- [ ] `/plugin list` 等で `ccdiscord` が有効と表示される

## 2. SessionStart で Rich Presence が出ること

新しい Claude Code セッションを起動。

- [ ] Discord 上で「Claude Code をプレイ中 / AI assisted coding」が表示される
- [ ] 経過時間が 0 から進む

## 3. SessionEnd で Rich Presence が消えること

セッションを終了 (`/exit` 等)。

- [ ] Discord 上のアクティビティが消える
- [ ] `${TMPDIR}/ccdiscord/<session_id>.pid` が削除されている
  - `ls "${TMPDIR}ccdiscord/"` あるいは `ls /tmp/ccdiscord/` で確認

## 4. 複数セッションが独立に動くこと

- [ ] セッション A を起動 → A の PID ファイルが作成される
- [ ] セッション B を起動 → B の PID ファイルが追加で作成される（A は残ったまま）
- [ ] B を終了 → B の PID ファイルだけ消え、A のプロセスは残る（Discord にはどちらかが表示される）
- [ ] A を終了 → A も消え、Discord のアクティビティが消える

## 5. エラーハンドリングが効くこと

Discord デスクトップクライアントを終了した状態でセッション開始。

- [ ] Claude Code セッション自体は正常に開く（フックの失敗で起動が遅れたり阻まれたりしない）
- [ ] フック出力で `[ccdiscord] Discord desktop client not detected. ...` 相当のメッセージが見える
  - 確認方法: `claude -d hooks` で起動してフックの stderr を確認

## 6. ローカル試用 (`claude --plugin-dir`) が機能すること

リポジトリ直下で:

```
claude --plugin-dir .
```

- [ ] Rich Presence が表示される

> README には現状 `claude --plugin-dir ./ccdiscord` とあるが、これは「親ディレクトリで実行する」前提の表記。検証後、リポジトリ直下で動かす想定なら `.` 表記に直す方針で OK。

## 検証後に README へ反映する候補

- `## セットアップ` の `/plugin marketplace add YOUR_GITHUB_USERNAME/ccdiscord` の `YOUR_GITHUB_USERNAME` を実際のユーザー名に置換するか、プレースホルダのまま「ここに自分の GitHub ユーザー名を入れる」と注意書きするかを決める
- `claude --plugin-dir` の例を `.` に揃える（実行ディレクトリの混乱を解消）
- `## カスタマイズ` のような独立セクションに任意 Step 1〜2 を分離して見通しを良くする（任意）
