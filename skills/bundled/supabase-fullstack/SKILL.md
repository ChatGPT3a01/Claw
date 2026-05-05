---
name: supabase-fullstack
description: Supabase 全端應用開發完整指南。涵蓋 Supabase CLI 操作、資料庫設計、Auth 認證、RLS 權限規則、CRUD 介面、Edge Functions、Storage、Netlify 部署串接。使用時機：(1) 建立 Supabase 後端專案，(2) 設計資料表與 migration，(3) 實作登入/註冊/權限，(4) 建立管理者後台 CRUD，(5) 串接前端到 Supabase，(6) 設定 RLS 安全規則，(7) 部署到 Netlify + Supabase。關鍵詞：Supabase、後端、資料庫、Auth、RLS、CRUD、PostgreSQL、migration、Edge Functions、Storage。
---

# Supabase 全端應用開發指南

從零到部署的完整 Supabase 開發流程。

---

## 一、環境準備

### 1. Supabase CLI 安裝與驗證

```bash
# 安裝（npm 方式）
npm install -g supabase

# 驗證
supabase --version

# 登入（會開瀏覽器取得 access token）
supabase login
```

### 2. 專案初始化

```bash
# 在專案目錄初始化 Supabase
supabase init

# 產生的結構：
# supabase/
# ├── config.toml          # 本機設定
# ├── migrations/           # 資料庫 migration 檔
# ├── functions/            # Edge Functions
# └── seed.sql              # 種子資料
```

### 3. 連結遠端專案

```bash
# 連結已存在的 Supabase 專案
supabase link --project-ref <PROJECT_ID>

# PROJECT_ID 在 Supabase Dashboard > Settings > General 可找到
```

### 4. 前端 SDK 安裝

```bash
# JavaScript / TypeScript
npm install @supabase/supabase-js

# 初始化 client
```

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)
```

---

## 二、資料庫設計與 Migration

### 1. 建立 Migration

```bash
# 建立新 migration 檔
supabase migration new create_users_table

# 會產生：supabase/migrations/20260316000000_create_users_table.sql
```

### 2. 常用資料表模板

```sql
-- ========== 使用者擴充資料表 ==========
CREATE TABLE public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  display_name TEXT,
  role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'editor')),
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 自動建立 profile（新用戶註冊時觸發）
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, display_name)
  VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ========== 通用內容資料表 ==========
CREATE TABLE public.posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  slug TEXT UNIQUE,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  author_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========== updated_at 自動更新 ==========
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 套用到每個需要的表
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_posts_updated_at
  BEFORE UPDATE ON public.posts
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
```

### 3. Migration 操作

```bash
# 套用 migration 到遠端
supabase db push

# 查看 migration 狀態
supabase migration list

# 從遠端拉回目前結構
supabase db pull

# 重置本機資料庫
supabase db reset

# 產生 TypeScript 型別
supabase gen types typescript --linked > src/types/database.ts
```

---

## 三、Auth 認證系統

### 1. Email/Password 認證

```javascript
// === 註冊 ===
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'securepassword',
  options: {
    data: {
      display_name: '使用者名稱',
    }
  }
})

// === 登入 ===
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securepassword',
})

// === 登出 ===
await supabase.auth.signOut()

// === 取得目前使用者 ===
const { data: { user } } = await supabase.auth.getUser()

// === 監聽 auth 狀態變化 ===
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    console.log('已登入', session.user)
  } else if (event === 'SIGNED_OUT') {
    console.log('已登出')
  }
})
```

### 2. OAuth 社群登入

```javascript
// Google 登入
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`
  }
})

// GitHub 登入
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
})
```

### 3. 管理者密碼登入（自訂邏輯）

```javascript
// 登入後檢查角色
async function loginAndCheckRole(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email, password
  })
  if (error) return { success: false, error: error.message }

  // 從 profiles 查角色
  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', data.user.id)
    .single()

  return {
    success: true,
    user: data.user,
    role: profile?.role || 'user',
    isAdmin: profile?.role === 'admin'
  }
}
```

### 4. Auth Callback 處理（Next.js）

```javascript
// app/auth/callback/route.js
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')

  if (code) {
    const supabase = await createClient()
    await supabase.auth.exchangeCodeForSession(code)
  }

  return NextResponse.redirect(`${origin}/dashboard`)
}
```

---

## 四、RLS 權限規則

### 1. 基本 RLS 設定

```sql
-- 啟用 RLS（必須！）
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- ========== profiles RLS ==========

-- 所有人可讀
CREATE POLICY "profiles_select_all"
  ON public.profiles FOR SELECT
  USING (true);

-- 只能改自己
CREATE POLICY "profiles_update_own"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- ========== posts RLS ==========

-- 已發布文章所有人可讀
CREATE POLICY "posts_select_published"
  ON public.posts FOR SELECT
  USING (status = 'published');

-- 作者可讀自己所有文章
CREATE POLICY "posts_select_own"
  ON public.posts FOR SELECT
  USING (auth.uid() = author_id);

-- 作者可新增
CREATE POLICY "posts_insert_authenticated"
  ON public.posts FOR INSERT
  WITH CHECK (auth.uid() = author_id);

-- 作者可改自己的
CREATE POLICY "posts_update_own"
  ON public.posts FOR UPDATE
  USING (auth.uid() = author_id);

-- 作者可刪自己的
CREATE POLICY "posts_delete_own"
  ON public.posts FOR DELETE
  USING (auth.uid() = author_id);
```

### 2. 管理者全權限模式

```sql
-- 建立 is_admin 輔助函式
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 管理者可讀所有
CREATE POLICY "admin_select_all"
  ON public.posts FOR SELECT
  USING (public.is_admin());

-- 管理者可改所有
CREATE POLICY "admin_update_all"
  ON public.posts FOR UPDATE
  USING (public.is_admin());

-- 管理者可刪所有
CREATE POLICY "admin_delete_all"
  ON public.posts FOR DELETE
  USING (public.is_admin());

-- 管理者可新增
CREATE POLICY "admin_insert_all"
  ON public.posts FOR INSERT
  WITH CHECK (public.is_admin());
```

### 3. 多角色權限模板

```sql
-- 角色層級函式
CREATE OR REPLACE FUNCTION public.has_role(required_role TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  user_role TEXT;
BEGIN
  SELECT role INTO user_role FROM public.profiles WHERE id = auth.uid();

  -- 權限層級：admin > editor > user
  IF required_role = 'user' THEN
    RETURN user_role IN ('user', 'editor', 'admin');
  ELSIF required_role = 'editor' THEN
    RETURN user_role IN ('editor', 'admin');
  ELSIF required_role = 'admin' THEN
    RETURN user_role = 'admin';
  END IF;

  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 五、CRUD 操作

### 1. 基本 CRUD

```javascript
// === 查詢（Read） ===
// 全部
const { data, error } = await supabase
  .from('posts')
  .select('*')

// 帶關聯
const { data } = await supabase
  .from('posts')
  .select(`
    *,
    author:profiles(display_name, avatar_url)
  `)

// 篩選 + 分頁 + 排序
const { data, count } = await supabase
  .from('posts')
  .select('*', { count: 'exact' })
  .eq('status', 'published')
  .order('created_at', { ascending: false })
  .range(0, 9)  // 前 10 筆

// 搜尋
const { data } = await supabase
  .from('posts')
  .select('*')
  .ilike('title', `%${keyword}%`)

// === 新增（Create） ===
const { data, error } = await supabase
  .from('posts')
  .insert({
    title: '新文章',
    content: '內容...',
    author_id: user.id,
    status: 'draft'
  })
  .select()
  .single()

// 批次新增
const { data, error } = await supabase
  .from('posts')
  .insert([
    { title: '文章1', content: '...' },
    { title: '文章2', content: '...' },
  ])
  .select()

// === 更新（Update） ===
const { data, error } = await supabase
  .from('posts')
  .update({ title: '新標題', status: 'published' })
  .eq('id', postId)
  .select()
  .single()

// === 刪除（Delete） ===
const { error } = await supabase
  .from('posts')
  .delete()
  .eq('id', postId)
```

### 2. 即時訂閱（Realtime）

```javascript
// 監聽資料變化
const channel = supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    {
      event: '*',        // INSERT, UPDATE, DELETE, *
      schema: 'public',
      table: 'posts',
    },
    (payload) => {
      console.log('變更:', payload.eventType, payload.new)
    }
  )
  .subscribe()

// 取消訂閱
supabase.removeChannel(channel)
```

---

## 六、Storage 檔案儲存

### 1. 建立 Bucket

```sql
-- 在 migration 中建立
INSERT INTO storage.buckets (id, name, public)
VALUES ('avatars', 'avatars', true);

INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', false);

-- Storage RLS
CREATE POLICY "avatars_select_public"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'avatars');

CREATE POLICY "avatars_insert_authenticated"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'avatars'
    AND auth.role() = 'authenticated'
  );

CREATE POLICY "avatars_update_own"
  ON storage.objects FOR UPDATE
  USING (
    bucket_id = 'avatars'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );
```

### 2. 前端上傳/下載

```javascript
// === 上傳 ===
const file = event.target.files[0]
const filePath = `${user.id}/${Date.now()}_${file.name}`

const { data, error } = await supabase.storage
  .from('avatars')
  .upload(filePath, file, {
    cacheControl: '3600',
    upsert: true
  })

// === 取得公開 URL ===
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(filePath)

// === 下載 ===
const { data, error } = await supabase.storage
  .from('documents')
  .download(filePath)

// === 刪除 ===
const { error } = await supabase.storage
  .from('avatars')
  .remove([filePath])

// === 列出檔案 ===
const { data, error } = await supabase.storage
  .from('avatars')
  .list(user.id, {
    limit: 20,
    offset: 0,
    sortBy: { column: 'created_at', order: 'desc' }
  })
```

---

## 七、Edge Functions

### 1. 建立與部署

```bash
# 建立新 function
supabase functions new send-email

# 本機測試
supabase functions serve send-email

# 部署
supabase functions deploy send-email
```

### 2. Edge Function 模板

```typescript
// supabase/functions/send-email/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 驗證使用者
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      {
        global: { headers: { Authorization: req.headers.get('Authorization')! } }
      }
    )

    const { data: { user }, error } = await supabase.auth.getUser()
    if (error || !user) {
      return new Response(JSON.stringify({ error: '未授權' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const body = await req.json()

    // 你的業務邏輯...

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
```

### 3. 前端呼叫 Edge Function

```javascript
const { data, error } = await supabase.functions.invoke('send-email', {
  body: { to: 'user@example.com', subject: '測試', content: '...' }
})
```

---

## 八、Netlify + Supabase 部署

### 1. 環境變數設定

```bash
# Netlify 環境變數（在 Netlify Dashboard 或 CLI 設定）
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# 如果用 SSR，額外加：
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
```

```bash
# 用 Netlify CLI 設定
netlify env:set NEXT_PUBLIC_SUPABASE_URL "https://xxxxx.supabase.co"
netlify env:set NEXT_PUBLIC_SUPABASE_ANON_KEY "eyJhbGci..."
```

### 2. Supabase Client 工廠模式

```javascript
// lib/supabase/client.js — 瀏覽器端
import { createClient } from '@supabase/supabase-js'

let supabase = null

export function getSupabase() {
  if (!supabase) {
    supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    )
  }
  return supabase
}
```

```javascript
// lib/supabase/server.js — Server 端（Next.js SSR / API Route）
import { createClient } from '@supabase/supabase-js'

export function getServiceSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    { auth: { persistSession: false } }
  )
}
```

### 3. netlify.toml 設定

```toml
[build]
  command = "npm run build"
  publish = "out"          # Next.js static export
  # publish = "dist"       # Vite
  # publish = "build"      # CRA

[build.environment]
  NODE_VERSION = "20"

# SPA fallback
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# Auth callback
[[redirects]]
  from = "/auth/callback"
  to = "/auth/callback"
  status = 200
```

### 4. Supabase Auth Redirect 設定

在 Supabase Dashboard > Authentication > URL Configuration：
- **Site URL**: `https://your-site.netlify.app`
- **Redirect URLs**: `https://your-site.netlify.app/auth/callback`

---

## 九、常用 CLI 指令速查

```bash
# ===== 專案管理 =====
supabase init                          # 初始化
supabase link --project-ref <ID>       # 連結遠端
supabase status                        # 查看狀態

# ===== 資料庫 =====
supabase migration new <name>          # 新 migration
supabase db push                       # 推送到遠端
supabase db pull                       # 拉回遠端結構
supabase db reset                      # 重置本機 DB
supabase migration list                # 列出 migration

# ===== 型別產生 =====
supabase gen types typescript --linked > src/types/database.ts

# ===== Edge Functions =====
supabase functions new <name>          # 建立
supabase functions serve <name>        # 本機測試
supabase functions deploy <name>       # 部署
supabase functions deploy              # 部署全部

# ===== 密鑰 =====
supabase secrets set KEY=VALUE         # 設定密鑰
supabase secrets list                  # 列出密鑰

# ===== 檢查 =====
supabase inspect db locks              # 查看 DB 鎖定
supabase inspect db table-sizes        # 資料表大小
```

---

## 十、完整專案架構範例

```
my-supabase-app/
├── public/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── SignupForm.jsx
│   │   │   └── AuthGuard.jsx          # 路由保護
│   │   ├── Admin/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DataTable.jsx          # 通用 CRUD 表格
│   │   │   └── AdminGuard.jsx         # 管理者路由保護
│   │   └── Layout/
│   ├── lib/
│   │   └── supabase/
│   │       ├── client.js              # 瀏覽器端 client
│   │       └── server.js              # Server 端 client
│   ├── hooks/
│   │   ├── useAuth.js                 # Auth 狀態 hook
│   │   └── useSupabaseQuery.js        # 通用查詢 hook
│   ├── types/
│   │   └── database.ts               # 自動產生的型別
│   └── pages/ or app/
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   │   ├── 20260316000001_create_profiles.sql
│   │   ├── 20260316000002_create_posts.sql
│   │   └── 20260316000003_enable_rls.sql
│   ├── functions/
│   │   └── send-email/
│   │       └── index.ts
│   └── seed.sql
├── netlify.toml
├── .env.local                         # 本機環境變數
├── .env.example                       # 環境變數範本
└── package.json
```

---

## 十一、安全注意事項

1. **永遠啟用 RLS** — 沒有 RLS 的表等於公開讀寫
2. **anon key 是公開的** — 安全性完全靠 RLS，不要把 service_role_key 放在前端
3. **service_role_key** — 只用在 server 端（Edge Functions、API Routes），繞過所有 RLS
4. **.env 檔不能 commit** — 加入 `.gitignore`
5. **密碼要求** — Supabase Auth 預設最少 6 碼，可在 Dashboard 調整
6. **Email 確認** — 預設開啟，開發時可在 Dashboard > Auth > Settings 關閉

---

## 十二、疑難排解

| 問題 | 解法 |
|------|------|
| `permission denied for table` | 檢查 RLS policy，確認啟用且有對應規則 |
| `JWT expired` | 前端呼叫 `supabase.auth.refreshSession()` |
| `relation does not exist` | 執行 `supabase db push` 套用 migration |
| `new row violates RLS` | 檢查 INSERT 的 WITH CHECK 條件 |
| `supabase link` 失敗 | 確認 access token 有效，重新 `supabase login` |
| CORS 錯誤 | Edge Function 要加 corsHeaders，或檢查 Supabase Dashboard 設定 |
| 本機 vs 遠端不同步 | `supabase db pull` 拉回遠端，再 `supabase db push` |

## 升級補充：通用全端架構參考

若需求不只是在 Supabase 上完成 CRUD，而是包含：

- 更完整的 API 設計
- 認證流程與服務分層
- SSE / WebSocket 等即時功能
- 更一般化的前後端整合與部署加固

請加讀：

- `references/general-fullstack-upgrade/SKILL.md`
- `references/general-fullstack-upgrade/references/`

