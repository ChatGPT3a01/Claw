# Supabase Auth 進階模式

## 1. AuthGuard 路由保護元件（React）

```jsx
import { useEffect, useState } from 'react'
import { getSupabase } from '@/lib/supabase/client'

export function AuthGuard({ children, fallback = null }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const supabase = getSupabase()

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  if (loading) return <div>載入中...</div>
  if (!user) return fallback || <LoginRedirect />
  return children
}
```

## 2. AdminGuard 管理者保護

```jsx
import { useEffect, useState } from 'react'
import { getSupabase } from '@/lib/supabase/client'

export function AdminGuard({ children, fallback = null }) {
  const [isAdmin, setIsAdmin] = useState(false)
  const [loading, setLoading] = useState(true)
  const supabase = getSupabase()

  useEffect(() => {
    async function checkAdmin() {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) { setLoading(false); return }

      const { data: profile } = await supabase
        .from('profiles')
        .select('role')
        .eq('id', user.id)
        .single()

      setIsAdmin(profile?.role === 'admin')
      setLoading(false)
    }
    checkAdmin()
  }, [])

  if (loading) return <div>驗證權限中...</div>
  if (!isAdmin) return fallback || <div>無權限存取</div>
  return children
}
```

## 3. useAuth Hook

```jsx
import { useEffect, useState } from 'react'
import { getSupabase } from '@/lib/supabase/client'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const supabase = getSupabase()

  useEffect(() => {
    async function loadUser() {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)

      if (user) {
        const { data } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single()
        setProfile(data)
      }
      setLoading(false)
    }

    loadUser()

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        const currentUser = session?.user ?? null
        setUser(currentUser)
        if (currentUser) {
          const { data } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', currentUser.id)
            .single()
          setProfile(data)
        } else {
          setProfile(null)
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    return { data, error }
  }

  const signUp = async (email, password, metadata = {}) => {
    const { data, error } = await supabase.auth.signUp({
      email, password,
      options: { data: metadata }
    })
    return { data, error }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setProfile(null)
  }

  return {
    user,
    profile,
    loading,
    isAuthenticated: !!user,
    isAdmin: profile?.role === 'admin',
    signIn,
    signUp,
    signOut,
  }
}
```

## 4. 密碼重設流程

```javascript
// 1. 發送重設信
const { error } = await supabase.auth.resetPasswordForEmail(email, {
  redirectTo: `${window.location.origin}/auth/reset-password`,
})

// 2. 在 reset-password 頁面更新密碼
const { error } = await supabase.auth.updateUser({
  password: newPassword
})
```

## 5. 管理者手動建立使用者（Server 端）

```javascript
import { getServiceSupabase } from '@/lib/supabase/server'

// 用 service_role_key 建立使用者（繞過 email 確認）
const supabase = getServiceSupabase()

const { data, error } = await supabase.auth.admin.createUser({
  email: 'newuser@example.com',
  password: 'tempPassword123',
  email_confirm: true,  // 跳過 email 確認
  user_metadata: {
    display_name: '新使用者'
  }
})

// 設定角色
await supabase
  .from('profiles')
  .update({ role: 'editor' })
  .eq('id', data.user.id)
```
