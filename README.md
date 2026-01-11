# TicketPro - オンラインチケット販売システム MVP

Djangoベースのオンラインチケット販売・管理システムのプロトタイプ実装です。

## 概要

イベントチケットのオンライン販売、座席管理、入場管理、売上管理を統合的に提供するWebアプリケーションです。

## 主な機能

### MVP機能（Phase 1-6）
- ✅ イベント・会場・座席マスタ管理（主催者）
- ✅ チケット購入（座席指定・自由席）
- ✅ 電子チケット発行（QRコード）
- ✅ 入場管理（QRコードスキャン）
- ✅ 会員管理（登録・ログイン・マイページ）
- ✅ 主催者ダッシュボード・売上管理

### 追加機能（Phase 7-10）
- ✅ パスワード変更・リセット
- ✅ 購入履歴確認
- ✅ 自由席チケット購入
- ✅ キャンセル・返金処理

## 技術スタック

- **Backend**: Django 5.2+, Python 3.11+
- **Database**: PostgreSQL (Docker)
- **Frontend**: Bootstrap 5, Alpine.js
- **QRコード**: qrcode, Pillow
- **PDF生成**: ReportLab

## セットアップ

### 前提条件

- Python 3.11以上
- PostgreSQL（Dockerコンテナ推奨）
- Git

### 1. リポジトリのクローン

```bash
git clone https://github.com/okab130/onlticket2.git
cd onlticket2
```

### 2. PostgreSQLコンテナの起動確認

```bash
docker ps --filter "name=db"
```

コンテナが起動していない場合:
```bash
docker start db
```

### 3. Python仮想環境の作成

```bash
python -m venv venv
```

### 4. 仮想環境の有効化

**Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
source venv/bin/activate
```

### 5. 依存関係のインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. 環境変数の設定

`.env.example`をコピーして`.env`を作成:

```bash
cp .env.example .env
```

`.env`を編集してデータベース接続情報を設定:

```
DATABASE_NAME=postgres
DATABASE_USER=postgres
DATABASE_PASSWORD=pass
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_SCHEMA=onlticket2
```

### 7. マイグレーションの実行

```bash
python manage.py migrate
```

### 8. スーパーユーザーの作成

```bash
python manage.py createsuperuser
```

### 9. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで http://localhost:8000 にアクセスします。

## 主要URL

- **トップページ**: http://localhost:8000/
- **イベント一覧（購入者）**: http://localhost:8000/events/
- **管理画面**: http://localhost:8000/admin/
- **会員登録**: http://localhost:8000/members/register/
- **ログイン**: http://localhost:8000/members/login/
- **主催者ダッシュボード**: http://localhost:8000/organizers/dashboard/

## ディレクトリ構成

```
speckit_onlTicket2/
├── apps/                    # Djangoアプリケーション
│   ├── core/                # コア機能
│   ├── events/              # イベント管理
│   ├── seats/               # 座席管理
│   ├── orders/              # 注文・カート
│   ├── tickets/             # チケット管理
│   ├── entries/             # 入場管理
│   ├── members/             # 会員管理
│   └── organizers/          # 主催者管理
├── config/                  # Django設定
├── templates/               # HTMLテンプレート
├── static/                  # 静的ファイル
├── media/                   # アップロードファイル
├── tests/                   # テスト
├── specs/                   # 要件定義・設計
├── constitution.md          # 開発原則
└── requirements.txt         # Python依存関係
```

## 開発ワークフロー

### テストの実行

```bash
python manage.py test
```

### マイグレーションの作成

```bash
python manage.py makemigrations
python manage.py migrate
```

### 静的ファイルの収集

```bash
python manage.py collectstatic
```

## セキュリティ

- CSRF保護（Django標準）
- SQLインジェクション対策（ORM使用）
- XSS対策（テンプレート自動エスケープ）
- Brute Force攻撃対策（ログイン試行回数制限）
- QRコード署名検証（HMAC-SHA256）

## データベーススキーマ

主要テーブル:
- `venues` - 会場
- `events` - イベント
- `seats` - 座席
- `ticket_types` - チケット種別
- `carts`, `cart_items` - カート
- `orders` - 注文
- `payments` - 支払い
- `tickets` - チケット
- `entries` - 入場記録
- `cancellations` - キャンセル申請

## トラブルシューティング

### データベース接続エラー

1. PostgreSQLコンテナが起動していることを確認
2. `.env`ファイルの接続情報を確認
3. スキーマ`onlticket2`が存在することを確認

### マイグレーションエラー

```bash
python manage.py migrate --fake-initial
```

### ポート競合

```bash
python manage.py runserver 8080
```

## ライセンス

プロトタイプ実装のため、内部利用限定

## 開発者

okabe (@okab130)

## バージョン履歴

- **v1.0.0** (2026-01-11) - MVP完成
  - Phase 1-6: 基本機能実装
  - Phase 7-10: 追加機能実装
  - Phase 11: ポリッシュ完了
