# 自己紹介システム Djangoリメイク Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 旧・静的自己紹介ページ（GitHub Pages + JSON + GitHub Actions）を、Django（MVT、REST APIなし）による動的システムに置き換える。訪問者はプロフィール（活動実績・資格・スキル）を閲覧でき、管理者はログインしてそれらをCRUD編集できる。

**Architecture:** 単一Djangoアプリ`portfolio`に、Model（`Activity`／`Certification`／`Skill`／`Tag`、管理者はDjango標準`User`を流用）・関数ベースビュー（用途ごとに`portfolio/views/`配下のモジュールに分割）・Form・テンプレートをまとめる。認証はDjango標準の`django.contrib.auth`（`authenticate()`/`login()`/`logout()`）を使い、Django管理サイト（`/admin`）は使わず、すべて自前のログイン画面・編集画面を実装する。

**Tech Stack:** Python 3.11+ / Django 5.1系 / SQLite（開発用DB） / Django標準テストランナー（`python manage.py test`）。Django REST Frameworkは使用しない。

**Spec:** [design/00_概要.md](../../../design/00_概要.md) 〜 [design/05_クラス図.md](../../../design/05_クラス図.md)

## Global Constraints

- REST APIは作らない。Django標準のview／template／formのみで実装する（`design/00_概要.md`）。
- 管理者はプロフィール所有者1名のみ。カスタムの管理者モデルは作らず、Django標準の`User`モデルを認証に利用する（`design/01_ドメインモデル.md`）。
- タグ専用の管理画面は作らない。活動実績の登録・編集フォーム内でカンマ区切り入力から取得または新規作成する（`design/00_概要.md`）。
- プロフィールヘッダー（氏名・学校情報・SNSリンク・アバター画像）は編集対象外。テンプレートに固定値として書く（`design/00_概要.md`）。
- ビューはDjangoの汎用クラスビュー（ListView等）ではなく、ユースケース1つにつき関数ベースビュー1つを対応させる（承認済み設計方針、`03_ロバストネス図.md`のコントローラと1対1対応させるため）。
- Django管理サイト（`/admin`）は使用しない。管理者用の画面はすべて自前実装する（承認済み設計方針）。

---

## File Structure

```
manage.py
requirements.txt
.gitignore
config/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    asgi.py
templates/
    base.html                          … 全画面共通のHTML骨格
portfolio/
    __init__.py
    apps.py
    models.py                          … Activity / Certification / Skill / Tag
    forms.py                           … ActivityForm / CertificationForm / SkillForm
    urls.py                            … portfolio名前空間のURL定義
    views/
        __init__.py
        public.py                      … profile_view
        auth.py                        … login_view / logout_view
        dashboard.py                   … dashboard_view
        activity.py                    … activity_create/update/delete_view
        certification.py               … certification_create/update/delete_view
        skill.py                       … skill_create/update/delete_view
    templates/portfolio/
        profile.html
        login.html
        dashboard.html
        activity_form.html
        activity_confirm_delete.html
        certification_form.html
        certification_confirm_delete.html
        skill_form.html
        skill_confirm_delete.html
    migrations/
        __init__.py
    tests/
        __init__.py
        test_models.py
        test_views_public.py
        test_views_auth.py
        test_views_dashboard.py
        test_forms.py
        test_views_activity.py
        test_views_certification.py
        test_views_skill.py
```

各ビューモジュールはロバストネス図の1コントローラ＝1関数に対応し、各テストファイルは対応するビューモジュールと1対1で対応する。

---

## Task 1: プロジェクト雛形の作成

**Files:**
- Create: `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`（`django-admin startproject`で生成）
- Create: `portfolio/__init__.py`, `portfolio/apps.py`, `portfolio/models.py`, `portfolio/migrations/__init__.py`（`python manage.py startapp`で生成、`views.py`と`tests.py`は削除して置き換える）
- Create: `portfolio/views/__init__.py`
- Create: `portfolio/urls.py`
- Create: `portfolio/tests/__init__.py`
- Create: `templates/base.html`
- Create: `requirements.txt`
- Create: `.gitignore`
- Modify: `config/settings.py`
- Modify: `config/urls.py`

**Interfaces:**
- Produces: URL名前空間`portfolio`（`portfolio/urls.py`の`app_name = "portfolio"`、`urlpatterns = []`）。以降のタスクはここにパスを追加する。
- Produces: `templates/base.html`の`{% block title %}`・`{% block content %}`。以降のテンプレートはこれを`{% extends "base.html" %}`する。

- [ ] **Step 1: Djangoプロジェクトを作成する**

リポジトリ直下（`manage.py`を置く場所）で実行する。

```bash
pip install "Django>=5.1,<6.0"
django-admin startproject config .
```

- [ ] **Step 2: portfolioアプリを作成する**

```bash
python manage.py startapp portfolio
```

- [ ] **Step 3: 不要なデフォルトファイルを削除し、views/・tests/をパッケージ化する**

```bash
rm portfolio/views.py
rm portfolio/tests.py
mkdir portfolio/views
mkdir portfolio/tests
```

`portfolio/views/__init__.py`を空ファイルとして作成する。

`portfolio/tests/__init__.py`を空ファイルとして作成する。

- [ ] **Step 4: `portfolio/urls.py`を作成する**

```python
from django.urls import path

app_name = "portfolio"

urlpatterns = []
```

- [ ] **Step 5: `config/urls.py`を書き換える**

```python
from django.urls import include, path

urlpatterns = [
    path("", include("portfolio.urls")),
]
```

- [ ] **Step 6: `config/settings.py`を編集する**

`INSTALLED_APPS`に`"portfolio"`を追加する:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portfolio",
]
```

`TEMPLATES`の`"DIRS"`を編集する:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        ...
    },
]
```

`LANGUAGE_CODE`・`TIME_ZONE`を変更し、ファイル末尾に認証関連の設定を追加する:

```python
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"

LOGIN_URL = "portfolio:login"
LOGIN_REDIRECT_URL = "portfolio:dashboard"
```

- [ ] **Step 7: `templates/base.html`を作成する**

```html
{% load static %}<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{% block title %}松永 悠志 | Portfolio{% endblock %}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
{% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 8: `requirements.txt`を作成する**

```
Django>=5.1,<6.0
```

- [ ] **Step 9: `.gitignore`を作成する**

```
__pycache__/
*.pyc
db.sqlite3
.venv/
venv/
env/
```

- [ ] **Step 10: 動作確認する**

```bash
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 11: Commit**

```bash
git add manage.py config portfolio templates requirements.txt .gitignore
git commit -m "chore: Djangoプロジェクトとportfolioアプリの雛形を作成"
```

---

## Task 2: Tagモデル

**Files:**
- Modify: `portfolio/models.py`
- Create: `portfolio/tests/test_models.py`
- Create: `portfolio/migrations/0001_initial.py`（`makemigrations`で生成）

**Interfaces:**
- Consumes: なし
- Produces: `portfolio.models.Tag`（フィールド：`name: CharField(max_length=50, unique=True)`）。Task 3以降の`Activity.tags`が参照する。

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_models.py`:

```python
from django.test import TestCase

from portfolio.models import Tag


class TagModelTest(TestCase):
    def test_str_returns_name(self):
        tag = Tag.objects.create(name="Winner")
        self.assertEqual(str(tag), "Winner")

    def test_name_must_be_unique(self):
        from django.db.utils import IntegrityError

        Tag.objects.create(name="Winner")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Winner")
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_models -v 2
```

Expected: FAIL（`ImportError: cannot import name 'Tag'`）

- [ ] **Step 3: Tagモデルを実装する**

`portfolio/models.py`:

```python
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
```

- [ ] **Step 4: マイグレーションを作成し適用する**

```bash
python manage.py makemigrations portfolio
python manage.py migrate
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_models -v 2
```

Expected: `OK`（2 tests）

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations portfolio/tests/test_models.py
git commit -m "feat: Tagモデルを追加"
```

---

## Task 3: Activityモデル

**Files:**
- Modify: `portfolio/models.py`
- Modify: `portfolio/tests/test_models.py`
- Create: `portfolio/migrations/0002_activity.py`（`makemigrations`で生成）

**Interfaces:**
- Consumes: `portfolio.models.Tag`（Task 2）
- Produces: `portfolio.models.Activity`（フィールド：`icon: CharField`, `title: CharField`, `tags: ManyToManyField(Tag)`, `created_at: DateTimeField(auto_now_add=True)`、`Meta.ordering = ["created_at"]`）。Task 6・10〜13が参照する。

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_models.py`に追記:

```python
from portfolio.models import Activity, Tag


class ActivityModelTest(TestCase):
    def test_str_returns_title(self):
        activity = Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        self.assertEqual(str(activity), "北九州Techハッカソン2025")

    def test_can_attach_multiple_tags(self):
        activity = Activity.objects.create(icon="rocket", title="Startup Weekend 北九州")
        winner = Tag.objects.create(name="Winner")
        organizer = Tag.objects.create(name="organizer")
        activity.tags.set([winner, organizer])
        self.assertEqual(list(activity.tags.order_by("name")), [winner, organizer])

    def test_ordered_by_created_at(self):
        first = Activity.objects.create(icon="trophy", title="先に登録した実績")
        second = Activity.objects.create(icon="rocket", title="後に登録した実績")
        self.assertEqual(list(Activity.objects.all()), [first, second])
```

(`Tag`のimportは既存の`from portfolio.models import Tag`を`from portfolio.models import Activity, Tag`に書き換える。)

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_models.ActivityModelTest -v 2
```

Expected: FAIL（`ImportError: cannot import name 'Activity'`）

- [ ] **Step 3: Activityモデルを実装する**

`portfolio/models.py`に追記:

```python
class Activity(models.Model):
    icon = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, blank=True, related_name="activities")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title
```

- [ ] **Step 4: マイグレーションを作成し適用する**

```bash
python manage.py makemigrations portfolio
python manage.py migrate
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_models -v 2
```

Expected: `OK`（5 tests）

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations portfolio/tests/test_models.py
git commit -m "feat: Activityモデルを追加"
```

---

## Task 4: Certificationモデル

**Files:**
- Modify: `portfolio/models.py`
- Modify: `portfolio/tests/test_models.py`
- Create: `portfolio/migrations/0003_certification.py`（`makemigrations`で生成）

**Interfaces:**
- Consumes: なし
- Produces: `portfolio.models.Certification`（フィールド：`icon: CharField`, `title: CharField`, `created_at: DateTimeField(auto_now_add=True)`、`Meta.ordering = ["created_at"]`）。Task 6・9・14〜16が参照する。

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_models.py`に追記:

```python
from portfolio.models import Certification


class CertificationModelTest(TestCase):
    def test_str_returns_title(self):
        certification = Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        self.assertEqual(str(certification), "基本情報技術者試験")

    def test_ordered_by_created_at(self):
        first = Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        second = Certification.objects.create(icon="files", title="簿記実務検定2級")
        self.assertEqual(list(Certification.objects.all()), [first, second])
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_models.CertificationModelTest -v 2
```

Expected: FAIL（`ImportError: cannot import name 'Certification'`）

- [ ] **Step 3: Certificationモデルを実装する**

`portfolio/models.py`に追記:

```python
class Certification(models.Model):
    icon = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title
```

- [ ] **Step 4: マイグレーションを作成し適用する**

```bash
python manage.py makemigrations portfolio
python manage.py migrate
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_models -v 2
```

Expected: `OK`（7 tests）

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations portfolio/tests/test_models.py
git commit -m "feat: Certificationモデルを追加"
```

---

## Task 5: Skillモデル

**Files:**
- Modify: `portfolio/models.py`
- Modify: `portfolio/tests/test_models.py`
- Create: `portfolio/migrations/0004_skill.py`（`makemigrations`で生成）

**Interfaces:**
- Consumes: なし
- Produces: `portfolio.models.Skill`（フィールド：`name: CharField(max_length=100, unique=True)`, `created_at: DateTimeField(auto_now_add=True)`、`Meta.ordering = ["created_at"]`）。Task 6・9・17〜19が参照する。

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_models.py`に追記:

```python
from django.db.utils import IntegrityError

from portfolio.models import Skill


class SkillModelTest(TestCase):
    def test_str_returns_name(self):
        skill = Skill.objects.create(name="Python / Django")
        self.assertEqual(str(skill), "Python / Django")

    def test_name_must_be_unique(self):
        Skill.objects.create(name="Python / Django")
        with self.assertRaises(IntegrityError):
            Skill.objects.create(name="Python / Django")

    def test_ordered_by_created_at(self):
        first = Skill.objects.create(name="HTML5 / CSS3")
        second = Skill.objects.create(name="Go")
        self.assertEqual(list(Skill.objects.all()), [first, second])
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_models.SkillModelTest -v 2
```

Expected: FAIL（`ImportError: cannot import name 'Skill'`）

- [ ] **Step 3: Skillモデルを実装する**

`portfolio/models.py`に追記:

```python
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name
```

- [ ] **Step 4: マイグレーションを作成し適用する**

```bash
python manage.py makemigrations portfolio
python manage.py migrate
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_models -v 2
```

Expected: `OK`（10 tests）

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations portfolio/tests/test_models.py
git commit -m "feat: Skillモデルを追加"
```

---

## Task 6: プロフィール画面（訪問者向け閲覧）

**Files:**
- Create: `portfolio/views/public.py`
- Create: `portfolio/templates/portfolio/profile.html`
- Modify: `portfolio/urls.py`
- Create: `portfolio/tests/test_views_public.py`

**Interfaces:**
- Consumes: `Activity`, `Certification`, `Skill`（Task 3〜5）
- Produces: `portfolio.views.public.profile_view(request)`、URL名`portfolio:profile`（パス`""`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_public.py`:

```python
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity, Certification, Skill


class ProfileViewTest(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse("portfolio:profile"))
        self.assertEqual(response.status_code, 200)

    def test_shows_registered_data(self):
        Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        Certification.objects.create(icon="shield-check", title="基本情報技術者試験")
        Skill.objects.create(name="Python / Django")

        response = self.client.get(reverse("portfolio:profile"))

        self.assertContains(response, "北九州Techハッカソン2025")
        self.assertContains(response, "基本情報技術者試験")
        self.assertContains(response, "Python / Django")

    def test_shows_empty_state_when_no_data(self):
        response = self.client.get(reverse("portfolio:profile"))
        self.assertContains(response, "登録された活動実績はまだありません。")
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_public -v 2
```

Expected: FAIL（`NoReverseMatch: 'portfolio' is not a registered namespace` または該当URL未定義エラー）

- [ ] **Step 3: profile_viewを実装する**

`portfolio/views/public.py`:

```python
from django.shortcuts import render

from ..models import Activity, Certification, Skill


def profile_view(request):
    context = {
        "activities": Activity.objects.all(),
        "certifications": Certification.objects.all(),
        "skills": Skill.objects.all(),
    }
    return render(request, "portfolio/profile.html", context)
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/profile.html`:

```html
{% extends "base.html" %}
{% block title %}松永 悠志 | Portfolio{% endblock %}
{% block content %}
<h1>松永 悠志</h1>

<section>
  <h2>活動・実績</h2>
  {% if activities %}
    <ul>
      {% for activity in activities %}
        <li>
          {{ activity.title }}
          {% for tag in activity.tags.all %}<span class="tag">{{ tag.name }}</span>{% endfor %}
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>登録された活動実績はまだありません。</p>
  {% endif %}
</section>

<section>
  <h2>保有資格・検定</h2>
  {% if certifications %}
    <ul>
      {% for certification in certifications %}
        <li>{{ certification.title }}</li>
      {% endfor %}
    </ul>
  {% else %}
    <p>登録された資格情報はまだありません。</p>
  {% endif %}
</section>

<section>
  <h2>スキル</h2>
  {% if skills %}
    <ul>
      {% for skill in skills %}
        <li>{{ skill.name }}</li>
      {% endfor %}
    </ul>
  {% else %}
    <p>登録されたスキルはまだありません。</p>
  {% endif %}
</section>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`を書き換える:

```python
from django.urls import path

from .views import public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
]
```

- [ ] **Step 6: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_public -v 2
```

Expected: `OK`（3 tests）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/public.py portfolio/templates/portfolio/profile.html portfolio/urls.py portfolio/tests/test_views_public.py
git commit -m "feat: プロフィール画面（訪問者向け閲覧）を実装"
```

---

## Task 7: 管理者ログイン

**Files:**
- Create: `portfolio/views/auth.py`
- Create: `portfolio/templates/portfolio/login.html`
- Modify: `portfolio/urls.py`
- Create: `portfolio/tests/test_views_auth.py`

**Interfaces:**
- Consumes: `django.contrib.auth.models.User`（Django標準）
- Produces: `portfolio.views.auth.login_view(request)`、URL名`portfolio:login`（パス`"login/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_auth.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_get_shows_login_form(self):
        response = self.client.get(reverse("portfolio:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ユーザー名")

    def test_post_with_correct_credentials_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("portfolio:login"),
            {"username": "admin", "password": "password123"},
        )
        self.assertRedirects(response, reverse("portfolio:dashboard"))

    def test_post_with_wrong_credentials_shows_error(self):
        response = self.client.post(
            reverse("portfolio:login"),
            {"username": "admin", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ユーザー名またはパスワードが正しくありません。")
```

`reverse("portfolio:dashboard")`はTask 9で定義するが、`reverse()`はURL名の存在チェックのみ行うため、Task 9完了までは`test_post_with_correct_credentials_redirects_to_dashboard`は`NoReverseMatch`で失敗する。このテストはTask 9完了時に緑になる想定で、このタスクでは残り2件が通ることを確認する。

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_auth.LoginViewTest.test_get_shows_login_form -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: login_viewを実装する**

`portfolio/views/auth.py`:

```python
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("portfolio:dashboard")
        error = "ユーザー名またはパスワードが正しくありません。"
    return render(request, "portfolio/login.html", {"error": error})
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/login.html`:

```html
{% extends "base.html" %}
{% block title %}管理者ログイン{% endblock %}
{% block content %}
<h1>管理者ログイン</h1>
{% if error %}<p class="error">{{ error }}</p>{% endif %}
<form method="post">
  {% csrf_token %}
  <label>ユーザー名 <input type="text" name="username" required></label>
  <label>パスワード <input type="password" name="password" required></label>
  <button type="submit">ログイン</button>
</form>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`を書き換える:

```python
from django.urls import path

from .views import auth, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
]
```

- [ ] **Step 6: テストが通ることを確認する（ダッシュボード関連を除く）**

```bash
python manage.py test portfolio.tests.test_views_auth.LoginViewTest.test_get_shows_login_form portfolio.tests.test_views_auth.LoginViewTest.test_post_with_wrong_credentials_shows_error -v 2
```

Expected: `OK`（2 tests）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/auth.py portfolio/templates/portfolio/login.html portfolio/urls.py portfolio/tests/test_views_auth.py
git commit -m "feat: 管理者ログイン画面を実装"
```

---

## Task 8: 管理者ログアウト

**Files:**
- Modify: `portfolio/views/auth.py`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/tests/test_views_auth.py`

**Interfaces:**
- Consumes: なし
- Produces: `portfolio.views.auth.logout_view(request)`（`@login_required` `@require_POST`）、URL名`portfolio:logout`（パス`"logout/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_auth.py`に追記:

```python
class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_post_while_logged_in_redirects_to_profile(self):
        self.client.login(username="admin", password="password123")
        response = self.client.post(reverse("portfolio:logout"))
        self.assertRedirects(response, reverse("portfolio:profile"))

    def test_get_is_not_allowed(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:logout"))
        self.assertEqual(response.status_code, 405)

    def test_requires_login(self):
        response = self.client.post(reverse("portfolio:logout"))
        self.assertRedirects(
            response, f"{reverse('portfolio:login')}?next={reverse('portfolio:logout')}"
        )
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_auth.LogoutViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: logout_viewを実装する**

`portfolio/views/auth.py`に追記:

```python
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect("portfolio:profile")
```

（ファイル先頭のimportをまとめる: `from django.contrib.auth import authenticate, login, logout`）

- [ ] **Step 4: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("logout/", auth.logout_view, name="logout"),
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_auth.LogoutViewTest -v 2
```

Expected: `OK`（3 tests）

- [ ] **Step 6: Commit**

```bash
git add portfolio/views/auth.py portfolio/urls.py portfolio/tests/test_views_auth.py
git commit -m "feat: 管理者ログアウトを実装"
```

---

## Task 9: 管理画面（ダッシュボード）

**Files:**
- Create: `portfolio/views/dashboard.py`
- Create: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/urls.py`
- Create: `portfolio/tests/test_views_dashboard.py`

**Interfaces:**
- Consumes: `Activity`, `Certification`, `Skill`（Task 3〜5）
- Produces: `portfolio.views.dashboard.dashboard_view(request)`（`@login_required`）、URL名`portfolio:dashboard`（パス`"dashboard/"`）。テンプレートは`portfolio:activity_create`等、Task 11以降で定義するURL名へのリンクを含む（このタスクでは仮に空リストのみ表示するボタンなしの一覧を作り、Task 11〜19でリンクを追加する）。

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_dashboard.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        response = self.client.get(reverse("portfolio:dashboard"))
        self.assertRedirects(
            response, f"{reverse('portfolio:login')}?next={reverse('portfolio:dashboard')}"
        )

    def test_shows_registered_data_when_logged_in(self):
        Activity.objects.create(icon="trophy", title="北九州Techハッカソン2025")
        self.client.login(username="admin", password="password123")

        response = self.client.get(reverse("portfolio:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "北九州Techハッカソン2025")
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_dashboard -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: dashboard_viewを実装する**

`portfolio/views/dashboard.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Activity, Certification, Skill


@login_required
def dashboard_view(request):
    context = {
        "activities": Activity.objects.all(),
        "certifications": Certification.objects.all(),
        "skills": Skill.objects.all(),
    }
    return render(request, "portfolio/dashboard.html", context)
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/dashboard.html`（活動実績・資格・スキルへの登録／編集／削除リンクは、それぞれのURL名が定義されるTask 11〜19で追記する。このタスクでは一覧表示とログアウトボタンのみ実装する）:

```html
{% extends "base.html" %}
{% block title %}管理画面{% endblock %}
{% block content %}
<h1>管理画面</h1>
<form method="post" action="{% url 'portfolio:logout' %}">
  {% csrf_token %}
  <button type="submit">ログアウト</button>
</form>

<section>
  <h2>活動実績</h2>
  <ul>
    {% for activity in activities %}
      <li>{{ activity.title }}</li>
    {% endfor %}
  </ul>
</section>

<section>
  <h2>資格</h2>
  <ul>
    {% for certification in certifications %}
      <li>{{ certification.title }}</li>
    {% endfor %}
  </ul>
</section>

<section>
  <h2>スキル</h2>
  <ul>
    {% for skill in skills %}
      <li>{{ skill.name }}</li>
    {% endfor %}
  </ul>
</section>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("dashboard/", dashboard.dashboard_view, name="dashboard"),
```

（import行に`dashboard`を追加：`from .views import auth, dashboard, public`）

- [ ] **Step 6: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_dashboard portfolio.tests.test_views_auth -v 2
```

Expected: `OK`（Task 7〜9であとまわしにしていたログインリダイレクトのテストも含めて全て緑になる）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/dashboard.py portfolio/templates/portfolio/dashboard.html portfolio/urls.py portfolio/tests/test_views_dashboard.py
git commit -m "feat: 管理画面（ダッシュボード）を実装"
```

---

## Task 10: ActivityForm（タグのインライン作成）

**Files:**
- Create: `portfolio/forms.py`
- Create: `portfolio/tests/test_forms.py`

**Interfaces:**
- Consumes: `Activity`, `Tag`（Task 2・3）
- Produces: `portfolio.forms.ActivityForm`（`Meta.model = Activity`、`Meta.fields = ["icon", "title"]`、独自フィールド`tags: CharField`（カンマ区切り文字列）、`save(commit=True)`でタグを`Tag.objects.get_or_create()`して`activity.tags.set()`する）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_forms.py`:

```python
from django.test import TestCase

from portfolio.forms import ActivityForm
from portfolio.models import Activity, Tag


class ActivityFormTest(TestCase):
    def test_valid_with_required_fields(self):
        form = ActivityForm(data={"icon": "trophy", "title": "北九州Techハッカソン2025", "tags": ""})
        self.assertTrue(form.is_valid())

    def test_invalid_without_title(self):
        form = ActivityForm(data={"icon": "trophy", "title": "", "tags": ""})
        self.assertFalse(form.is_valid())

    def test_save_creates_tags_from_comma_separated_input(self):
        form = ActivityForm(
            data={"icon": "trophy", "title": "Startup Weekend 北九州", "tags": "Winner, organizer"}
        )
        self.assertTrue(form.is_valid())

        activity = form.save()

        self.assertEqual(
            sorted(activity.tags.values_list("name", flat=True)), ["Winner", "organizer"]
        )

    def test_editing_prefills_existing_tags(self):
        activity = Activity.objects.create(icon="trophy", title="既存の実績")
        activity.tags.set([Tag.objects.create(name="Winner")])

        form = ActivityForm(instance=activity)

        self.assertEqual(form.fields["tags"].initial, "Winner")
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_forms -v 2
```

Expected: FAIL（`ModuleNotFoundError: No module named 'portfolio.forms'`）

- [ ] **Step 3: ActivityFormを実装する**

`portfolio/forms.py`:

```python
from django import forms

from .models import Activity, Tag


class ActivityForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label="タグ（カンマ区切り）",
        help_text="複数のタグはカンマで区切って入力してください（例: Winner, organizer）",
    )

    class Meta:
        model = Activity
        fields = ["icon", "title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )

    def clean_tags(self):
        raw = self.cleaned_data.get("tags", "")
        return [name.strip() for name in raw.split(",") if name.strip()]

    def save(self, commit=True):
        activity = super().save(commit=commit)
        if commit:
            self._apply_tags(activity)
        return activity

    def _apply_tags(self, activity):
        names = self.cleaned_data.get("tags", [])
        tags = [Tag.objects.get_or_create(name=name)[0] for name in names]
        activity.tags.set(tags)
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_forms -v 2
```

Expected: `OK`（4 tests）

- [ ] **Step 5: Commit**

```bash
git add portfolio/forms.py portfolio/tests/test_forms.py
git commit -m "feat: ActivityForm（タグのインライン作成）を実装"
```

---

## Task 11: 活動実績を登録する

**Files:**
- Create: `portfolio/views/activity.py`
- Create: `portfolio/templates/portfolio/activity_form.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Create: `portfolio/tests/test_views_activity.py`

**Interfaces:**
- Consumes: `ActivityForm`（Task 10）
- Produces: `portfolio.views.activity.activity_create_view(request)`（`@login_required`）、URL名`portfolio:activity_create`（パス`"activities/new/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_activity.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Activity


class ActivityCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:activity_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_activity_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_create"),
            {"icon": "trophy", "title": "北九州Techハッカソン2025", "tags": "Winner"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(Activity.objects.first().tags.first().name, "Winner")

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_create"), {"icon": "trophy", "title": "", "tags": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activity.objects.count(), 0)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: activity_create_viewを実装する**

`portfolio/views/activity.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import ActivityForm


@login_required
def activity_create_view(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = ActivityForm()
    return render(request, "portfolio/activity_form.html", {"form": form})
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/activity_form.html`:

```html
{% extends "base.html" %}
{% block title %}活動実績{% if activity %}編集{% else %}登録{% endif %}{% endblock %}
{% block content %}
<h1>活動実績{% if activity %}編集{% else %}登録{% endif %}</h1>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">保存</button>
</form>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`を書き換える（importに`activity`を追加）:

```python
from django.urls import path

from .views import activity, auth, dashboard, public

app_name = "portfolio"

urlpatterns = [
    path("", public.profile_view, name="profile"),
    path("login/", auth.login_view, name="login"),
    path("logout/", auth.logout_view, name="logout"),
    path("dashboard/", dashboard.dashboard_view, name="dashboard"),
    path("activities/new/", activity.activity_create_view, name="activity_create"),
]
```

- [ ] **Step 6: ダッシュボードに登録リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の「活動実績」セクションを書き換える:

```html
<section>
  <h2>活動実績</h2>
  <a href="{% url 'portfolio:activity_create' %}">新規登録</a>
  <ul>
    {% for activity in activities %}
      <li>{{ activity.title }}</li>
    {% endfor %}
  </ul>
</section>
```

- [ ] **Step 7: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity -v 2
```

Expected: `OK`（4 tests）

- [ ] **Step 8: Commit**

```bash
git add portfolio/views/activity.py portfolio/templates/portfolio/activity_form.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_activity.py
git commit -m "feat: 活動実績の登録機能を実装"
```

---

## Task 12: 活動実績を編集する

**Files:**
- Modify: `portfolio/views/activity.py`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_activity.py`

**Interfaces:**
- Consumes: `ActivityForm`（Task 10）
- Produces: `portfolio.views.activity.activity_update_view(request, pk)`（`@login_required`）、URL名`portfolio:activity_update`（パス`"activities/<int:pk>/edit/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_activity.py`に追記:

```python
from portfolio.models import Activity


class ActivityUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.activity = Activity.objects.create(icon="trophy", title="既存の実績")

    def test_requires_login(self):
        url = reverse("portfolio:activity_update", args=[self.activity.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_update", args=[self.activity.pk]))
        self.assertContains(response, "既存の実績")

    def test_post_valid_data_updates_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_update", args=[self.activity.pk]),
            {"icon": "trophy", "title": "更新後の実績", "tags": ""},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.title, "更新後の実績")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_update", args=[9999]))
        self.assertEqual(response.status_code, 404)
```

（`Activity`のimportは既存の`from portfolio.models import Activity`をファイル上部に1回だけ置けばよい。既に`ActivityCreateViewTest`が同ファイルにある場合、重複import文は削除すること。）

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity.ActivityUpdateViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: activity_update_viewを実装する**

`portfolio/views/activity.py`に追記:

```python
from django.shortcuts import get_object_or_404

from ..models import Activity


@login_required
def activity_update_view(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = ActivityForm(instance=activity)
    return render(request, "portfolio/activity_form.html", {"form": form, "activity": activity})
```

（ファイル先頭のimportをまとめる: `from django.shortcuts import get_object_or_404, redirect, render`）

- [ ] **Step 4: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("activities/<int:pk>/edit/", activity.activity_update_view, name="activity_update"),
```

- [ ] **Step 5: ダッシュボードに編集リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の活動実績の`<li>`を書き換える:

```html
      <li>
        {{ activity.title }}
        <a href="{% url 'portfolio:activity_update' activity.pk %}">編集</a>
      </li>
```

- [ ] **Step 6: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity -v 2
```

Expected: `OK`（8 tests）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/activity.py portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_activity.py
git commit -m "feat: 活動実績の編集機能を実装"
```

---

## Task 13: 活動実績を削除する

**Files:**
- Modify: `portfolio/views/activity.py`
- Create: `portfolio/templates/portfolio/activity_confirm_delete.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_activity.py`

**Interfaces:**
- Consumes: `Activity`（Task 3）
- Produces: `portfolio.views.activity.activity_delete_view(request, pk)`（`@login_required`）、URL名`portfolio:activity_delete`（パス`"activities/<int:pk>/delete/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_activity.py`に追記:

```python
class ActivityDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.activity = Activity.objects.create(icon="trophy", title="削除対象の実績")

    def test_requires_login(self):
        url = reverse("portfolio:activity_delete", args=[self.activity.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:activity_delete", args=[self.activity.pk]))
        self.assertContains(response, "削除対象の実績")

    def test_post_confirm_yes_deletes_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_delete", args=[self.activity.pk]), {"confirm": "yes"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 0)

    def test_post_confirm_no_keeps_activity(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:activity_delete", args=[self.activity.pk]), {"confirm": "no"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Activity.objects.count(), 1)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity.ActivityDeleteViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: activity_delete_viewを実装する**

`portfolio/views/activity.py`に追記:

```python
@login_required
def activity_delete_view(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            activity.delete()
        return redirect("portfolio:dashboard")
    return render(request, "portfolio/activity_confirm_delete.html", {"activity": activity})
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/activity_confirm_delete.html`:

```html
{% extends "base.html" %}
{% block title %}活動実績削除確認{% endblock %}
{% block content %}
<h1>活動実績削除確認</h1>
<p>「{{ activity.title }}」を削除します。よろしいですか？</p>
<form method="post">
  {% csrf_token %}
  <button type="submit" name="confirm" value="yes">削除する</button>
  <button type="submit" name="confirm" value="no">キャンセル</button>
</form>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("activities/<int:pk>/delete/", activity.activity_delete_view, name="activity_delete"),
```

- [ ] **Step 6: ダッシュボードに削除リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の活動実績の`<li>`を書き換える:

```html
      <li>
        {{ activity.title }}
        <a href="{% url 'portfolio:activity_update' activity.pk %}">編集</a>
        <a href="{% url 'portfolio:activity_delete' activity.pk %}">削除</a>
      </li>
```

- [ ] **Step 7: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_activity -v 2
```

Expected: `OK`（12 tests）

- [ ] **Step 8: Commit**

```bash
git add portfolio/views/activity.py portfolio/templates/portfolio/activity_confirm_delete.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_activity.py
git commit -m "feat: 活動実績の削除機能を実装"
```

---

## Task 14: 資格情報を登録する

**Files:**
- Modify: `portfolio/forms.py`
- Create: `portfolio/views/certification.py`
- Create: `portfolio/templates/portfolio/certification_form.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Create: `portfolio/tests/test_views_certification.py`

**Interfaces:**
- Consumes: `Certification`（Task 4）
- Produces: `portfolio.forms.CertificationForm`（`Meta.model = Certification`、`Meta.fields = ["icon", "title"]`）、`portfolio.views.certification.certification_create_view(request)`（`@login_required`）、URL名`portfolio:certification_create`（パス`"certifications/new/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_certification.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Certification


class CertificationCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:certification_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:certification_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_certification_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_create"),
            {"icon": "shield-check", "title": "基本情報技術者試験"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 1)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_create"), {"icon": "shield-check", "title": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Certification.objects.count(), 0)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: CertificationFormを実装する**

`portfolio/forms.py`に追記:

```python
from .models import Certification


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ["icon", "title"]
```

（ファイル先頭のimportをまとめる: `from .models import Activity, Certification, Tag`）

- [ ] **Step 4: certification_create_viewを実装する**

`portfolio/views/certification.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import CertificationForm


@login_required
def certification_create_view(request):
    if request.method == "POST":
        form = CertificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = CertificationForm()
    return render(request, "portfolio/certification_form.html", {"form": form})
```

- [ ] **Step 5: テンプレートを作成する**

`portfolio/templates/portfolio/certification_form.html`:

```html
{% extends "base.html" %}
{% block title %}資格{% if certification %}編集{% else %}登録{% endif %}{% endblock %}
{% block content %}
<h1>資格{% if certification %}編集{% else %}登録{% endif %}</h1>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">保存</button>
</form>
{% endblock %}
```

- [ ] **Step 6: URLを登録する**

`portfolio/urls.py`を書き換える（importに`certification`を追加）:

```python
from .views import activity, auth, certification, dashboard, public
```

`urlpatterns`に追記:

```python
    path("certifications/new/", certification.certification_create_view, name="certification_create"),
```

- [ ] **Step 7: ダッシュボードに登録リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の「資格」セクションを書き換える:

```html
<section>
  <h2>資格</h2>
  <a href="{% url 'portfolio:certification_create' %}">新規登録</a>
  <ul>
    {% for certification in certifications %}
      <li>{{ certification.title }}</li>
    {% endfor %}
  </ul>
</section>
```

- [ ] **Step 8: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification -v 2
```

Expected: `OK`（4 tests）

- [ ] **Step 9: Commit**

```bash
git add portfolio/forms.py portfolio/views/certification.py portfolio/templates/portfolio/certification_form.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_certification.py
git commit -m "feat: 資格情報の登録機能を実装"
```

---

## Task 15: 資格情報を編集する

**Files:**
- Modify: `portfolio/views/certification.py`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_certification.py`

**Interfaces:**
- Consumes: `CertificationForm`（Task 14）
- Produces: `portfolio.views.certification.certification_update_view(request, pk)`（`@login_required`）、URL名`portfolio:certification_update`（パス`"certifications/<int:pk>/edit/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_certification.py`に追記:

```python
class CertificationUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.certification = Certification.objects.create(icon="shield-check", title="既存の資格")

    def test_requires_login(self):
        url = reverse("portfolio:certification_update", args=[self.certification.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(
            reverse("portfolio:certification_update", args=[self.certification.pk])
        )
        self.assertContains(response, "既存の資格")

    def test_post_valid_data_updates_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_update", args=[self.certification.pk]),
            {"icon": "shield-check", "title": "更新後の資格"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.certification.refresh_from_db()
        self.assertEqual(self.certification.title, "更新後の資格")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:certification_update", args=[9999]))
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification.CertificationUpdateViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: certification_update_viewを実装する**

`portfolio/views/certification.py`に追記:

```python
from django.shortcuts import get_object_or_404

from ..models import Certification


@login_required
def certification_update_view(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = CertificationForm(instance=certification)
    return render(
        request, "portfolio/certification_form.html", {"form": form, "certification": certification}
    )
```

（ファイル先頭のimportをまとめる: `from django.shortcuts import get_object_or_404, redirect, render`）

- [ ] **Step 4: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("certifications/<int:pk>/edit/", certification.certification_update_view, name="certification_update"),
```

- [ ] **Step 5: ダッシュボードに編集リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の資格の`<li>`を書き換える:

```html
      <li>
        {{ certification.title }}
        <a href="{% url 'portfolio:certification_update' certification.pk %}">編集</a>
      </li>
```

- [ ] **Step 6: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification -v 2
```

Expected: `OK`（8 tests）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/certification.py portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_certification.py
git commit -m "feat: 資格情報の編集機能を実装"
```

---

## Task 16: 資格情報を削除する

**Files:**
- Modify: `portfolio/views/certification.py`
- Create: `portfolio/templates/portfolio/certification_confirm_delete.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_certification.py`

**Interfaces:**
- Consumes: `Certification`（Task 4）
- Produces: `portfolio.views.certification.certification_delete_view(request, pk)`（`@login_required`）、URL名`portfolio:certification_delete`（パス`"certifications/<int:pk>/delete/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_certification.py`に追記:

```python
class CertificationDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.certification = Certification.objects.create(icon="shield-check", title="削除対象の資格")

    def test_requires_login(self):
        url = reverse("portfolio:certification_delete", args=[self.certification.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(
            reverse("portfolio:certification_delete", args=[self.certification.pk])
        )
        self.assertContains(response, "削除対象の資格")

    def test_post_confirm_yes_deletes_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_delete", args=[self.certification.pk]),
            {"confirm": "yes"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 0)

    def test_post_confirm_no_keeps_certification(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:certification_delete", args=[self.certification.pk]),
            {"confirm": "no"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Certification.objects.count(), 1)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification.CertificationDeleteViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: certification_delete_viewを実装する**

`portfolio/views/certification.py`に追記:

```python
@login_required
def certification_delete_view(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            certification.delete()
        return redirect("portfolio:dashboard")
    return render(
        request, "portfolio/certification_confirm_delete.html", {"certification": certification}
    )
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/certification_confirm_delete.html`:

```html
{% extends "base.html" %}
{% block title %}資格削除確認{% endblock %}
{% block content %}
<h1>資格削除確認</h1>
<p>「{{ certification.title }}」を削除します。よろしいですか？</p>
<form method="post">
  {% csrf_token %}
  <button type="submit" name="confirm" value="yes">削除する</button>
  <button type="submit" name="confirm" value="no">キャンセル</button>
</form>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("certifications/<int:pk>/delete/", certification.certification_delete_view, name="certification_delete"),
```

- [ ] **Step 6: ダッシュボードに削除リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の資格の`<li>`を書き換える:

```html
      <li>
        {{ certification.title }}
        <a href="{% url 'portfolio:certification_update' certification.pk %}">編集</a>
        <a href="{% url 'portfolio:certification_delete' certification.pk %}">削除</a>
      </li>
```

- [ ] **Step 7: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_certification -v 2
```

Expected: `OK`（12 tests）

- [ ] **Step 8: Commit**

```bash
git add portfolio/views/certification.py portfolio/templates/portfolio/certification_confirm_delete.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_certification.py
git commit -m "feat: 資格情報の削除機能を実装"
```

---

## Task 17: スキルを登録する

**Files:**
- Modify: `portfolio/forms.py`
- Create: `portfolio/views/skill.py`
- Create: `portfolio/templates/portfolio/skill_form.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Create: `portfolio/tests/test_views_skill.py`

**Interfaces:**
- Consumes: `Skill`（Task 5）
- Produces: `portfolio.forms.SkillForm`（`Meta.model = Skill`、`Meta.fields = ["name"]`）、`portfolio.views.skill.skill_create_view(request)`（`@login_required`）、URL名`portfolio:skill_create`（パス`"skills/new/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_skill.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portfolio.models import Skill


class SkillCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")

    def test_requires_login(self):
        url = reverse("portfolio:skill_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_empty_form(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_data_creates_skill_and_redirects(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_create"), {"name": "Python / Django"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 1)

    def test_post_invalid_data_shows_errors(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(reverse("portfolio:skill_create"), {"name": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Skill.objects.count(), 0)

    def test_post_duplicate_name_shows_errors(self):
        Skill.objects.create(name="Python / Django")
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_create"), {"name": "Python / Django"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Skill.objects.count(), 1)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_skill -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: SkillFormを実装する**

`portfolio/forms.py`に追記:

```python
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name"]
```

（ファイル先頭のimportをまとめる: `from .models import Activity, Certification, Skill, Tag`）

- [ ] **Step 4: skill_create_viewを実装する**

`portfolio/views/skill.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import SkillForm


@login_required
def skill_create_view(request):
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = SkillForm()
    return render(request, "portfolio/skill_form.html", {"form": form})
```

- [ ] **Step 5: テンプレートを作成する**

`portfolio/templates/portfolio/skill_form.html`:

```html
{% extends "base.html" %}
{% block title %}スキル{% if skill %}編集{% else %}登録{% endif %}{% endblock %}
{% block content %}
<h1>スキル{% if skill %}編集{% else %}登録{% endif %}</h1>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">保存</button>
</form>
{% endblock %}
```

- [ ] **Step 6: URLを登録する**

`portfolio/urls.py`を書き換える（importに`skill`を追加）:

```python
from .views import activity, auth, certification, dashboard, public, skill
```

`urlpatterns`に追記:

```python
    path("skills/new/", skill.skill_create_view, name="skill_create"),
```

- [ ] **Step 7: ダッシュボードに登録リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`の「スキル」セクションを書き換える:

```html
<section>
  <h2>スキル</h2>
  <a href="{% url 'portfolio:skill_create' %}">新規登録</a>
  <ul>
    {% for skill in skills %}
      <li>{{ skill.name }}</li>
    {% endfor %}
  </ul>
</section>
```

- [ ] **Step 8: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_skill -v 2
```

Expected: `OK`（5 tests）

- [ ] **Step 9: Commit**

```bash
git add portfolio/forms.py portfolio/views/skill.py portfolio/templates/portfolio/skill_form.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_skill.py
git commit -m "feat: スキルの登録機能を実装"
```

---

## Task 18: スキルを編集する

**Files:**
- Modify: `portfolio/views/skill.py`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_skill.py`

**Interfaces:**
- Consumes: `SkillForm`（Task 17）
- Produces: `portfolio.views.skill.skill_update_view(request, pk)`（`@login_required`）、URL名`portfolio:skill_update`（パス`"skills/<int:pk>/edit/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_skill.py`に追記:

```python
class SkillUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.skill = Skill.objects.create(name="既存のスキル")

    def test_requires_login(self):
        url = reverse("portfolio:skill_update", args=[self.skill.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_prefills_existing_data(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_update", args=[self.skill.pk]))
        self.assertContains(response, "既存のスキル")

    def test_post_valid_data_updates_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_update", args=[self.skill.pk]),
            {"name": "更新後のスキル"},
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "更新後のスキル")

    def test_get_with_unknown_pk_returns_404(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_update", args=[9999]))
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_skill.SkillUpdateViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: skill_update_viewを実装する**

`portfolio/views/skill.py`に追記:

```python
from django.shortcuts import get_object_or_404

from ..models import Skill


@login_required
def skill_update_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect("portfolio:dashboard")
    else:
        form = SkillForm(instance=skill)
    return render(request, "portfolio/skill_form.html", {"form": form, "skill": skill})
```

（ファイル先頭のimportをまとめる: `from django.shortcuts import get_object_or_404, redirect, render`）

- [ ] **Step 4: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("skills/<int:pk>/edit/", skill.skill_update_view, name="skill_update"),
```

- [ ] **Step 5: ダッシュボードに編集リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`のスキルの`<li>`を書き換える:

```html
      <li>
        {{ skill.name }}
        <a href="{% url 'portfolio:skill_update' skill.pk %}">編集</a>
      </li>
```

- [ ] **Step 6: テストが通ることを確認する**

```bash
python manage.py test portfolio.tests.test_views_skill -v 2
```

Expected: `OK`（9 tests）

- [ ] **Step 7: Commit**

```bash
git add portfolio/views/skill.py portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_skill.py
git commit -m "feat: スキルの編集機能を実装"
```

---

## Task 19: スキルを削除する

**Files:**
- Modify: `portfolio/views/skill.py`
- Create: `portfolio/templates/portfolio/skill_confirm_delete.html`
- Modify: `portfolio/urls.py`
- Modify: `portfolio/templates/portfolio/dashboard.html`
- Modify: `portfolio/tests/test_views_skill.py`

**Interfaces:**
- Consumes: `Skill`（Task 5）
- Produces: `portfolio.views.skill.skill_delete_view(request, pk)`（`@login_required`）、URL名`portfolio:skill_delete`（パス`"skills/<int:pk>/delete/"`）

- [ ] **Step 1: 失敗するテストを書く**

`portfolio/tests/test_views_skill.py`に追記:

```python
class SkillDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="password123")
        self.skill = Skill.objects.create(name="削除対象のスキル")

    def test_requires_login(self):
        url = reverse("portfolio:skill_delete", args=[self.skill.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('portfolio:login')}?next={url}")

    def test_get_shows_confirmation(self):
        self.client.login(username="admin", password="password123")
        response = self.client.get(reverse("portfolio:skill_delete", args=[self.skill.pk]))
        self.assertContains(response, "削除対象のスキル")

    def test_post_confirm_yes_deletes_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "yes"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 0)

    def test_post_confirm_no_keeps_skill(self):
        self.client.login(username="admin", password="password123")

        response = self.client.post(
            reverse("portfolio:skill_delete", args=[self.skill.pk]), {"confirm": "no"}
        )

        self.assertRedirects(response, reverse("portfolio:dashboard"))
        self.assertEqual(Skill.objects.count(), 1)
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
python manage.py test portfolio.tests.test_views_skill.SkillDeleteViewTest -v 2
```

Expected: FAIL（該当URL未定義エラー）

- [ ] **Step 3: skill_delete_viewを実装する**

`portfolio/views/skill.py`に追記:

```python
@login_required
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            skill.delete()
        return redirect("portfolio:dashboard")
    return render(request, "portfolio/skill_confirm_delete.html", {"skill": skill})
```

- [ ] **Step 4: テンプレートを作成する**

`portfolio/templates/portfolio/skill_confirm_delete.html`:

```html
{% extends "base.html" %}
{% block title %}スキル削除確認{% endblock %}
{% block content %}
<h1>スキル削除確認</h1>
<p>「{{ skill.name }}」を削除します。よろしいですか？</p>
<form method="post">
  {% csrf_token %}
  <button type="submit" name="confirm" value="yes">削除する</button>
  <button type="submit" name="confirm" value="no">キャンセル</button>
</form>
{% endblock %}
```

- [ ] **Step 5: URLを登録する**

`portfolio/urls.py`の`urlpatterns`に追記:

```python
    path("skills/<int:pk>/delete/", skill.skill_delete_view, name="skill_delete"),
```

- [ ] **Step 6: ダッシュボードに削除リンクを追加する**

`portfolio/templates/portfolio/dashboard.html`のスキルの`<li>`を書き換える:

```html
      <li>
        {{ skill.name }}
        <a href="{% url 'portfolio:skill_update' skill.pk %}">編集</a>
        <a href="{% url 'portfolio:skill_delete' skill.pk %}">削除</a>
      </li>
```

- [ ] **Step 7: 全テストスイートを実行し、すべて通ることを確認する**

```bash
python manage.py test -v 2
```

Expected: `OK`（全テストが緑。おおむね60テスト前後になる想定）

- [ ] **Step 8: Commit**

```bash
git add portfolio/views/skill.py portfolio/templates/portfolio/skill_confirm_delete.html portfolio/urls.py portfolio/templates/portfolio/dashboard.html portfolio/tests/test_views_skill.py
git commit -m "feat: スキルの削除機能を実装"
```

---

## 運用メモ（本プランのスコープ外）

- 管理者アカウントは`python manage.py createsuperuser`で1つだけ作成する。本プランには含めない（システムのユースケースではなく、運用・デプロイ時の初期セットアップ作業のため）。
- プロフィールヘッダー（氏名・学校情報・SNSリンク・アバター画像）や、旧ページのCSS・ダークモード切替JSの移植は、`design/00_概要.md`で編集対象外・対象外と定義したとおり本プランに含めない。見た目を旧ページに近づけたい場合は別途スコープを切って計画する。
