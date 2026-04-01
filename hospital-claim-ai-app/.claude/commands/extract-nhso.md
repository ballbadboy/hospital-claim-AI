ดึงความรู้จากแหล่ง สปสช.

Input: $ARGUMENTS (YouTube URL, PDF path, หรือ MOOC topic)

แหล่งข้อมูล 3 ทาง:
1. YouTube @nhsothailand → ใช้ youtube-skill-extractor
2. NHSO MOOC (mooc.nhso.go.th) → สรุปเป็น markdown
3. PDF Spec → อ่านและสรุป

Output: structured markdown ใน references/
- youtube → references/youtube-extracted/
- nhso rules → references/nhso-rules/
- hospital data → references/hospital-data/
