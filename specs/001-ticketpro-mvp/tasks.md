# Tasks: TicketPro オンラインチケット販売システム MVP

**Input**: Design documents from `/specs/001-ticketpro-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, ui-mockups/

**Branch**: `001-ticketpro-mvp`
**Date**: 2026-01-11

**Tests**: 統合テストは主要フロー（購入フロー、入場管理）で必須。単体テストは各ユーザーストーリーで実装。

**Organization**: タスクはユーザーストーリーごとにグループ化され、各ストーリーは独立して実装・テスト可能。

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: ユーザーストーリーID（US1, US2, US3...）
- 正確なファイルパスを記載

## Path Conventions

Django monolith構造（plan.mdより）:
- `config/` - 設定
- `apps/` - Djangoアプリ（events, seats, orders, tickets, entries, members, organizers, core）
- `templates/` - テンプレート
- `static/` - 静的ファイル
- `tests/` - テスト
- `tasks/` - Celeryタスク

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクト初期化と基本構造

**推定期間**: 2日

- [ ] T001 [P] GitHubリポジトリのクローン、Pythonバージョン確認（3.11+）
- [ ] T002 [P] PostgreSQLコンテナの起動確認（docker ps --filter "name=DB"）
- [ ] T003 Python仮想環境の作成（python -m venv venv）
- [ ] T004 仮想環境の有効化（.\venv\Scripts\Activate.ps1）
- [ ] T005 pipのアップグレード（python -m pip install --upgrade pip）
- [ ] T006 requirements.txtの作成（Django 5.2+, psycopg2, Pillow, qrcode, reportlab, celery, redis, django-axes, pytest, factory-boy）
- [ ] T007 依存関係のインストール（pip install -r requirements.txt）
- [ ] T008 [P] Djangoプロジェクト初期化（django-admin startproject config .）
- [ ] T009 [P] .env.exampleファイルの作成（DATABASE, CELERY, EMAIL設定）
- [ ] T010 [P] .envファイルの作成（.env.exampleをコピー）
- [ ] T011 [P] .gitignoreファイルの作成（venv/, *.pyc, .env, media/, __pycache__/）
- [ ] T012 config/settings.pyの設定（dotenv読み込み、DATABASE設定、search_path設定）
- [ ] T013 [P] 静的ファイル設定（STATIC_URL, MEDIA_URL, STATICFILES_DIRS）
- [ ] T014 [P] テンプレート設定（TEMPLATES['DIRS']にtemplates/を追加）

**Checkpoint**: 基本プロジェクト構造が完成

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: すべてのユーザーストーリーが依存するコア機能

**⚠️ CRITICAL**: このフェーズが完了するまでユーザーストーリーの実装は開始できない

**推定期間**: 1週間

### アプリ作成

- [ ] T015 [P] apps/members/ アプリ作成（python manage.py startapp members apps/members）
- [ ] T016 [P] apps/organizers/ アプリ作成（python manage.py startapp organizers apps/organizers）
- [ ] T017 [P] apps/events/ アプリ作成（python manage.py startapp events apps/events）
- [ ] T018 [P] apps/seats/ アプリ作成（python manage.py startapp seats apps/seats）
- [ ] T019 [P] apps/orders/ アプリ作成（python manage.py startapp orders apps/orders）
- [ ] T020 [P] apps/tickets/ アプリ作成（python manage.py startapp tickets apps/tickets）
- [ ] T021 [P] apps/entries/ アプリ作成（python manage.py startapp entries apps/entries）
- [ ] T022 [P] apps/core/ アプリ作成（python manage.py startapp core apps/core）

### 基本モデル作成

- [ ] T023 [P] apps/members/models.py - Userモデル作成（AbstractUser拡張、phone_number, birth_date, failed_login_attempts追加）
- [ ] T024 [P] apps/organizers/models.py - Organizerモデル作成（user, organization_name, role, contact_email）
- [ ] T025 [P] apps/events/models.py - Venueモデル作成（name, address, capacity, seat_map_image）
- [ ] T026 apps/events/models.py - Eventモデル作成（name, description, category, venue, start_datetime, organizer, is_public）
- [ ] T027 apps/seats/models.py - Seatモデル作成（venue, block, row, number, seat_type, status, reserved_by, version）
- [ ] T028 apps/events/models.py - TicketTypeモデル作成（event, name, type, price, total_quantity, sold_quantity）

### マイグレーション

- [ ] T029 マイグレーションファイル生成（python manage.py makemigrations）
- [ ] T030 マイグレーション実行（python manage.py migrate）
- [ ] T031 スーパーユーザー作成（python manage.py createsuperuser）

### 認証・権限

- [ ] T032 apps/members/forms.py - ユーザー登録フォーム作成（UserCreationFormを継承）
- [ ] T033 apps/members/forms.py - ログインフォーム作成（AuthenticationForm）
- [ ] T034 apps/members/views.py - 登録ビュー作成（register_view）
- [ ] T035 apps/members/views.py - ログインビュー作成（login_view）
- [ ] T036 apps/members/views.py - ログアウトビュー作成（logout_view）
- [ ] T037 apps/members/urls.py - URL設定（register/, login/, logout/）
- [ ] T038 config/urls.py - members URLを追加

### 共通テンプレート

- [ ] T039 [P] templates/base.html - ベーステンプレート作成（Bootstrap 5 CDN、Alpine.js CDN、ナビゲーションバー）
- [ ] T040 [P] templates/home.html - ホームページテンプレート
- [ ] T041 [P] templates/members/register.html - 会員登録テンプレート
- [ ] T042 [P] templates/members/login.html - ログインテンプレート
- [ ] T043 [P] static/css/custom.css - カスタムCSS作成（レスポンシブ対応）

### Celery設定

- [ ] T044 tasks/celery.py - Celeryアプリケーション初期化
- [ ] T045 config/__init__.py - Celeryアプリをインポート
- [ ] T046 config/settings.py - Celery設定追加（CELERY_BROKER_URL, CELERY_RESULT_BACKEND）
- [ ] T047 tasks/email_tasks.py - メール送信タスクのスケルトン作成

### Django Admin設定

- [ ] T048 [P] apps/members/admin.py - Userモデルを管理画面に登録
- [ ] T049 [P] apps/events/admin.py - Venue, Event, TicketTypeを管理画面に登録
- [ ] T050 [P] apps/seats/admin.py - Seatモデルを管理画面に登録

**Checkpoint**: 基盤機能完成、ユーザーストーリー実装可能

---

## Phase 3: User Story 1 - イベント・会場・座席マスタ管理 (Priority: P1) 🎯 MVP

**Goal**: 主催者が会場情報、座席表、イベント、チケット種別を登録できる

**Independent Test**: 主催者が管理画面にログイン → 会場登録 → 座席表作成 → イベント登録 → チケット種別設定 → イベント公開

**推定期間**: 1週間

### 会場管理

- [ ] T051 [P] [US1] apps/events/forms.py - VenueForm作成（name, address, capacity, seat_map_image）
- [ ] T052 [US1] apps/events/views.py - VenueListView作成（主催者向け会場一覧）
- [ ] T053 [US1] apps/events/views.py - VenueCreateView作成（CreateView）
- [ ] T054 [US1] apps/events/views.py - VenueUpdateView作成（UpdateView）
- [ ] T055 [US1] apps/events/views.py - VenueDeleteView作成（DeleteView）
- [ ] T056 [P] [US1] templates/events/venue_list.html - 会場一覧テンプレート
- [ ] T057 [P] [US1] templates/events/venue_form.html - 会場登録・編集テンプレート
- [ ] T058 [US1] apps/events/urls.py - 会場管理URL設定（venues/, venues/create/, venues/<pk>/edit/, venues/<pk>/delete/）

### 座席表作成

- [ ] T059 [P] [US1] apps/seats/forms.py - SeatBulkCreateForm作成（block, seat_type, row_range, number_range）
- [ ] T060 [US1] apps/seats/views.py - SeatBulkCreateView作成（一括座席登録）
- [ ] T061 [US1] apps/seats/views.py - SeatListView作成（venue_idでフィルター）
- [ ] T062 [US1] apps/seats/views.py - SeatDeleteView作成
- [ ] T063 [US1] apps/seats/services.py - generate_seats関数作成（列・番号の範囲から座席を生成）
- [ ] T064 [P] [US1] templates/seats/seat_creation.html - 座席表作成テンプレート（ui-mockup参照）
- [ ] T065 [P] [US1] templates/seats/seat_list.html - 登録済み座席一覧テンプレート
- [ ] T066 [US1] apps/seats/urls.py - 座席管理URL設定

### イベント管理

- [ ] T067 [P] [US1] apps/events/forms.py - EventForm作成（name, description, category, venue, start_datetime, end_datetime, image, is_public）
- [ ] T068 [US1] apps/events/views.py - EventListView作成（主催者向けイベント一覧、organizer=request.userでフィルター）
- [ ] T069 [US1] apps/events/views.py - EventCreateView作成（CreateView、organizerは自動設定）
- [ ] T070 [US1] apps/events/views.py - EventUpdateView作成（UpdateView）
- [ ] T071 [US1] apps/events/views.py - EventDeleteView作成（DeleteView）
- [ ] T072 [P] [US1] templates/events/event_list.html - イベント一覧テンプレート
- [ ] T073 [P] [US1] templates/events/event_form.html - イベント登録・編集テンプレート（ui-mockup参照）
- [ ] T074 [US1] apps/events/urls.py - イベント管理URL設定

### チケット種別設定

- [ ] T075 [P] [US1] apps/events/forms.py - TicketTypeForm作成（event, name, type, price, total_quantity, sale_start, sale_end）
- [ ] T076 [US1] apps/events/views.py - TicketTypeCreateView作成（event_idからeventを取得）
- [ ] T077 [US1] apps/events/views.py - TicketTypeUpdateView作成
- [ ] T078 [US1] apps/events/views.py - TicketTypeDeleteView作成
- [ ] T079 [P] [US1] templates/events/tickettype_form.html - チケット種別フォームテンプレート

### 統合テスト

- [ ] T080 [US1] tests/integration/test_event_management.py - イベント登録フロー統合テスト（会場作成→座席作成→イベント作成→チケット種別作成）

**Checkpoint**: User Story 1完了、マスタ管理システムとして独立動作

---

## Phase 4: User Story 2 - チケット購入（座席指定） (Priority: P1) 🎯 MVP Core

**Goal**: 購入者がイベント検索、座席選択、購入確定できる

**Independent Test**: 購入者がイベント検索 → イベント詳細確認 → 座席選択 → カート追加 → 購入確定

**推定期間**: 2週間

### イベント検索・一覧

- [ ] T081 [P] [US2] apps/events/views.py - PublicEventListView作成（is_public=Trueでフィルター、検索・絞込機能）
- [ ] T082 [US2] apps/events/views.py - EventDetailView作成（購入者向けイベント詳細）
- [ ] T083 [P] [US2] templates/events/public_event_list.html - イベント一覧テンプレート（ui-mockup参照）
- [ ] T084 [P] [US2] templates/events/event_detail.html - イベント詳細テンプレート

### 座席選択UI

- [ ] T085 [US2] apps/seats/views.py - SeatSelectionView作成（event_idから座席データをJSON形式で返す）
- [ ] T086 [US2] apps/seats/services.py - get_seat_map関数作成（ビジュアル座席表用のデータ構造生成）
- [ ] T087 [P] [US2] templates/seats/seat_selection.html - 座席選択テンプレート（Alpine.js、ui-mockup参照）
- [ ] T088 [P] [US2] static/js/seat_selection.js - Alpine.jsコンポーネント作成（座席クリック、選択管理、合計金額計算）

### カート機能

- [ ] T089 [P] [US2] apps/orders/models.py - Cartモデル作成（user, created_at）またはセッション管理
- [ ] T090 [P] [US2] apps/orders/models.py - CartItemモデル作成（cart, seat, added_at）
- [ ] T091 [US2] apps/orders/views.py - AddToCartView作成（Ajax、select_for_update()で座席ロック）
- [ ] T092 [US2] apps/orders/views.py - CartView作成（カート内容表示）
- [ ] T093 [US2] apps/orders/views.py - RemoveFromCartView作成（カートから座席削除）
- [ ] T094 [P] [US2] templates/orders/cart.html - カートテンプレート
- [ ] T095 [US2] apps/orders/urls.py - カート関連URL設定

### 購入確定

- [ ] T096 [P] [US2] apps/orders/models.py - Orderモデル作成（order_number, user, event, total_amount, status）
- [ ] T097 [P] [US2] apps/orders/models.py - Paymentモデル作成（order, method, amount, status, transaction_id）
- [ ] T098 [US2] apps/orders/forms.py - CheckoutForm作成（購入者情報確認）
- [ ] T099 [US2] apps/orders/views.py - CheckoutView作成（トランザクション処理、座席ステータス更新）
- [ ] T100 [US2] apps/orders/services.py - create_order関数作成（Order, Payment, Ticket作成）
- [ ] T101 [P] [US2] templates/orders/checkout.html - 購入確認テンプレート
- [ ] T102 [P] [US2] templates/orders/purchase_complete.html - 購入完了テンプレート

### 統合テスト

- [ ] T103 [US2] tests/integration/test_purchase_flow.py - 購入フロー統合テスト（イベント検索→座席選択→カート追加→購入確定）
- [ ] T104 [US2] tests/integration/test_double_purchase_prevention.py - 二重購入防止テスト（2ユーザーが同時に同じ座席を購入）

**Checkpoint**: User Story 2完了、チケット購入システムとして独立動作

---

## Phase 5: User Story 3 - 電子チケット発行とメール送信 (Priority: P1) 🎯 MVP Core

**Goal**: 購入者がQRコード付き電子チケットを受け取れる

**Independent Test**: チケット購入完了 → QRコード生成 → PDF生成 → メール送信（コンソール） → マイページで表示

**推定期間**: 1週間

### チケットモデル

- [ ] T105 [P] [US3] apps/tickets/models.py - Ticketモデル作成（order, seat, ticket_number, qr_code, status）
- [ ] T106 [US3] apps/tickets/services.py - TicketQRService.generate_ticket_number作成
- [ ] T107 [US3] apps/tickets/services.py - TicketQRService.generate_signature作成（HMAC-SHA256）
- [ ] T108 [US3] apps/tickets/services.py - TicketQRService.generate_qr_code作成（qrcode + Pillow）
- [ ] T109 [US3] apps/tickets/services.py - TicketQRService.verify_qr_code作成（署名検証）

### PDF生成

- [ ] T110 [US3] apps/tickets/services.py - TicketPDFService.generate_ticket_pdf作成（ReportLab、QRコード埋め込み）
- [ ] T111 [P] [US3] static/fonts/ - 日本語フォント追加（IPAexGothicなど、オプション）

### メール送信

- [ ] T112 [US3] tasks/email_tasks.py - send_ticket_email タスク作成（Celery、PDF添付）
- [ ] T113 [P] [US3] templates/emails/ticket_purchase.html - チケット購入メールHTMLテンプレート
- [ ] T114 [P] [US3] templates/emails/ticket_purchase.txt - チケット購入メールテキストテンプレート

### マイページ

- [ ] T115 [US3] apps/members/views.py - MyPageView作成（購入履歴、チケット一覧）
- [ ] T116 [US3] apps/tickets/views.py - TicketDetailView作成（QRコード表示、user=request.userで認証）
- [ ] T117 [US3] apps/tickets/views.py - DownloadTicketPDFView作成（PDFダウンロード）
- [ ] T118 [P] [US3] templates/members/mypage.html - マイページテンプレート（ui-mockup参照）
- [ ] T119 [P] [US3] templates/tickets/ticket_detail.html - チケット詳細テンプレート

### Signal連携

- [ ] T120 [US3] apps/orders/signals.py - post_save Signal作成（Order作成時にTicket生成、メール送信タスク呼び出し）

### 単体テスト

- [ ] T121 [P] [US3] tests/unit/test_qr_service.py - QRコード生成・検証の単体テスト
- [ ] T122 [P] [US3] tests/unit/test_pdf_service.py - PDF生成の単体テスト

**Checkpoint**: User Story 3完了、電子チケットシステムとして独立動作

---

## Phase 6: User Story 4 - 入場管理（QRコードスキャン） (Priority: P1) 🎯 MVP Core

**Goal**: スタッフがQRコードをスキャンして入場記録を管理できる

**Independent Test**: スタッフが入場管理画面でQRコードスキャン → チケット検証 → 入場記録保存 → 重複入場チェック

**推定期間**: 1週間

### 入場記録モデル

- [ ] T123 [P] [US4] apps/entries/models.py - Entryモデル作成（ticket, gate, scanned_by, entered_at）

### QRコードスキャン

- [ ] T124 [US4] apps/entries/views.py - QRScanView作成（カメラ映像表示、QRコード認識）
- [ ] T125 [US4] apps/entries/views.py - VerifyTicketView作成（Ajax、QRコード検証、重複入場チェック）
- [ ] T126 [US4] apps/entries/services.py - verify_and_record_entry関数作成（チケット検証、Entry作成、Ticketステータス更新）
- [ ] T127 [P] [US4] templates/entries/qr_scan.html - QRスキャンテンプレート（ui-mockup参照、カメラAPI使用）
- [ ] T128 [P] [US4] static/js/qr_scanner.js - QRコードスキャンJavaScript（html5-qrcode または jsQR）

### 入場状況表示

- [ ] T129 [US4] apps/entries/views.py - EntryStatusView作成（リアルタイム入場人数、ゲート別集計）
- [ ] T130 [P] [US4] templates/entries/entry_status.html - 入場状況テンプレート

### 統合テスト

- [ ] T131 [US4] tests/integration/test_entry_flow.py - 入場管理フロー統合テスト（QRスキャン→検証→入場記録→重複入場エラー）

**Checkpoint**: User Story 4完了、入場管理システムとして独立動作

---

## Phase 7: User Story 5 - 会員管理 (Priority: P1) 🎯 MVP

**Goal**: 購入者が会員登録、ログイン、マイページで情報管理できる

**Independent Test**: 会員登録 → ログイン → マイページ確認 → 会員情報編集 → パスワード変更

**推定期間**: 1週間

### 会員情報編集

- [ ] T132 [P] [US5] apps/members/forms.py - ProfileForm作成（phone_number, birth_date）
- [ ] T133 [US5] apps/members/views.py - ProfileUpdateView作成（UpdateView）
- [ ] T134 [P] [US5] templates/members/profile_form.html - 会員情報編集テンプレート

### パスワード管理

- [ ] T135 [P] [US5] apps/members/forms.py - PasswordChangeFormWithOld作成（現在のパスワード確認）
- [ ] T136 [US5] apps/members/views.py - PasswordChangeView作成（PasswordChangeView継承）
- [ ] T137 [US5] apps/members/views.py - PasswordResetRequestView作成（メールでリセットリンク送信）
- [ ] T138 [US5] apps/members/views.py - PasswordResetConfirmView作成（新しいパスワード設定）
- [ ] T139 [P] [US5] templates/members/password_change.html - パスワード変更テンプレート
- [ ] T140 [P] [US5] templates/members/password_reset.html - パスワードリセット申請テンプレート

### Brute Force攻撃対策

- [ ] T141 [US5] django-axesの設定（config/settings.py、AXES_FAILURE_LIMIT=5）
- [ ] T142 [US5] apps/members/middleware.py - カスタムログイン試行カウント（オプション、django-axesで十分）

### 購入履歴

- [ ] T143 [US5] apps/members/views.py - PurchaseHistoryView作成（Order一覧、user=request.userでフィルター）
- [ ] T144 [P] [US5] templates/members/purchase_history.html - 購入履歴テンプレート

**Checkpoint**: User Story 5完了、会員管理システムとして独立動作

---

## Phase 8: User Story 6 - 主催者ダッシュボードと売上管理 (Priority: P2)

**Goal**: 主催者が売上サマリー、販売推移、入場状況を確認できる

**Independent Test**: 主催者がログイン → ダッシュボード表示 → 売上サマリー確認 → CSV出力

**推定期間**: 1週間

### ダッシュボード

- [ ] T145 [US6] apps/organizers/views.py - DashboardView作成（売上サマリー、販売推移グラフデータ）
- [ ] T146 [US6] apps/organizers/services.py - calculate_sales_summary関数作成（総売上、販売枚数、完売イベント数）
- [ ] T147 [US6] apps/organizers/services.py - get_sales_trend関数作成（直近30日の日次売上）
- [ ] T148 [P] [US6] templates/organizers/dashboard.html - ダッシュボードテンプレート（ui-mockup参照、Chart.jsでグラフ表示）
- [ ] T149 [P] [US6] static/js/dashboard.js - Chart.js設定（販売推移グラフ）

### 売上レポート

- [ ] T150 [US6] apps/organizers/views.py - SalesReportView作成（イベント別売上、日次・週次・月次）
- [ ] T151 [US6] apps/organizers/views.py - SalesReportCSVView作成（CSV出力）
- [ ] T152 [P] [US6] templates/organizers/sales_report.html - 売上レポートテンプレート

**Checkpoint**: User Story 6完了、主催者管理システムとして独立動作

---

## Phase 9: User Story 7 - 自由席チケット購入 (Priority: P2)

**Goal**: 購入者が自由席チケットを購入できる（座席選択なし）

**Independent Test**: イベント検索 → 自由席イベント詳細 → 枚数指定 → カート追加 → 購入確定

**推定期間**: 3日

### 自由席購入フロー

- [ ] T153 [US7] apps/events/views.py - EventDetailViewを拡張（自由席の場合は枚数選択UIを表示）
- [ ] T154 [US7] apps/orders/views.py - AddToCartViewを拡張（自由席の場合はseat=Nullでチケット作成）
- [ ] T155 [P] [US7] templates/events/event_detail.html - 自由席枚数選択UI追加

**Checkpoint**: User Story 7完了、自由席購入システムとして独立動作

---

## Phase 10: User Story 8 - キャンセル・返金処理 (Priority: P3)

**Goal**: 購入者がチケットをキャンセルでき、座席が再販売可能になる

**Independent Test**: マイページ → キャンセル申請 → 主催者承認 → 座席ステータス更新 → 返金記録

**推定期間**: 1週間

### キャンセルモデル

- [ ] T156 [P] [US8] apps/orders/models.py - Cancellationモデル作成（order, reason, refund_amount, status, requested_at, processed_at）

### キャンセル申請

- [ ] T157 [US8] apps/orders/views.py - CancellationRequestView作成（キャンセル申請フォーム）
- [ ] T158 [P] [US8] templates/orders/cancellation_request.html - キャンセル申請テンプレート

### キャンセル承認

- [ ] T159 [US8] apps/organizers/views.py - CancellationApprovalView作成（主催者が承認/却下）
- [ ] T160 [US8] apps/orders/services.py - process_cancellation関数作成（Order, Ticket, Seatのステータス更新、返金記録）
- [ ] T161 [P] [US8] templates/organizers/cancellation_list.html - キャンセル申請一覧テンプレート

### メール通知

- [ ] T162 [US8] tasks/email_tasks.py - send_cancellation_email タスク作成

**Checkpoint**: User Story 8完了、キャンセル管理システムとして独立動作

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: すべてのユーザーストーリーに影響する改善

**推定期間**: 1週間

### ドキュメント

- [ ] T163 [P] README.md更新（プロジェクト概要、セットアップ手順、使用方法）
- [ ] T164 [P] docs/USER_MANUAL.md作成（利用者マニュアル）
- [ ] T165 [P] docs/OPERATION_MANUAL.md作成（運用手順書）

### コード品質

- [ ] T166 [P] コードリファクタリング（DRY原則、重複コード削除）
- [ ] T167 N+1問題の確認（Django Debug Toolbarでクエリ確認）
- [ ] T168 [P] 未使用コードの削除

### パフォーマンス最適化

- [ ] T169 select_related / prefetch_relatedの最適化
- [ ] T170 [P] 静的ファイルの圧縮（CSS, JS minify）
- [ ] T171 画像最適化（Pillow、サムネイル生成）

### セキュリティ監査

- [ ] T172 Django Security Checklist実行（python manage.py check --deploy）
- [ ] T173 [P] HTTPS設定確認（本番環境用）
- [ ] T174 [P] 環境変数の確認（SECRET_KEY、DATABASE_PASSWORD）

### 統合テスト

- [ ] T175 主要フロー統合テスト実行（pytest tests/integration/）
- [ ] T176 カバレッジ確認（pytest --cov=apps）

### quickstart.md検証

- [ ] T177 quickstart.mdの手順を最初から実行して動作確認
- [ ] T178 トラブルシューティングセクション更新

**Checkpoint**: すべてのユーザーストーリーが統合され、MVP完成

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし、即座に開始可能
- **Phase 2 (Foundational)**: Phase 1に依存、**すべてのユーザーストーリーをブロック**
- **Phase 3-10 (User Stories)**: Phase 2に依存
  - Phase 3 (US1) → Phase 2完了後に開始可能、他のストーリーに依存なし
  - Phase 4 (US2) → Phase 3 (US1)に依存（Event, Seatが必要）
  - Phase 5 (US3) → Phase 4 (US2)に依存（Order, Ticketが必要）
  - Phase 6 (US4) → Phase 5 (US3)に依存（QRコード付きTicketが必要）
  - Phase 7 (US5) → Phase 2に依存、Phase 3-6と並行可能
  - Phase 8 (US6) → Phase 3-5に依存（売上データが必要）
  - Phase 9 (US7) → Phase 3, 5に依存
  - Phase 10 (US8) → Phase 4に依存
- **Phase 11 (Polish)**: 必要なユーザーストーリー完了後に開始

### Recommended Implementation Sequence

1. **Phase 1**: Setup（2日）
2. **Phase 2**: Foundational（1週間）**CRITICAL BLOCKER**
3. **Phase 3**: US1 - マスタ管理（1週間）
4. **Phase 4**: US2 - チケット購入（2週間）**MVP Core**
5. **Phase 5**: US3 - 電子チケット発行（1週間）**MVP Core**
6. **Phase 6**: US4 - 入場管理（1週間）**MVP Core**
7. **Phase 7**: US5 - 会員管理（1週間）- Phase 3-6と並行可能
8. **Phase 8**: US6 - 主催者ダッシュボード（1週間）- P2
9. **Phase 9**: US7 - 自由席チケット（3日）- P2
10. **Phase 10**: US8 - キャンセル・返金（1週間）- P3
11. **Phase 11**: Polish & Testing（1週間）

**Total Estimated Duration**: 10-12週間

### Parallel Opportunities

- Phase 1のすべての[P]タスクは並行実行可能
- Phase 2のアプリ作成（T015-T022）は並行実行可能
- Phase 2の基本モデル作成（T023-T028）は並行実行可能
- Phase 7 (US5)はPhase 3-6と並行実行可能（異なるアプリ）

---

## Task Summary

| Phase | Tasks | Duration | Priority |
|-------|-------|----------|----------|
| Phase 1: Setup | T001-T014 (14 tasks) | 2日 | - |
| Phase 2: Foundational | T015-T050 (36 tasks) | 1週間 | **BLOCKER** |
| Phase 3: US1 | T051-T080 (30 tasks) | 1週間 | P1 |
| Phase 4: US2 | T081-T104 (24 tasks) | 2週間 | P1 |
| Phase 5: US3 | T105-T122 (18 tasks) | 1週間 | P1 |
| Phase 6: US4 | T123-T131 (9 tasks) | 1週間 | P1 |
| Phase 7: US5 | T132-T144 (13 tasks) | 1週間 | P1 |
| Phase 8: US6 | T145-T152 (8 tasks) | 1週間 | P2 |
| Phase 9: US7 | T153-T155 (3 tasks) | 3日 | P2 |
| Phase 10: US8 | T156-T162 (7 tasks) | 1週間 | P3 |
| Phase 11: Polish | T163-T178 (16 tasks) | 1週間 | - |

**Total Tasks**: 178

---

**Next Steps**: Phase 1（Setup）のT001から順次実行してください。
