# Supabase CRUD 元件模板

## 1. 通用 DataTable 管理元件

```jsx
import { useState, useEffect } from 'react'
import { getSupabase } from '@/lib/supabase/client'

export function DataTable({
  table,               // 資料表名稱
  columns,             // 欄位定義 [{ key, label, type, editable }]
  defaultSort = 'created_at',
  pageSize = 10,
  canCreate = true,
  canEdit = true,
  canDelete = true,
}) {
  const [data, setData] = useState([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [newForm, setNewForm] = useState({})
  const [showNew, setShowNew] = useState(false)
  const supabase = getSupabase()

  // 載入資料
  async function fetchData() {
    setLoading(true)
    const from = page * pageSize
    const to = from + pageSize - 1

    const { data, count, error } = await supabase
      .from(table)
      .select('*', { count: 'exact' })
      .order(defaultSort, { ascending: false })
      .range(from, to)

    if (!error) {
      setData(data)
      setCount(count)
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [page])

  // 新增
  async function handleCreate() {
    const { error } = await supabase
      .from(table)
      .insert(newForm)

    if (!error) {
      setNewForm({})
      setShowNew(false)
      fetchData()
    } else {
      alert('新增失敗: ' + error.message)
    }
  }

  // 更新
  async function handleUpdate(id) {
    const { error } = await supabase
      .from(table)
      .update(editForm)
      .eq('id', id)

    if (!error) {
      setEditingId(null)
      setEditForm({})
      fetchData()
    } else {
      alert('更新失敗: ' + error.message)
    }
  }

  // 刪除
  async function handleDelete(id) {
    if (!confirm('確定要刪除嗎？')) return

    const { error } = await supabase
      .from(table)
      .delete()
      .eq('id', id)

    if (!error) {
      fetchData()
    } else {
      alert('刪除失敗: ' + error.message)
    }
  }

  const totalPages = Math.ceil(count / pageSize)

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">{table} 管理</h2>
        {canCreate && (
          <button
            onClick={() => setShowNew(!showNew)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + 新增
          </button>
        )}
      </div>

      {/* 新增表單 */}
      {showNew && (
        <div className="mb-4 p-4 border rounded bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            {columns.filter(c => c.editable !== false).map(col => (
              <div key={col.key}>
                <label className="block text-sm font-medium mb-1">{col.label}</label>
                <input
                  type={col.type || 'text'}
                  value={newForm[col.key] || ''}
                  onChange={e => setNewForm({ ...newForm, [col.key]: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            <button onClick={handleCreate} className="px-4 py-2 bg-green-600 text-white rounded">
              儲存
            </button>
            <button onClick={() => setShowNew(false)} className="px-4 py-2 bg-gray-300 rounded">
              取消
            </button>
          </div>
        </div>
      )}

      {/* 資料表格 */}
      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-100">
            {columns.map(col => (
              <th key={col.key} className="border p-2 text-left">{col.label}</th>
            ))}
            {(canEdit || canDelete) && <th className="border p-2">操作</th>}
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id} className="hover:bg-gray-50">
              {columns.map(col => (
                <td key={col.key} className="border p-2">
                  {editingId === row.id && col.editable !== false ? (
                    <input
                      type={col.type || 'text'}
                      value={editForm[col.key] ?? row[col.key] ?? ''}
                      onChange={e => setEditForm({ ...editForm, [col.key]: e.target.value })}
                      className="w-full px-2 py-1 border rounded"
                    />
                  ) : (
                    row[col.key]
                  )}
                </td>
              ))}
              {(canEdit || canDelete) && (
                <td className="border p-2 text-center">
                  {editingId === row.id ? (
                    <div className="flex gap-1 justify-center">
                      <button onClick={() => handleUpdate(row.id)} className="text-green-600">儲存</button>
                      <button onClick={() => setEditingId(null)} className="text-gray-600">取消</button>
                    </div>
                  ) : (
                    <div className="flex gap-1 justify-center">
                      {canEdit && (
                        <button
                          onClick={() => { setEditingId(row.id); setEditForm(row) }}
                          className="text-blue-600"
                        >
                          編輯
                        </button>
                      )}
                      {canDelete && (
                        <button onClick={() => handleDelete(row.id)} className="text-red-600">
                          刪除
                        </button>
                      )}
                    </div>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {/* 分頁 */}
      <div className="mt-4 flex justify-between items-center">
        <span className="text-sm text-gray-600">共 {count} 筆，第 {page + 1} / {totalPages} 頁</span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            上一頁
          </button>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            下一頁
          </button>
        </div>
      </div>
    </div>
  )
}
```

## 2. 使用範例

```jsx
// 在管理頁面使用
<DataTable
  table="posts"
  columns={[
    { key: 'title', label: '標題', editable: true },
    { key: 'status', label: '狀態', editable: true },
    { key: 'created_at', label: '建立時間', editable: false },
  ]}
  defaultSort="created_at"
  pageSize={15}
/>
```

## 3. LoginForm 登入元件

```jsx
import { useState } from 'react'
import { getSupabase } from '@/lib/supabase/client'

export function LoginForm({ onSuccess, onSignupClick }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const supabase = getSupabase()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email, password
    })

    if (authError) {
      setError(authError.message === 'Invalid login credentials'
        ? '帳號或密碼錯誤'
        : authError.message
      )
      setLoading(false)
      return
    }

    onSuccess?.(data.user)
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6 text-center">登入</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-1">密碼</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          minLength={6}
          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? '登入中...' : '登入'}
      </button>

      {onSignupClick && (
        <p className="mt-4 text-center text-sm text-gray-600">
          還沒有帳號？
          <button type="button" onClick={onSignupClick} className="text-blue-600 hover:underline ml-1">
            註冊
          </button>
        </p>
      )}
    </form>
  )
}
```
