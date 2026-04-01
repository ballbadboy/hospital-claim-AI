# Phase 3: Dashboard + Reports — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Excel report generation backend and React dashboard frontend for KPI visibility, claim management, and report export.

**Architecture:** Report engine generates Excel via openpyxl. New API routes serve report data + file downloads. React frontend (Vite + TailwindCSS + Recharts + TanStack Query) consumes existing + new API endpoints.

**Tech Stack:** Backend: openpyxl (existing), FastAPI. Frontend: Vite, React 18, TailwindCSS, Recharts, TanStack Query.

---

### Task 1: Report engine (Excel generation)

**Files:**
- Create: `core/report_engine.py`
- Create: `tests/test_report_engine.py`

### Task 2: Report API routes

**Files:**
- Create: `api/routes_reports.py`
- Modify: `api/main.py` — include reports router

### Task 3: Claims list API with pagination/filters

**Files:**
- Modify: `api/routes.py` — add `/claims` list endpoint with pagination

### Task 4: React frontend scaffolding

**Files:**
- Create: `dashboard/` — Vite + React + TailwindCSS project

### Task 5: Dashboard page with KPI cards + charts

**Files:**
- Create: dashboard components (KPICards, DenyReasonChart, DepartmentTable)

### Task 6: Claims list page + ClaimView detail page

### Task 7: Reports page + CSV batch uploader

### Task 8: Wire frontend to backend + final verification
