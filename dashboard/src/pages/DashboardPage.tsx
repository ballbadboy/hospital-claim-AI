import { useDashboardStats } from '../api/hooks'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#2563EB', '#EF4444', '#F59E0B', '#10B981', '#8B5CF6', '#EC4899']

function KPICard({ label, value, subtitle, color = 'blue' }: {
  label: string; value: string | number; subtitle?: string; color?: string
}) {
  const colorMap: Record<string, string> = {
    blue: 'border-blue-500', red: 'border-red-500', green: 'border-green-500', yellow: 'border-yellow-500',
  }
  return (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${colorMap[color] || 'border-blue-500'}`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboardStats()

  if (isLoading) return <div className="text-center py-12 text-gray-500">กำลังโหลด...</div>
  if (error) return <div className="text-center py-12 text-red-500">ไม่สามารถโหลดข้อมูลได้</div>

  const deptData = data.by_department
    ? Object.entries(data.by_department).map(([name, d]: [string, any]) => ({
        name, total: d.total, denied: d.denied, deny_rate: d.deny_rate,
      }))
    : []

  const denyReasonData = data.by_deny_reason
    ? Object.entries(data.by_deny_reason).map(([name, count]) => ({ name, value: count as number }))
    : []

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label="เคสทั้งหมด" value={data.total_claims?.toLocaleString() || 0} color="blue" />
        <KPICard label="Deny Rate" value={`${data.deny_rate || 0}%`} subtitle={`${data.denied_claims || 0} เคส`} color="red" />
        <KPICard label="Revenue at Risk" value={`฿${(data.revenue_at_risk || 0).toLocaleString()}`} color="yellow" />
        <KPICard label="Revenue Recovered" value={`฿${(data.revenue_recovered || 0).toLocaleString()}`} color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Deny Reasons Chart */}
        {denyReasonData.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">สาเหตุ Deny</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={denyReasonData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {denyReasonData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Department Chart */}
        {deptData.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Deny Rate แยกตามแผนก</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={deptData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis unit="%" />
                <Tooltip />
                <Bar dataKey="deny_rate" fill="#2563EB" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Department Table */}
      {deptData.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <h3 className="text-lg font-semibold p-6 pb-3">KPI แยกตามแผนก</h3>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">แผนก</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">เคสทั้งหมด</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">ถูก Deny</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Deny Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {deptData.map(d => (
                <tr key={d.name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium">{d.name}</td>
                  <td className="px-6 py-4 text-right">{d.total}</td>
                  <td className="px-6 py-4 text-right">{d.denied}</td>
                  <td className="px-6 py-4 text-right">{d.deny_rate}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty state */}
      {data.total_claims === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center text-gray-400">
          <p className="text-lg">ยังไม่มีข้อมูลเคส</p>
          <p className="text-sm mt-2">เริ่มตรวจเคสโดยอัปโหลด CSV หรือเชื่อมต่อ HIS</p>
        </div>
      )}
    </div>
  )
}
