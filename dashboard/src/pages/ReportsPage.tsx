import { useState } from 'react'
import api from '../api/client'

export default function ReportsPage() {
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)

  const downloadMonthly = async () => {
    const response = await api.get(`/reports/monthly`, {
      params: { year, month },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `monthly_summary_${year}_${String(month).padStart(2, '0')}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  }

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadResult(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/check/csv', formData)
      setUploadResult(response.data)
    } catch (err: any) {
      setUploadResult({ error: err.response?.data?.detail || 'Upload failed' })
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Reports & Upload</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Excel Reports */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">สรุปรายเดือน (Excel)</h3>
          <div className="flex gap-3 mb-4">
            <select value={year} onChange={e => setYear(Number(e.target.value))}
              className="border rounded-lg px-3 py-2 text-sm">
              {[2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
            </select>
            <select value={month} onChange={e => setMonth(Number(e.target.value))}
              className="border rounded-lg px-3 py-2 text-sm">
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>{String(i + 1).padStart(2, '0')}</option>
              ))}
            </select>
            <button onClick={downloadMonthly}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
              Download Excel
            </button>
          </div>
          <p className="text-xs text-gray-400">รายงานสรุป deny rate, revenue, สาเหตุ deny แยกตามแผนก</p>
        </div>

        {/* CSV Upload */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">อัปโหลด CSV ตรวจเคส</h3>
          <label className="block border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors">
            <input type="file" accept=".csv" onChange={handleCSVUpload} className="hidden" />
            {uploading ? (
              <p className="text-blue-600">กำลังตรวจ...</p>
            ) : (
              <>
                <p className="text-gray-500">คลิกหรือลากไฟล์ CSV มาวาง</p>
                <p className="text-xs text-gray-400 mt-1">รองรับไฟล์จาก FDH Dashboard (สูงสุด 500 เคส, 5MB)</p>
              </>
            )}
          </label>

          {uploadResult && !uploadResult.error && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <p className="font-semibold text-green-800">ตรวจเสร็จ {uploadResult.total} เคส</p>
              <div className="flex gap-4 mt-2 text-sm">
                <span className="text-green-600">พร้อมส่ง: {uploadResult.ready}</span>
                <span className="text-red-600">มีปัญหา: {uploadResult.issues}</span>
                <span className="text-red-700">Critical: {uploadResult.critical_total}</span>
              </div>
            </div>
          )}

          {uploadResult?.error && (
            <div className="mt-4 p-4 bg-red-50 rounded-lg">
              <p className="text-red-700">{uploadResult.error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
