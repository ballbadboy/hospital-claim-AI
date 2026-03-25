import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useClaims } from '../api/hooks'

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-700',
  checked: 'bg-blue-100 text-blue-700',
  ready: 'bg-green-100 text-green-700',
  submitted: 'bg-purple-100 text-purple-700',
  approved: 'bg-green-100 text-green-800',
  denied: 'bg-red-100 text-red-700',
  cancelled: 'bg-gray-200 text-gray-500',
}

export default function ClaimsPage() {
  const [page, setPage] = useState(1)
  const [department, setDepartment] = useState('')
  const [status, setStatus] = useState('')
  const { data, isLoading } = useClaims(page, 20, {
    ...(department && { department }),
    ...(status && { fdh_status: status }),
  })

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Claims</h2>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select value={department} onChange={e => { setDepartment(e.target.value); setPage(1) }}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">ทุกแผนก</option>
          <option value="cath_lab">Cath Lab</option>
          <option value="or_surgery">OR Surgery</option>
          <option value="chemo">Chemo</option>
          <option value="dialysis">Dialysis</option>
          <option value="icu_nicu">ICU/NICU</option>
          <option value="er_ucep">ER/UCEP</option>
          <option value="ods_mis">ODS/MIS</option>
          <option value="opd_ncd">OPD/NCD</option>
          <option value="rehab_palliative">Rehab</option>
        </select>
        <select value={status} onChange={e => { setStatus(e.target.value); setPage(1) }}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">ทุกสถานะ</option>
          <option value="pending">Pending</option>
          <option value="checked">Checked</option>
          <option value="ready">Ready</option>
          <option value="submitted">Submitted</option>
          <option value="approved">Approved</option>
          <option value="denied">Denied</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">AN</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">HN</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">แผนก</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">PDx</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Score</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">สถานะ</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">วันที่</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr><td colSpan={7} className="px-6 py-12 text-center text-gray-400">กำลังโหลด...</td></tr>
            ) : data?.claims?.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-12 text-center text-gray-400">ไม่พบเคส</td></tr>
            ) : (
              data?.claims?.map((c: any) => (
                <tr key={c.an} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link to={`/claims/${c.an}`} className="text-blue-600 hover:underline font-medium">{c.an}</Link>
                  </td>
                  <td className="px-6 py-4 text-gray-600">{c.hn}</td>
                  <td className="px-6 py-4 text-gray-600">{c.department}</td>
                  <td className="px-6 py-4 font-mono text-sm">{c.principal_dx}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`font-bold ${c.score >= 80 ? 'text-green-600' : c.score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {c.score}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[c.fdh_status] || 'bg-gray-100'}`}>
                      {c.fdh_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString('th-TH') : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="px-6 py-4 border-t flex items-center justify-between">
            <span className="text-sm text-gray-500">
              แสดง {((page - 1) * 20) + 1}-{Math.min(page * 20, data.total)} จาก {data.total} เคส
            </span>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}
                className="px-3 py-1 border rounded text-sm disabled:opacity-30">ก่อนหน้า</button>
              <span className="px-3 py-1 text-sm">หน้า {page}/{data.pages}</span>
              <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page >= data.pages}
                className="px-3 py-1 border rounded text-sm disabled:opacity-30">ถัดไป</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
