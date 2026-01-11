# TicketPro オンラインチケット販売システム - プロジェクトチェックリスト

**プロジェクト**: TicketPro MVP  
**作成日**: 2026-01-11  
**最終更新**: 2026-01-11  
**ステータス**: Phase 1 完了 → Phase 2 実装中

---

## 📊 プロジェクト全体進捗

| フェーズ | ステータス | 完了率 | 備考 |
|---------|----------|--------|------|
| Phase 0: Research | ✅ 完了 | 100% | 調査完了 |
| Phase 1: Design & Contracts | ✅ 完了 | 100% | データモデル、UI Mockup完了 |
| Phase 2: Implementation | 🚧 進行中 | 約60% | Setup & Foundational完了 |
| Phase 3: Testing & Polish | ⏳ 未開始 | 0% | - |

---

## Phase 0: Research ✅ **完了**

### 調査項目
- [x] Django Transaction Control（トランザクション制御）
- [x] QRコード生成（qrcodeライブラリ）
- [x] PDF生成（ReportLab）
- [x] Celery + Redis Setup（非同期処理）
- [x] Django Security Best Practices
- [x] N+1問題防止（select_related, prefetch_related）
- [x] Bootstrap 5 + Alpine.js（レスポンシブUI）
- [x] pytest-django（テスト環境）

**成果物**: `specs/001-ticketpro-mvp/research.md`

---

## Phase 1: Design & Contracts ✅ **完了**

### データモデル設計
- [x] 11エンティティのER図作成
- [x] 各モデルのフィールド定義
- [x] リレーション設計
- [x] インデックス戦略策定
- [x] マイグレーション計画

**成果物**: `specs/001-ticketpro-mvp/data-model.md`

### UI Mockups（NON-NEGOTIABLE）
- [x] 主催者向け画面（3画面）
  - [x] イベント登録画面
  - [x] 座席表作成画面
  - [x] ダッシュボード
- [x] 購入者向け画面（3画面）
  - [x] イベント一覧・検索画面
  - [x] 座席選択画面
  - [x] マイページ
- [x] 入場管理画面（1画面）
  - [x] QRコードスキャン画面

**成果物**: `specs/001-ticketpro-mvp/ui-mockups/`

### Quickstart Guide
- [x] 開発環境セットアップ手順
- [x] PostgreSQL接続設定
- [x] Djangoプロジェクト初期化
- [x] マイグレーション実行
- [x] 初期データ投入
- [x] Celery + Redis設定

**成果物**: `specs/001-ticketpro-mvp/quickstart.md`

### Constitution Check
- [x] データモデル中心アプローチ確認
- [x] UI/UX実装前検証完了
- [x] 品質・保守性・安全性の確認

---

## Phase 2: Implementation 🚧 **進行中**

### Phase 2.1: Setup（環境構築）✅ **完了**

- [x] T001 GitHubリポジトリのクローン
- [x] T002 PostgreSQLコンテナの起動確認（コンテナ名: db）
- [x] T003 Python仮想環境の作成
- [x] T004 仮想環境の有効化
- [x] T005 pipのアップグレード
- [x] T006 requirements.txtの作成
- [x] T007 依存関係のインストール
- [x] T008 Djangoプロジェクト初期化
- [x] T009 .env.exampleファイルの作成
- [x] T010 .envファイルの作成
- [x] T011 .gitignoreファイルの作成
- [x] T012 config/settings.pyの設定
- [x] T013 静的ファイル設定
- [x] T014 テンプレート設定

**ステータス**: ✅ 完了（14/14タスク）

---

### Phase 2.2: Foundational（基盤機能）✅ **完了**

#### アプリ作成
- [x] T015 apps/members/ アプリ作成
- [x] T016 apps/organizers/ アプリ作成
- [x] T017 apps/events/ アプリ作成
- [x] T018 apps/seats/ アプリ作成
- [x] T019 apps/orders/ アプリ作成
- [x] T020 apps/tickets/ アプリ作成
- [x] T021 apps/entries/ アプリ作成
- [x] T022 apps/core/ アプリ作成

#### 基本モデル作成
- [x] T023 Userモデル作成（AbstractUser拡張）
- [x] T024 Organizerモデル作成
- [x] T025 Venueモデル作成
- [x] T026 Eventモデル作成
- [x] T027 Seatモデル作成
- [x] T028 TicketTypeモデル作成

#### マイグレーション
- [x] T029 マイグレーションファイル生成
- [x] T030 マイグレーション実行
- [x] T031 スーパーユーザー作成

#### 認証・権限
- [x] T032 ユーザー登録フォーム作成
- [x] T033 ログインフォーム作成
- [x] T034 登録ビュー作成
- [x] T035 ログインビュー作成
- [x] T036 ログアウトビュー作成
- [x] T037 members URL設定
- [x] T038 config/urls.pyにmembers URL追加

#### 共通テンプレート
- [x] T039 templates/base.html作成
- [x] T040 templates/home.html作成
- [x] T041 templates/members/register.html作成
- [x] T042 templates/members/login.html作成
- [x] T043 static/css/custom.css作成

#### Celery設定
- [x] T044 tasks/celery.py作成
- [x] T045 config/__init__.pyにCeleryインポート
- [x] T046 config/settings.pyにCelery設定追加
- [x] T047 tasks/email_tasks.pyスケルトン作成

#### Django Admin設定
- [x] T048 Userモデルを管理画面に登録
- [x] T049 Venue, Event, TicketTypeを管理画面に登録
- [x] T050 Seatモデルを管理画面に登録

**ステータス**: ✅ 完了（36/36タスク）

---

### Phase 2.3: User Story 1 - マスタ管理（P1）🎯 MVP

**目標**: 主催者が会場・座席・イベント・チケット種別を登録できる

#### 会場管理
- [ ] T051 apps/events/forms.py - VenueForm作成
- [ ] T052 apps/events/views.py - VenueListView作成
- [ ] T053 apps/events/views.py - VenueCreateView作成
- [ ] T054 apps/events/views.py - VenueUpdateView作成
- [ ] T055 apps/events/views.py - VenueDeleteView作成
- [ ] T056 templates/events/venue_list.html作成
- [ ] T057 templates/events/venue_form.html作成
- [ ] T058 apps/events/urls.py - 会場管理URL設定

#### 座席表作成
- [ ] T059 apps/seats/forms.py - SeatBulkCreateForm作成
- [ ] T060 apps/seats/views.py - SeatBulkCreateView作成
- [ ] T061 apps/seats/views.py - SeatListView作成
- [ ] T062 apps/seats/views.py - SeatDeleteView作成
- [ ] T063 apps/seats/services.py - generate_seats関数作成
- [ ] T064 templates/seats/seat_creation.html作成
- [ ] T065 templates/seats/seat_list.html作成
- [ ] T066 apps/seats/urls.py設定

#### イベント管理
- [ ] T067 apps/events/forms.py - EventForm作成
- [ ] T068 apps/events/views.py - EventListView作成
- [ ] T069 apps/events/views.py - EventCreateView作成
- [ ] T070 apps/events/views.py - EventUpdateView作成
- [ ] T071 apps/events/views.py - EventDeleteView作成
- [ ] T072 templates/events/event_list.html作成
- [ ] T073 templates/events/event_form.html作成
- [ ] T074 apps/events/urls.py設定

#### チケット種別設定
- [ ] T075 apps/events/forms.py - TicketTypeForm作成
- [ ] T076 apps/events/views.py - TicketTypeCreateView作成
- [ ] T077 apps/events/views.py - TicketTypeUpdateView作成
- [ ] T078 apps/events/views.py - TicketTypeDeleteView作成
- [ ] T079 templates/events/tickettype_form.html作成

#### 統合テスト
- [ ] T080 tests/integration/test_event_management.py作成

**ステータス**: ⏳ 未開始（0/30タスク）

---

### Phase 2.4: User Story 2 - チケット購入（座席指定）（P1）🎯 MVP Core

**目標**: 購入者がイベント検索、座席選択、購入確定できる

#### イベント検索・一覧
- [ ] T081 apps/events/views.py - PublicEventListView作成
- [ ] T082 apps/events/views.py - EventDetailView作成
- [ ] T083 templates/events/public_event_list.html作成
- [ ] T084 templates/events/event_detail.html作成

#### 座席選択UI
- [ ] T085 apps/seats/views.py - SeatSelectionView作成
- [ ] T086 apps/seats/services.py - get_seat_map関数作成
- [ ] T087 templates/seats/seat_selection.html作成
- [ ] T088 static/js/seat_selection.js作成（Alpine.js）

#### カート機能
- [ ] T089 apps/orders/models.py - Cart/CartItemモデル作成
- [ ] T090 apps/orders/models.py - CartItemモデル作成
- [ ] T091 apps/orders/views.py - AddToCartView作成
- [ ] T092 apps/orders/views.py - CartView作成
- [ ] T093 apps/orders/views.py - RemoveFromCartView作成
- [ ] T094 templates/orders/cart.html作成
- [ ] T095 apps/orders/urls.py設定

#### 購入確定
- [ ] T096 apps/orders/models.py - Orderモデル作成
- [ ] T097 apps/orders/models.py - Paymentモデル作成
- [ ] T098 apps/orders/forms.py - CheckoutForm作成
- [ ] T099 apps/orders/views.py - CheckoutView作成
- [ ] T100 apps/orders/services.py - create_order関数作成
- [ ] T101 templates/orders/checkout.html作成
- [ ] T102 templates/orders/purchase_complete.html作成

#### 統合テスト
- [ ] T103 tests/integration/test_purchase_flow.py作成
- [ ] T104 tests/integration/test_double_purchase_prevention.py作成

**ステータス**: ⏳ 未開始（0/24タスク）

---

### Phase 2.5: User Story 3 - 電子チケット発行（P1）🎯 MVP Core

**目標**: 購入者がQRコード付き電子チケットを受け取れる

#### チケットモデル
- [ ] T105 apps/tickets/models.py - Ticketモデル作成
- [ ] T106 apps/tickets/services.py - generate_ticket_number作成
- [ ] T107 apps/tickets/services.py - generate_signature作成
- [ ] T108 apps/tickets/services.py - generate_qr_code作成
- [ ] T109 apps/tickets/services.py - verify_qr_code作成

#### PDF生成
- [ ] T110 apps/tickets/services.py - generate_ticket_pdf作成
- [ ] T111 static/fonts/ - 日本語フォント追加

#### メール送信
- [ ] T112 tasks/email_tasks.py - send_ticket_email作成
- [ ] T113 templates/emails/ticket_purchase.html作成
- [ ] T114 templates/emails/ticket_purchase.txt作成

#### マイページ
- [ ] T115 apps/members/views.py - MyPageView作成
- [ ] T116 apps/tickets/views.py - TicketDetailView作成
- [ ] T117 apps/tickets/views.py - DownloadTicketPDFView作成
- [ ] T118 templates/members/mypage.html作成
- [ ] T119 templates/tickets/ticket_detail.html作成

#### Signal連携
- [ ] T120 apps/orders/signals.py - post_save Signal作成

#### 単体テスト
- [ ] T121 tests/unit/test_qr_service.py作成
- [ ] T122 tests/unit/test_pdf_service.py作成

**ステータス**: ⏳ 未開始（0/18タスク）

---

### Phase 2.6: User Story 4 - 入場管理（P1）🎯 MVP Core

**目標**: スタッフがQRコードをスキャンして入場記録を管理

#### 入場記録モデル
- [ ] T123 apps/entries/models.py - Entryモデル作成

#### QRコードスキャン
- [ ] T124 apps/entries/views.py - QRScanView作成
- [ ] T125 apps/entries/views.py - VerifyTicketView作成
- [ ] T126 apps/entries/services.py - verify_and_record_entry作成
- [ ] T127 templates/entries/qr_scan.html作成
- [ ] T128 static/js/qr_scanner.js作成

#### 入場状況表示
- [ ] T129 apps/entries/views.py - EntryStatusView作成
- [ ] T130 templates/entries/entry_status.html作成

#### 統合テスト
- [ ] T131 tests/integration/test_entry_flow.py作成

**ステータス**: ⏳ 未開始（0/9タスク）

---

### Phase 2.7: User Story 5 - 会員管理（P1）🎯 MVP

**目標**: 購入者が会員登録、ログイン、情報管理できる

#### 会員情報編集
- [ ] T132 apps/members/forms.py - ProfileForm作成
- [ ] T133 apps/members/views.py - ProfileUpdateView作成
- [ ] T134 templates/members/profile_form.html作成

#### パスワード管理
- [ ] T135 apps/members/forms.py - PasswordChangeFormWithOld作成
- [ ] T136 apps/members/views.py - PasswordChangeView作成
- [ ] T137 apps/members/views.py - PasswordResetRequestView作成
- [ ] T138 apps/members/views.py - PasswordResetConfirmView作成
- [ ] T139 templates/members/password_change.html作成
- [ ] T140 templates/members/password_reset.html作成

#### Brute Force攻撃対策
- [ ] T141 django-axesの設定
- [ ] T142 カスタムログイン試行カウント（オプション）

#### 購入履歴
- [ ] T143 apps/members/views.py - PurchaseHistoryView作成
- [ ] T144 templates/members/purchase_history.html作成

**ステータス**: ⏳ 未開始（0/13タスク）

---

### Phase 2.8: User Story 6 - 主催者ダッシュボード（P2）

**目標**: 主催者が売上サマリー、販売推移を確認できる

#### ダッシュボード
- [ ] T145 apps/organizers/views.py - DashboardView作成
- [ ] T146 apps/organizers/services.py - calculate_sales_summary作成
- [ ] T147 apps/organizers/services.py - get_sales_trend作成
- [ ] T148 templates/organizers/dashboard.html作成
- [ ] T149 static/js/dashboard.js作成（Chart.js）

#### 売上レポート
- [ ] T150 apps/organizers/views.py - SalesReportView作成
- [ ] T151 apps/organizers/views.py - SalesReportCSVView作成
- [ ] T152 templates/organizers/sales_report.html作成

**ステータス**: ⏳ 未開始（0/8タスク）

---

### Phase 2.9: User Story 7 - 自由席チケット購入（P2）

**目標**: 購入者が自由席チケットを購入できる

- [ ] T153 apps/events/views.py - EventDetailView拡張
- [ ] T154 apps/orders/views.py - AddToCartView拡張
- [ ] T155 templates/events/event_detail.html - 自由席UI追加

**ステータス**: ⏳ 未開始（0/3タスク）

---

### Phase 2.10: User Story 8 - キャンセル・返金（P3）

**目標**: 購入者がチケットをキャンセルできる

#### キャンセルモデル
- [ ] T156 apps/orders/models.py - Cancellationモデル作成

#### キャンセル申請
- [ ] T157 apps/orders/views.py - CancellationRequestView作成
- [ ] T158 templates/orders/cancellation_request.html作成

#### キャンセル承認
- [ ] T159 apps/organizers/views.py - CancellationApprovalView作成
- [ ] T160 apps/orders/services.py - process_cancellation作成
- [ ] T161 templates/organizers/cancellation_list.html作成

#### メール通知
- [ ] T162 tasks/email_tasks.py - send_cancellation_email作成

**ステータス**: ⏳ 未開始（0/7タスク）

---

### Phase 2.11: Polish & Cross-Cutting Concerns

**目標**: コード品質向上、ドキュメント整備、テスト

#### ドキュメント
- [ ] T163 README.md更新
- [ ] T164 docs/USER_MANUAL.md作成
- [ ] T165 docs/OPERATION_MANUAL.md作成

#### コード品質
- [ ] T166 コードリファクタリング（DRY原則）
- [ ] T167 N+1問題の確認
- [ ] T168 未使用コードの削除

#### パフォーマンス最適化
- [ ] T169 select_related / prefetch_related最適化
- [ ] T170 静的ファイルの圧縮
- [ ] T171 画像最適化

#### セキュリティ監査
- [ ] T172 Django Security Checklist実行
- [ ] T173 HTTPS設定確認
- [ ] T174 環境変数の確認

#### 統合テスト
- [ ] T175 主要フロー統合テスト実行
- [ ] T176 カバレッジ確認

#### quickstart.md検証
- [ ] T177 quickstart.md手順実行確認
- [ ] T178 トラブルシューティング更新

**ステータス**: ⏳ 未開始（0/16タスク）

---

## 📈 進捗サマリー

### タスク完了状況

| フェーズ | 完了タスク | 総タスク数 | 完了率 | ステータス |
|---------|----------|----------|--------|----------|
| Phase 2.1: Setup | 14 | 14 | 100% | ✅ 完了 |
| Phase 2.2: Foundational | 36 | 36 | 100% | ✅ 完了 |
| Phase 2.3: US1 (P1) | 0 | 30 | 0% | ⏳ 未開始 |
| Phase 2.4: US2 (P1) | 0 | 24 | 0% | ⏳ 未開始 |
| Phase 2.5: US3 (P1) | 0 | 18 | 0% | ⏳ 未開始 |
| Phase 2.6: US4 (P1) | 0 | 9 | 0% | ⏳ 未開始 |
| Phase 2.7: US5 (P1) | 0 | 13 | 0% | ⏳ 未開始 |
| Phase 2.8: US6 (P2) | 0 | 8 | 0% | ⏳ 未開始 |
| Phase 2.9: US7 (P2) | 0 | 3 | 0% | ⏳ 未開始 |
| Phase 2.10: US8 (P3) | 0 | 7 | 0% | ⏳ 未開始 |
| Phase 2.11: Polish | 0 | 16 | 0% | ⏳ 未開始 |

**合計**: 50/178タスク完了（28.1%）

---

## 🎯 MVP Core機能（必須）

### 優先度P1タスク
- [ ] Phase 2.3: User Story 1 - マスタ管理（30タスク）
- [ ] Phase 2.4: User Story 2 - チケット購入（24タスク）
- [ ] Phase 2.5: User Story 3 - 電子チケット発行（18タスク）
- [ ] Phase 2.6: User Story 4 - 入場管理（9タスク）
- [ ] Phase 2.7: User Story 5 - 会員管理（13タスク）

**MVP Core合計**: 94タスク

---

## 🔄 次のステップ

### 推奨実装順序

1. **Phase 2.3: User Story 1** - マスタ管理（1週間）
   - 会場、座席、イベント、チケット種別の登録機能
   
2. **Phase 2.4: User Story 2** - チケット購入（2週間）
   - イベント検索、座席選択、カート、購入確定
   
3. **Phase 2.5: User Story 3** - 電子チケット発行（1週間）
   - QRコード生成、PDF生成、メール送信
   
4. **Phase 2.6: User Story 4** - 入場管理（1週間）
   - QRコードスキャン、入場記録、重複チェック
   
5. **Phase 2.7: User Story 5** - 会員管理（1週間）
   - マイページ、購入履歴、パスワード管理

### 開始コマンド

```bash
# Phase 2.3を開始
# 次のタスクから実装: T051 VenueForm作成
```

---

## ✅ Constitution準拠チェック

### データモデル中心アプローチ
- [x] 主要エンティティ定義完了
- [x] ER図作成完了
- [x] データ整合性要件明確

### UI/UX実装前検証
- [x] 画面モック7画面作成完了
- [x] レスポンシブデザイン考慮
- [x] エラーハンドリング設計

### 品質・保守性・安全性
- [x] Django標準セキュリティ機能活用
- [x] トランザクション制御設計
- [ ] テスト実装（Phase 2進行中）

---

## 🔧 技術スタック確認

### バックエンド
- [x] Django 5.2+
- [x] Python 3.11+
- [x] PostgreSQL 15+ (コンテナ名: db)
- [x] Django ORM
- [x] Celery + Redis

### フロントエンド
- [x] Django Templates
- [x] Bootstrap 5
- [x] Alpine.js
- [ ] QRコードスキャン（html5-qrcode）

### 開発ツール
- [x] Git + GitHub
- [x] pytest + pytest-django
- [ ] Factory Boy（テストデータ）
- [ ] Django Debug Toolbar

---

## 📝 メモ

### 実装済み機能
- ✅ PostgreSQL接続（schema: onlticket2）
- ✅ 基本モデル（User, Organizer, Venue, Event, Seat, TicketType）
- ✅ 認証機能（会員登録、ログイン、ログアウト）
- ✅ Django Admin設定
- ✅ Celery + Redis設定

### 次の実装ポイント
- 会場管理画面の実装（T051-T058）
- 座席表作成機能（一括登録）
- イベント登録画面（主催者向け）
- チケット種別設定

### 技術的注意事項
- 座席の二重販売防止（select_for_update()）
- カート仮予約タイムアウト（10分）
- N+1問題の回避（select_related, prefetch_related）
- QRコード署名検証（HMAC-SHA256）

---

**最終更新**: 2026-01-11  
**次回更新予定**: Phase 2.3完了時
