# Implementation Plan: TicketPro オンラインチケット販売システム MVP

**Branch**: `001-ticketpro-mvp` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ticketpro-mvp/spec.md`

## Summary

TicketPro は、イベントチケットのオンライン販売、座席管理、入場管理、売上管理を実現するDjangoベースのWebアプリケーションです。主催者がイベント・会場・座席を登録し、購入者が座席指定または自由席チケットを購入、QRコード付き電子チケットを受け取り、入場時にスキャンする一連のフローを提供します。

**技術的アプローチ**: Django 5.2 + PostgreSQL + Django ORM によるデータモデル中心設計。トランザクション制御により座席の二重販売を防止。Bootstrap + Alpine.js でレスポンシブUI。Celery + Redis で非同期メール送信。Django標準のセキュリティ機能（CSRF、SQLインジェクション、XSS対策、Brute force対策）を活用。

## Technical Context

**Language/Version**: Python 3.11+, Django 5.2+ (LTS)
**Primary Dependencies**: 
  - Django 5.2+
  - psycopg2 (PostgreSQL adapter)
  - Pillow (画像処理、QRコード生成)
  - qrcode (QRコード生成)
  - reportlab (PDF生成)
  - celery (非同期処理)
  - redis (Celeryバックエンド)
  - Bootstrap 5 (CSS framework)
  - Alpine.js (軽量JavaScript framework)

**Storage**: PostgreSQL 15+
  - プロト環境: DB名:postgres, schema:onlticket2
  - 単体テスト環境: DB名:postgres, schema:onlticket2_t
  - Docker コンテナ名:DB（既に稼働中）

**Testing**: 
  - pytest + pytest-django (単体テスト、統合テスト)
  - Django TestCase (モデル、ビュー、フォームのテスト)
  - Selenium (E2Eテスト - オプション)

**Target Platform**: ローカル開発環境（Windows）、プロトタイプフェーズ

**Project Type**: Web application (Django monolith with frontend templates)

**Performance Goals**: 
  - 画面表示: 3秒以内
  - 決済処理: 5秒以内
  - 座席仮予約タイムアウト: 10分間
  - N+1問題の回避（select_related、prefetch_related活用）

**Constraints**: 
  - プロトタイプフェーズのため、本番環境へのデプロイは不要
  - 決済はプロトタイプでは簡易実装（実際の決済API連携なし）
  - メール送信はコンソール出力（SMTP連携なし）
  - ローカル環境での動作を前提

**Scale/Scope**: 
  - 月間イベント数: 200件
  - 月間チケット販売枚数: 10,000枚
  - 想定ユーザー数: イベント主催者100社、購入者10,000名/月

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. データモデル中心アプローチ (NON-NEGOTIABLE)
- ✅ 主要エンティティ定義済み: Venue, Seat, Event, TicketType, Member, Order, Ticket, Payment, Entry, Organizer, Cancellation
- ✅ 運用フローから設定・参照タイミングを確認済み（spec.mdのユーザーストーリー）
- ✅ データ整合性要件明確: 二重販売防止（FR-043）、カートタイムアウト（FR-044）

### ✅ II. UI/UX実装前検証 (NON-NEGOTIABLE)
- ⚠️ 画面モック未作成 → **Phase 1で作成必須**
- ✅ 画面イベントと機能の対応関係は spec.md Acceptance Scenarios で定義済み
- ✅ レスポンシブデザイン要件明確（Bootstrap 5使用）

### ✅ III. 品質・保守性・安全性の追求
- ✅ プロトタイプでも最低限の品質基準を維持（セキュリティ、エラーハンドリング、テスト）
- ✅ 技術的負債の明示的記録（コメントまたはドキュメント）
- ✅ DRY原則、意味のある命名規約

### ✅ IV. エラーハンドリングの原則
- ✅ 根本原因の修正方針
- ✅ 明確なエラーメッセージ（spec.md Edge Cases参照）
- ✅ 外部API/ネットワーク失敗考慮（決済エラー、メール送信エラー）

### ✅ V. コード品質の基準
- ✅ DRY原則、意味のある命名
- ✅ Django標準のコーディングスタイル準拠

### ✅ VI. テスト規律
- ✅ 主要フローの統合テスト必須（購入フロー、入場管理）
- ✅ 振る舞いのテスト（Acceptance Scenarios ベース）
- ✅ 単体テスト環境準備済み（schema:onlticket2_t）

### ✅ VII. セキュリティの考え方 (NON-NEGOTIABLE)
- ✅ Django標準セキュリティ機能活用（CSRF、SQLインジェクション、XSS、Brute force対策）
- ✅ 環境変数での機密情報管理（settings.py）
- ✅ アクセス制御（購入者間の情報参照禁止、FR-049）

### 未解決事項
- ⚠️ **Phase 1で解決必須**: 画面モックの作成とレビュー
- ⚠️ **Phase 1で解決必須**: カート仮予約タイムアウトの実装方法（Celery Beatまたはデータベーストリガー）

## Project Structure

### Documentation (this feature)

```text
specs/001-ticketpro-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - Django best practices, transaction control, QR code generation
├── data-model.md        # Phase 1 output - ER diagram, model definitions, relationships
├── quickstart.md        # Phase 1 output - Development setup, database schema creation, running the app
├── contracts/           # Phase 1 output - API contracts (if REST API needed)
│   ├── event-api.md     # Event management endpoints
│   ├── ticket-api.md    # Ticket purchase endpoints
│   └── entry-api.md     # Entry management endpoints
├── ui-mockups/          # Phase 1 output - Screen mockups (NON-NEGOTIABLE)
│   ├── organizer/       # 主催者向け画面
│   └── customer/        # 購入者向け画面
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
onlticket2/                      # Django project root
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
│
├── config/                      # Project settings
│   ├── __init__.py
│   ├── settings.py              # Main settings (split into base/dev/prod later)
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI config
│   └── asgi.py                  # ASGI config (for Celery)
│
├── apps/                        # Django apps
│   ├── events/                  # イベント・会場管理
│   │   ├── models.py            # Venue, Event, TicketType models
│   │   ├── views.py             # Event list, detail, create views
│   │   ├── forms.py             # Event forms
│   │   ├── urls.py              # Event URLs
│   │   ├── admin.py             # Django admin config
│   │   └── templates/events/    # Event templates
│   │
│   ├── seats/                   # 座席管理
│   │   ├── models.py            # Seat model
│   │   ├── views.py             # Seat selection views
│   │   ├── urls.py              # Seat URLs
│   │   └── templates/seats/     # Seat templates
│   │
│   ├── orders/                  # 注文・決済管理
│   │   ├── models.py            # Order, Payment models
│   │   ├── views.py             # Cart, checkout views
│   │   ├── forms.py             # Order forms
│   │   ├── urls.py              # Order URLs
│   │   └── templates/orders/    # Order templates
│   │
│   ├── tickets/                 # チケット管理
│   │   ├── models.py            # Ticket model
│   │   ├── views.py             # Ticket display, download views
│   │   ├── services.py          # QR code generation, PDF generation
│   │   ├── urls.py              # Ticket URLs
│   │   └── templates/tickets/   # Ticket templates
│   │
│   ├── entries/                 # 入場管理
│   │   ├── models.py            # Entry model
│   │   ├── views.py             # QR scan, entry record views
│   │   ├── urls.py              # Entry URLs
│   │   └── templates/entries/   # Entry templates
│   │
│   ├── members/                 # 会員管理
│   │   ├── models.py            # Member model (extends User)
│   │   ├── views.py             # Registration, login, profile views
│   │   ├── forms.py             # Registration, login forms
│   │   ├── urls.py              # Member URLs
│   │   └── templates/members/   # Member templates
│   │
│   ├── organizers/              # 主催者管理
│   │   ├── models.py            # Organizer model
│   │   ├── views.py             # Dashboard, sales report views
│   │   ├── urls.py              # Organizer URLs
│   │   └── templates/organizers/ # Organizer templates
│   │
│   └── core/                    # 共通機能
│       ├── middleware.py        # Custom middleware (logging, auth)
│       ├── utils.py             # Utility functions
│       └── templates/core/      # Base templates, common components
│
├── static/                      # Static files
│   ├── css/                     # Bootstrap, custom CSS
│   ├── js/                      # Alpine.js, custom JS
│   └── images/                  # Images, icons
│
├── media/                       # User-uploaded files
│   ├── event_images/            # Event images
│   ├── seat_maps/               # Seat map images
│   └── tickets/                 # Generated ticket PDFs
│
├── templates/                   # Global templates
│   ├── base.html                # Base template
│   ├── home.html                # Home page
│   └── errors/                  # Error pages (404, 500)
│
├── tests/                       # Tests
│   ├── conftest.py              # Pytest configuration
│   ├── factories.py             # Factory Boy factories for test data
│   ├── integration/             # Integration tests
│   │   ├── test_purchase_flow.py
│   │   ├── test_entry_flow.py
│   │   └── test_cancellation_flow.py
│   ├── unit/                    # Unit tests
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_services.py
│   │   └── test_forms.py
│   └── contract/                # API contract tests (if REST API)
│       └── test_event_api.py
│
├── tasks/                       # Celery tasks
│   ├── __init__.py
│   ├── celery.py                # Celery configuration
│   ├── email_tasks.py           # Email sending tasks
│   └── cleanup_tasks.py         # Cart timeout cleanup tasks
│
└── docs/                        # Documentation
    ├── README.md                # Project overview
    ├── SETUP.md                 # Development setup
    ├── API.md                   # API documentation (if REST API)
    └── DEPLOYMENT.md            # Deployment guide (for future)
```

**Structure Decision**: Django monolith (web application) を選択。理由：
- プロトタイプフェーズでは、シンプルなモノリシック構造が適切
- Django Appsで機能を分割し、保守性を確保
- フロントエンドはDjango Templatesで実装（SPA不要）
- 将来的にREST API化する場合は、apps/以下にAPIビューを追加

## Complexity Tracking

> **Constitution Check violations that must be justified**

なし。すべての原則に準拠しています。

## Phase 0: Research Topics

### 必須調査項目

1. **Django Transaction Control**
   - Djangoでのトランザクション制御方法（`transaction.atomic()`）
   - 座席の二重販売防止（楽観的ロックまたは悲観的ロック）
   - カート仮予約のタイムアウト実装（Celery Beat または データベーストリガー）

2. **QR Code Generation in Django**
   - qrcodeライブラリの使用方法
   - QRコードに含める情報（チケット番号、署名）
   - QRコードのセキュリティ（改ざん防止）

3. **PDF Generation in Django**
   - reportlabまたはWeasyPrintの選定
   - チケットPDFのレイアウト設計
   - QRコードをPDFに埋め込む方法

4. **Celery + Redis Setup**
   - Celeryの設定方法（tasks/, celery.py）
   - Redisのインストールと設定
   - 非同期メール送信タスクの実装
   - Celery Beatでの定期タスク（カートクリーンアップ）

5. **Django Security Best Practices**
   - CSRF対策の確認（Django標準）
   - SQLインジェクション対策（ORM使用）
   - XSS対策（テンプレート自動エスケープ）
   - Brute force対策（django-axes または カスタム実装）

6. **N+1 Problem Prevention**
   - select_relatedの使い方（1対1、多対1リレーション）
   - prefetch_relatedの使い方（多対多、逆参照）
   - Django Debug Toolbarでのクエリ確認

7. **Responsive UI with Bootstrap + Alpine.js**
   - Bootstrap 5の導入方法
   - Alpine.jsの基本的な使い方（座席選択UIに活用）
   - Django Templatesとの統合

8. **Django Testing Best Practices**
   - pytest-djangoのセットアップ
   - Factory Boyでのテストデータ生成
   - TransactionTestCaseの使い方（トランザクションテスト）
   - Seleniumでのブラウザテスト（オプション）

### 調査成果物
- `specs/001-ticketpro-mvp/research.md` に調査結果をまとめる
- コード例、ライブラリ選定理由、実装方針を記載

## Phase 1: Design & Contracts

### 必須成果物

1. **data-model.md**
   - ER図（主要11エンティティの関係性）
   - 各モデルのフィールド定義（Django model fields）
   - インデックス設計
   - マイグレーション計画

2. **quickstart.md**
   - 開発環境のセットアップ手順
   - PostgreSQLコンテナの起動確認
   - Djangoプロジェクトの初期化
   - データベースマイグレーション
   - 初期データの投入（会場、イベント、テストユーザー）
   - 開発サーバーの起動方法

3. **ui-mockups/** (NON-NEGOTIABLE)
   - 主催者向け画面モック
     - イベント登録画面
     - 座席表作成画面
     - ダッシュボード
   - 購入者向け画面モック
     - イベント一覧・検索
     - イベント詳細
     - 座席選択画面（ビジュアル座席表）
     - カート画面
     - 購入完了画面
     - マイページ
   - 入場管理画面モック
     - QRコードスキャン画面

4. **contracts/** (if REST API needed)
   - イベント管理API
   - チケット購入API
   - 入場管理API
   - 認証API

### Phase 1 完了条件
- ✅ データモデル設計完了、レビュー済み
- ✅ 画面モック作成完了、レビュー済み（NON-NEGOTIABLE）
- ✅ quickstart.md作成完了、開発環境セットアップ成功
- ✅ Constitution Check再実施、全項目クリア

## Phase 2: Task Breakdown

Phase 1完了後、`/speckit.tasks` コマンドで詳細タスクを生成します。

### 想定タスク構成（概要）

**Phase 2.1: Setup（環境構築）**
- Djangoプロジェクト初期化
- 依存関係インストール
- PostgreSQL接続設定
- 静的ファイル設定

**Phase 2.2: Foundational（基盤機能）**
- 基本モデル作成（Venue, Event, Seat, TicketType, Member, Organizer）
- 認証機能（会員登録、ログイン、パスワードリセット）
- 共通テンプレート（base.html）

**Phase 2.3: User Story 1 - マスタ管理（P1）**
- 会場登録機能
- 座席表作成機能
- イベント登録機能
- チケット種別設定機能

**Phase 2.4: User Story 2 - チケット購入（座席指定）（P1）**
- イベント検索・一覧表示
- イベント詳細表示
- 座席選択画面（ビジュアル座席表）
- カート機能
- 購入手続き（決済簡易実装）

**Phase 2.5: User Story 3 - 電子チケット発行（P1）**
- QRコード生成サービス
- チケットPDF生成サービス
- メール送信タスク（Celery）
- マイページ（チケット表示・ダウンロード）

**Phase 2.6: User Story 4 - 入場管理（P1）**
- QRコードスキャン機能
- 入場記録保存
- 重複入場チェック
- 入場状況リアルタイム表示

**Phase 2.7: User Story 5 - 会員管理（P1）**
- 会員登録・ログイン
- マイページ（購入履歴、チケット一覧）
- 会員情報編集
- パスワードリセット
- Brute force対策

**Phase 2.8: User Story 6 - 主催者ダッシュボード（P2）**
- ダッシュボード（売上サマリー）
- イベント別売上
- 販売推移グラフ
- CSV出力

**Phase 2.9: User Story 7 - 自由席チケット購入（P2）**
- 自由席チケット購入フロー
- 自由席チケット発行

**Phase 2.10: User Story 8 - キャンセル・返金（P3）**
- キャンセル申請機能
- キャンセル承認機能
- 座席ステータス更新
- 返金記録

**Phase 2.11: Polish & Cross-Cutting Concerns**
- ドキュメント更新
- コードリファクタリング
- パフォーマンス最適化（N+1問題確認）
- セキュリティ監査
- 統合テスト
- quickstart.md検証

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 0 (Research)**: No dependencies - can start immediately
- **Phase 1 (Design)**: Depends on Phase 0 completion - BLOCKS Phase 2
- **Phase 2 (Implementation)**: Depends on Phase 1 completion
  - Phase 2.1 (Setup) must complete first
  - Phase 2.2 (Foundational) depends on Phase 2.1 - BLOCKS all user stories
  - User Stories (Phase 2.3-2.10) depend on Phase 2.2
  - User Stories can proceed in priority order (P1 → P2 → P3)
  - Phase 2.11 (Polish) depends on desired user stories completion

### User Story Dependencies
- **User Story 1 (P1)**: Depends on Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 (needs Event, Seat) - Can integrate after US1 completion
- **User Story 3 (P1)**: Depends on User Story 2 (needs Order, Ticket) - Can integrate after US2 completion
- **User Story 4 (P1)**: Depends on User Story 3 (needs Ticket with QR code) - Can integrate after US3 completion
- **User Story 5 (P1)**: Depends on Foundational - Can proceed in parallel with US1-4
- **User Story 6 (P2)**: Depends on US1-5 (needs sales data) - Can proceed after US1-5 completion
- **User Story 7 (P2)**: Depends on US1, US3 (similar to US2 but simpler) - Can proceed after US1, US3
- **User Story 8 (P3)**: Depends on US2 (needs Order, Ticket) - Can proceed after US2 completion

### Recommended Implementation Sequence
1. **Phase 0**: Research (1 week)
2. **Phase 1**: Design & Mockups (1 week)
3. **Phase 2.1**: Setup (2 days)
4. **Phase 2.2**: Foundational (1 week)
5. **Phase 2.3**: User Story 1 - マスタ管理 (1 week)
6. **Phase 2.4**: User Story 2 - チケット購入（座席指定） (2 weeks) - **MVP Core**
7. **Phase 2.5**: User Story 3 - 電子チケット発行 (1 week) - **MVP Core**
8. **Phase 2.6**: User Story 4 - 入場管理 (1 week) - **MVP Core**
9. **Phase 2.7**: User Story 5 - 会員管理 (1 week) - Can parallelize with US1-4
10. **Phase 2.8**: User Story 6 - 主催者ダッシュボード (1 week) - P2
11. **Phase 2.9**: User Story 7 - 自由席チケット購入 (3 days) - P2
12. **Phase 2.10**: User Story 8 - キャンセル・返金 (1 week) - P3
13. **Phase 2.11**: Polish & Testing (1 week)

**Total Estimated Duration**: 10-12 weeks

## Next Steps

1. ✅ **Constitution Check passed** - Proceed to Phase 0
2. 🔍 **Phase 0**: Run `/speckit.plan` to generate `research.md`
   - Research Django transaction control, QR code generation, PDF generation, Celery setup
3. 🎨 **Phase 1**: Run `/speckit.plan` to generate `data-model.md`, `quickstart.md`, `ui-mockups/`
   - **CRITICAL**: Create and review UI mockups (NON-NEGOTIABLE)
4. 📋 **Phase 2**: Run `/speckit.tasks` to generate `tasks.md`
   - Detailed task breakdown with checkboxes
5. 🚀 **Implementation**: Start Phase 2.1 (Setup)

---

**Note**: このプランは Constitution に準拠し、データモデル中心アプローチ、UI/UX実装前検証、品質・保守性・安全性の追求を実現します。Phase 1での画面モック作成とレビューは必須です。
