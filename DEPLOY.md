# デプロイ手順 (Vercel + Neon)

本番は Vercel（Git連携で push 時に自動デプロイ）、DB は Neon Postgres を使う。Vercel は WSGI の `application`（`config/wsgi.py`）を自動検出するため、`vercel.json` や `api/` は不要。SQLite は Vercel 上で書き込めないので本番では使わない。

## 1. Neon Postgres を用意する

1. Vercel ダッシュボードの Marketplace から Neon を追加し、プロジェクトに接続する。
2. 発行された接続文字列のうち、プール接続（ホスト名に `-pooler` を含むもの）の `DATABASE_URL` を控える。末尾は `?sslmode=require` であること。

## 2. Vercel の環境変数

| 変数 | 値 |
| --- | --- |
| `SECRET_KEY` | 50文字以上のランダム文字列 |
| `DATABASE_URL` | 手順1のプール接続文字列（Marketplace 連携なら自動設定される）。本番では必須 |
| `ALLOWED_HOSTS` | 独自ドメインをカンマ区切りで指定（例: `example.com`）。`*.vercel.app` は `VERCEL` 環境変数により自動で許可される |
| `CSRF_TRUSTED_ORIGINS` | スキーム付きのオリジンをカンマ区切りで指定（例: `https://example.com`） |

`DJANGO_DEBUG` は未設定（または `0`）のままにする。有効にすると DEBUG 動作になる。`SECRET_KEY` と `DATABASE_URL` は、どちらか一方でも未設定だと起動時に `ImproperlyConfigured` で失敗する（意図した挙動。`DATABASE_URL` を忘れて読み取り専用の SQLite に落ちるのを防ぐ）。

`SECRET_KEY` の生成例:

```
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 3. 初回セットアップ（開発マシンから実行）

マイグレーションは関数の起動時には実行されない。デプロイ前後に手元から本番DBへ適用する。

```
pip install -r requirements.txt
DATABASE_URL="postgres://...?sslmode=require" python manage.py migrate
DATABASE_URL="postgres://...?sslmode=require" python manage.py createsuperuser
```

管理者アカウントは1つだけ（プロフィールの持ち主）作成する。モデルを変更したときも、デプロイのたびに同じ `migrate` を実行すること。

## 4. デプロイ

Git リポジトリを Vercel プロジェクトに接続し、`master` へ push すれば自動でデプロイされる。Python のバージョンは `.python-version`（3.13）で指定している。

## 補足: ローカルの Docker

`docker-compose.yml` はローカル開発と CI 用（本番では使わない）。`env_file` の `required: false` を使うため Docker Compose 2.24 以上が必要。

## 静的ファイル（CSS/JS/画像）の配信

`portfolio/static/portfolio/` 配下の CSS・JS・画像は `whitenoise`（`config/settings.py` の `MIDDLEWARE`）が配信する。`WHITENOISE_USE_FINDERS = True` にしているため、`collectstatic` を実行するビルドステップは不要（Vercel はゼロコンフィグで `vercel.json`/`api/` もビルドコマンドも挟まないため、`migrate` を手元から手動実行しているのと同じ理由で `collectstatic` に頼らない構成にしている）。`gunicorn`（Docker）でも `runserver`（開発）でも同じ経路で配信される。

デプロイ後は Preview/本番 URL の `/static/portfolio/css/style.css` が `200` を返すことを確認すること。
