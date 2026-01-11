# Quickstart Guide: TicketPro オンラインチケット販売システム MVP

**Date**: 2026-01-11  
**Status**: Completed  
**Plan Reference**: [plan.md](./plan.md)

## Overview

このドキュメントは、TicketPro MVPの開発環境セットアップ手順をまとめたものです。PostgreSQL、Django、Celery + Redisのセットアップ、初期データ投入、開発サーバー起動までを網羅しています。

---

## Prerequisites

### システム要件

- **OS**: Windows 10/11
- **Python**: 3.11以上
- **Docker**: 20.10以上（PostgreSQL用）
- **Git**: 2.30以上

### 事前準備

```powershell
# Pythonバージョン確認
python --version
# Python 3.11.0 以上

# Dockerバージョン確認
docker --version
# Docker version 20.10.0 以上

# Gitバージョン確認
git --version
# git version 2.30.0 以上
```

---

## Step 1: リポジトリのクローン

```powershell
# リポジトリをクローン
git clone https://github.com/okab130/onlticket2.git
cd onlticket2
```

---

## Step 2: PostgreSQLコンテナの起動確認

### 既存コンテナの確認

```powershell
# 既存のPostgreSQLコンテナを確認
docker ps -a --filter "name=DB"

# コンテナが停止している場合は起動
docker start DB

# コンテナが起動しているか確認
docker ps --filter "name=DB"
```

### 接続確認

```powershell
# PostgreSQLに接続
docker exec -it DB psql -U postgres

# プロト環境のスキーマ確認
\c postgres
\dn

# スキーマ一覧に onlticket2 と onlticket2_t があることを確認
# 出力例:
#   List of schemas
#   Name          | Owner
#  ---------------+----------
#   onlticket2    | postgres
#   onlticket2_t  | postgres
#   public        | postgres

\q  # 終了
```

### 新規セットアップ（既存コンテナがない場合）

```powershell
# PostgreSQLコンテナを作成・起動
docker run --name DB `
  -e POSTGRES_PASSWORD=pass `
  -p 5432:5432 `
  -d postgres:15

# スキーマ作成
docker exec -it DB psql -U postgres -c "CREATE SCHEMA IF NOT EXISTS onlticket2;"
docker exec -it DB psql -U postgres -c "CREATE SCHEMA IF NOT EXISTS onlticket2_t;"
```

---

## Step 3: Python仮想環境の作成

```powershell
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化（PowerShell）
.\venv\Scripts\Activate.ps1

# 仮想環境を有効化（コマンドプロンプト）
venv\Scripts\activate.bat

# 仮想環境が有効化されたことを確認（プロンプトに(venv)が表示される）
```

---

## Step 4: 依存関係のインストール

```powershell
# pipをアップグレード
python -m pip install --upgrade pip

# requirements.txtから依存関係をインストール
pip install -r requirements.txt
```

### requirements.txt

```txt
Django==5.2.0
psycopg2-binary==2.9.9
Pillow==10.2.0
qrcode[pil]==7.4.2
reportlab==4.0.9
celery==5.3.6
redis==5.0.1
django-axes==6.1.1
pytest==7.4.4
pytest-django==4.7.0
factory-boy==3.3.0
```

---

## Step 5: Djangoプロジェクトの初期化

### 環境変数の設定

```powershell
# .envファイルを作成（.env.exampleをコピー）
Copy-Item .env.example .env

# .envファイルを編集
notepad .env
```

### .env.example

```env
# Django設定
DJANGO_SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# データベース設定
DATABASE_NAME=postgres
DATABASE_USER=postgres
DATABASE_PASSWORD=pass
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_SCHEMA=onlticket2

# Celery設定
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# メール設定（プロトタイプではコンソール出力）
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### config/settings.py（抜粋）

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'postgres'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'pass'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
        'OPTIONS': {
            'options': f'-c search_path={os.getenv("DATABASE_SCHEMA", "onlticket2")}'
        }
    }
}
```

---

## Step 6: データベースマイグレーション

```powershell
# マイグレーションファイルを作成
python manage.py makemigrations

# マイグレーションを実行
python manage.py migrate

# マイグレーション結果を確認
python manage.py showmigrations
```

---

## Step 7: スーパーユーザーの作成

```powershell
# スーパーユーザーを作成
python manage.py createsuperuser

# 入力例:
# Username: admin
# Email: admin@example.com
# Password: admin123
# Password (again): admin123
```

---

## Step 8: 初期データの投入

### fixtures/initial_data.json（サンプル）

```json
[
  {
    "model": "events.venue",
    "pk": 1,
    "fields": {
      "name": "東京ホール",
      "address": "東京都渋谷区1-2-3",
      "capacity": 300
    }
  },
  {
    "model": "organizers.organizer",
    "pk": 1,
    "fields": {
      "user": 1,
      "organization_name": "○○イベント企画",
      "role": "admin",
      "contact_email": "organizer@example.com",
      "contact_phone": "03-1234-5678"
    }
  }
]
```

```powershell
# 初期データを投入
python manage.py loaddata fixtures/initial_data.json
```

---

## Step 9: 静的ファイルの収集

```powershell
# 静的ファイルを収集（本番環境では必須、開発環境ではオプション）
python manage.py collectstatic --noinput
```

---

## Step 10: 開発サーバーの起動

```powershell
# 開発サーバーを起動
python manage.py runserver

# ブラウザでアクセス
# http://localhost:8000/

# 管理画面にアクセス
# http://localhost:8000/admin/
# Username: admin
# Password: admin123
```

---

## Step 11: Celery + Redisのセットアップ

### Redisのインストール（Windows）

```powershell
# Chocolateyを使用してRedisをインストール
choco install redis-64

# Redisサービスを開始
redis-server

# 別のターミナルでRedis CLIを起動して確認
redis-cli ping
# 出力: PONG
```

### Celeryワーカーの起動

```powershell
# 新しいターミナルを開いて仮想環境を有効化
.\venv\Scripts\Activate.ps1

# Celeryワーカーを起動（Windows環境）
celery -A tasks worker -l info --pool=solo

# 別のターミナルでCelery Beatを起動（定期タスク用）
celery -A tasks beat -l info
```

---

## Step 12: テストの実行

```powershell
# すべてのテストを実行
pytest

# 特定のテストを実行
pytest tests/integration/test_purchase_flow.py

# カバレッジ付きで実行
pytest --cov=apps --cov-report=html

# カバレッジレポートを表示
# htmlcov/index.html をブラウザで開く
```

---

## 開発環境の動作確認

### チェックリスト

- [ ] PostgreSQLコンテナが起動している
- [ ] Djangoマイグレーションが完了している
- [ ] スーパーユーザーが作成されている
- [ ] 開発サーバーが起動している（http://localhost:8000/）
- [ ] 管理画面にログインできる（http://localhost:8000/admin/）
- [ ] Redisが起動している
- [ ] Celeryワーカーが起動している
- [ ] テストが実行できる

### 主要URL

| URL | 説明 |
|-----|------|
| http://localhost:8000/ | トップページ |
| http://localhost:8000/admin/ | Django管理画面 |
| http://localhost:8000/events/ | イベント一覧 |
| http://localhost:8000/organizer/dashboard/ | 主催者ダッシュボード |
| http://localhost:8000/mypage/ | 購入者マイページ |
| http://localhost:8000/entry/scan/ | QRコードスキャン画面 |

---

## トラブルシューティング

### PostgreSQL接続エラー

```
django.db.utils.OperationalError: FATAL:  password authentication failed
```

**解決方法**:
- .envファイルのDATABASE_PASSWORDを確認
- PostgreSQLコンテナが起動しているか確認（`docker ps`）

### マイグレーションエラー

```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**解決方法**:
```powershell
# マイグレーション履歴をクリア（開発環境のみ）
python manage.py migrate --fake-initial
```

### Celeryワーカーが起動しない（Windows）

```
ValueError: not enough values to unpack
```

**解決方法**:
```powershell
# Windows環境では --pool=solo を指定
celery -A tasks worker -l info --pool=solo
```

### Redisが起動しない

```
Could not connect to Redis at localhost:6379: Connection refused
```

**解決方法**:
```powershell
# Redisサービスを開始
redis-server

# バックグラウンドで起動する場合
redis-server --daemonize yes
```

---

## 次のステップ

1. **Phase 2へ進む**: `/speckit.tasks` でタスク分解
2. **開発開始**: User Story 1（マスタ管理）から実装
3. **継続的なテスト**: 実装後に統合テストを実行

---

## 参考リンク

- [Django公式ドキュメント](https://docs.djangoproject.com/)
- [Celery公式ドキュメント](https://docs.celeryq.dev/)
- [PostgreSQL公式ドキュメント](https://www.postgresql.org/docs/)
- [プロジェクトGitHubリポジトリ](https://github.com/okab130/onlticket2.git)

---

**Quickstart完了日**: 2026-01-11  
**次のステップ**: Phase 2（Implementation）
