import { useParams, Link } from 'react-router-dom'
import { useClaimStatus } from '../api/hooks'
import api from '../api/client'

export default function ClaimViewPage() {
  const { an } = useParams<{ an: string }>()
  const { data, isLoading, error } = useClaimStatus(an || '')

  if (isLoading) return <div className="text-center py-12 text-gray-500">กำลังโหลด...</div>
  if (error) return <div className="text-center py-12 text-red-500">ไม่พบเคส {an}</div>

  const downloadAudit = async () => {
    const response = await api.get(`/reports/audit/${an}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_trail_${an}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div>
      <Link to="/claims" className="text-blue-600 hover:underline text-sm mb-4 inline-block">&larr; กลับไปรายการเคส</Link>
      <h2 className="text-2xl font-bold mb-6">เคส {data.an}</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">ข้อมูลเคส</h3>
          <dl className="space-y-2">
            <div className="flex justify-between"><dt className="text-gray-500">HN</dt><dd className="font-medium">{data.hn}</dd></div>
            <div className="flex justify-between"><dt className="text-gray-500">AN</dt><dd className="font-medium">{data.an}</dd></div>
            <div className="flex justify-between"><dt className="text-gray-500">แผนก</dt><dd className="font-medium">{data.department}</dd></div>
            <div className="flex justify-between"><dt className="text-gray-500">Score</dt>
              <dd className={`font-bold ${data.score >= 80 ? 'text-green-600' : data.score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>{data.score}/100</dd>
            </div>
            <div className="flex justify-between"><dt className="text-gray-500">สถานะ FDH</dt><dd className="font-medium">{data.fdh_status}</dd></div>
            <div className="flex justify-between"><dt className="text-gray-500">สถานะอุทธรณ์</dt><dd className="font-medium">{data.appeal_status || 'none'}</dd></div>
            <div className="flex justify-between"><dt className="text-gray-500">พร้อมส่งเบิก</dt>
              <dd className={data.ready_to_submit ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                {data.ready_to_submit ? 'พร้อม' : 'ยังไม่พร้อม'}
              </dd>
            </div>
          </dl>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Audit Trail</h3>
            <button onClick={downloadAudit} className="text-sm text-blue-600 hover:underline">Download Excel</button>
          </div>
          {data.audit_trail?.length === 0 ? (
            <p className="text-gray-400">ยังไม่มี audit trail</p>
          ) : (
            <div className="space-y-3">
              {data.audit_trail?.map((entry: any, i: number) => (
                <div key={i} className="border-l-2 border-blue-200 pl-4 py-1">
                  <p className="font-medium text-sm">{entry.action}</p>
                  <p className="text-xs text-gray-400">{entry.user} — {entry.at ? new Date(entry.at).toLocaleString('th-TH') : ''}</p>
                  {entry.details && Object.keys(entry.details).length > 0 && (
                    <p className="text-xs text-gray-500 mt-1">{JSON.stringify(entry.details)}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
