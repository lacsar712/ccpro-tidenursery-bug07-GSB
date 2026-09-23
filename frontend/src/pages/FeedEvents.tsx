import { FormEvent, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { FeedEvent, Pond } from '../types'

function nowLocal() {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

const empty = {
  pondId: 0,
  fedAt: nowLocal(),
  feedType: '轮虫',
  amountKg: 1,
  operatorName: '水质技术员',
}

export default function FeedEvents() {
  const [ponds, setPonds] = useState<Pond[]>([])
  const [rows, setRows] = useState<FeedEvent[]>([])
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')

  async function load() {
    const [ps, es] = await Promise.all([
      api<Pond[]>('/api/ponds'),
      // 近七日列表,与看板汇总共用后端同一东八区划界函数
      api<FeedEvent[]>('/api/feed-events?lastDays=7'),
    ])
    setPonds(ps)
    setRows(es)
    if (!form.pondId && ps[0]) {
      setForm((f) => ({ ...f, pondId: ps[0].id }))
    }
  }

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (!form.operatorName.trim()) {
      setError('操作人不能为空')
      return
    }
    try {
      await api('/api/feed-events', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          operatorName: form.operatorName.trim(),
          fedAt: new Date(form.fedAt).toISOString(),
        }),
      })
      setForm((f) => ({ ...empty, pondId: f.pondId, fedAt: nowLocal() }))
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该投喂记录？')) return
    try {
      await api(`/api/feed-events/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  const pondLabel = (id: number) => {
    const p = ponds.find((x) => x.id === id)
    return p ? `${p.pondCode} (${p.species})` : `#${id}`
  }

  // 即“近七日列表过滤后的千克合计”,应与看板汇总卡完全相等
  const totalKg = rows.reduce((sum, r) => sum + r.amountKg, 0)

  return (
    <div>
      <header className="page-header">
        <h1>投喂事件</h1>
        <p className="muted">记录饵料类型、投喂量与操作人 · 列表与汇总均按东八区近 7 日</p>
      </header>
      {error && <div className="error">{error}</div>}

      <form className="panel form-grid" onSubmit={onSubmit}>
        <label>
          塘口
          <select
            value={form.pondId}
            onChange={(e) => setForm({ ...form, pondId: Number(e.target.value) })}
            required
          >
            {ponds.map((p) => (
              <option key={p.id} value={p.id}>
                {p.pondCode} · {p.species}
              </option>
            ))}
          </select>
        </label>
        <label>
          投喂时间
          <input
            type="datetime-local"
            value={form.fedAt}
            onChange={(e) => setForm({ ...form, fedAt: e.target.value })}
            required
          />
        </label>
        <label>
          饵料类型
          <input
            value={form.feedType}
            onChange={(e) => setForm({ ...form, feedType: e.target.value })}
            required
          />
        </label>
        <label>
          投喂量 kg
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={form.amountKg}
            onChange={(e) => setForm({ ...form, amountKg: Number(e.target.value) })}
            required
          />
        </label>
        <label>
          操作人
          <input
            value={form.operatorName}
            onChange={(e) => setForm({ ...form, operatorName: e.target.value })}
            required
          />
        </label>
        <button type="submit" className="btn primary">
          登记投喂
        </button>
      </form>

      <div className="table-wrap">
        <div className="list-total muted">
          东八区近 7 日列表合计:<strong>{totalKg.toFixed(2)} kg</strong>
          (应与看板「近 7 日投喂总量」一致)
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>塘口</th>
              <th>投喂时间</th>
              <th>饵料</th>
              <th>数量 kg</th>
              <th>操作人</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{pondLabel(r.pondId)}</td>
                <td>{new Date(r.fedAt).toLocaleString()}</td>
                <td>{r.feedType}</td>
                <td>{r.amountKg}</td>
                <td>{r.operatorName}</td>
                <td>
                  <button className="btn ghost" onClick={() => remove(r.id)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
