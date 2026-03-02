# Release Note Generator

デプロイ情報を保存し、AIで社内外向けのリリースノート草案とロールバック観点を生成するバックエンドです。

## 設計思想

変更入力と配布文面を別レイヤーで管理することで、承認前レビューと再生成がしやすくなります。開発生産性と運用の両方を語れる題材です。

### なぜこの設計にしたのか

- ルーティング、ユースケース、永続化、AI呼び出しを分離して、責務を明確にするため。
- `mock` と `openai` を切り替えられるようにして、ローカル開発と本番連携を両立するため。
- 解析結果を元データと別テーブルで持ち、再生成と監査をしやすくするため。
- 認証、例外整形、入力制約を最初から入れ、実務に近い非機能要件まで示すため。

## 技術スタック

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite（`DATABASE_URL` を差し替えれば Postgres に移行可能）
- OpenAI互換API / mock provider
- Pytest / Ruff / Black / Mypy
- Docker / GitHub Actions

## ディレクトリ構成

```text
.
├── .env.example
├── .github/workflows/ci.yml
├── app
│   ├── api/routes.py
│   ├── core/config.py
│   ├── core/errors.py
│   ├── core/security.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── repositories.py
│   ├── schemas.py
│   └── services
│       ├── ai.py
│       └── domain.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
└── tests
    ├── conftest.py
    ├── test_health.py
    └── test_workflow.py
```

## API概要

- `POST /deployments`: デプロイ記録を登録
- `GET /deployments/{id}`: デプロイ記録を取得
- `POST /deployments/{id}/draft-note`: AI解析を実行
- `GET /deployments/{id}/note`: 解析結果を取得

## 最小実装コード例

```python
@router.post(
    "/deployments/{record_id}/draft-note",
    response_model=schemas.ReleaseNoteDraftResponse,
    dependencies=[Depends(verify_internal_api_key)],
)
def analyze_record(
    record_id: str,
    service: DeploymentService = Depends(get_service),
) -> schemas.ReleaseNoteDraftResponse:
    return service.draft_release_note(record_id)
```

## ローカル起動

```bash
cp .env.example .env
make install
make run
```

Dockerでも起動できます。

```bash
cp .env.example .env
docker compose up --build
```

デフォルトでは `AI_PROVIDER=mock` のため、外部AIキーなしで動作確認できます。

## テスト

```bash
make test
make lint
make typecheck
```

## セキュリティ配慮

- 変更内容は社内情報なので、内部APIキーでのみ操作する前提にしている。
- AIへの入力は構造化済みの変更要約に限定し、不要なログ全文は送らない。
- Issue参照は文字列配列として保存し、監査や外部連携をしやすくする。

## エラーハンドリング設計

- AI生成に失敗しても元のデプロイ記録は保持し、再生成だけやり直せるようにしている。
- 例外応答に `request_id` を含め、CIやログと照合しやすくする。

## CI

GitHub Actions で以下を実行します。

- `ruff check .`
- `black --check .`
- `mypy app tests`
- `pytest`

## サンプルリクエスト

```bash
curl -X POST http://localhost:8000/deployments \
  -H "Content-Type: application/json" \
  -H "X-Internal-API-Key: dev-internal-key" \
  -d '{
  "service_name": "checkout-api",
  "environment": "production",
  "change_summary": "Improved payment retry behavior and added dashboard alerts for failed authorizations.",
  "issue_refs": [
    "PAY-123",
    "OPS-88"
  ]
}'
```

## READMEテンプレとして使う場合の章立て

- 背景 / 課題設定
- コンセプト
- 設計思想
- 技術スタック
- ディレクトリ構成
- ローカル起動手順
- API仕様
- テスト / CI
- セキュリティ
- 今後の拡張
