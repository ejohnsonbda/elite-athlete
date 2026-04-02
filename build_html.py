#!/usr/bin/env python3
"""
Build the Elite Athlete Sponsorship Dashboard HTML file.
Reads applicants.json and injects data into a single-file HTML app.
"""
import json
import os

with open('/home/ubuntu/elite-athlete-work/applicants.json', encoding='utf-8') as f:
    applicants = json.load(f)

applicants_json = json.dumps(applicants, ensure_ascii=False)

# Unique sports for filter
sports = sorted(set(a['sport'].strip().title() for a in applicants if a['sport']))
sport_options = '\n'.join(f'<option value="{s}">{s}</option>' for s in sports)

# Total stats
total_amount = sum(a['totalAmountNum'] for a in applicants)
total_str = f'${total_amount:,.0f}'

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Elite Athlete Sponsorship Applications 2025 — Bermuda</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
  <style>
    /* ===== RESET & BASE ===== */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --navy:   #0A2342;
      --navy2:  #123363;
      --white:  #FFFFFF;
      --gold:   #C9A84C;
      --gold2:  #E8C96A;
      --gold-light: #FDF6E3;
      --gray:   #F4F6F9;
      --gray2:  #E8ECF2;
      --gray3:  #9AA5B4;
      --text:   #1A2B3C;
      --border: #D0D9E8;
      --shadow: 0 2px 12px rgba(10,35,66,0.10);
      --shadow2: 0 4px 24px rgba(10,35,66,0.16);
      --green:  #2e7d32;
      --red:    #c62828;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--gray);
      color: var(--text);
      min-height: 100vh;
    }}

    /* ===== LOGIN SCREEN ===== */
    #login-screen {{
      position: fixed; inset: 0; z-index: 9999;
      background: linear-gradient(135deg, var(--navy) 0%, #0d1f3c 60%, #1a0a2e 100%);
      display: flex; align-items: center; justify-content: center;
    }}
    .login-box {{
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 20px;
      padding: 48px 40px;
      width: 100%; max-width: 420px;
      text-align: center;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 40px rgba(0,0,0,0.4);
    }}
    .login-logo {{
      width: 72px; height: 72px;
      background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 100%);
      border-radius: 18px;
      display: flex; align-items: center; justify-content: center;
      font-size: 2rem; margin: 0 auto 20px;
    }}
    .login-box h1 {{
      color: #fff; font-size: 1.5rem; font-weight: 700; margin-bottom: 6px;
    }}
    .login-box p {{
      color: rgba(255,255,255,0.6); font-size: 0.88rem; margin-bottom: 28px;
    }}
    .login-input {{
      width: 100%; padding: 14px 18px;
      background: rgba(255,255,255,0.1);
      border: 1.5px solid rgba(255,255,255,0.2);
      border-radius: 10px; color: #fff;
      font-size: 1.1rem; text-align: center;
      letter-spacing: 4px; font-weight: 700;
      outline: none; transition: border-color 0.2s;
      margin-bottom: 14px;
    }}
    .login-input::placeholder {{ letter-spacing: 1px; font-weight: 400; color: rgba(255,255,255,0.4); }}
    .login-input:focus {{ border-color: var(--gold); }}
    .login-input.error {{ border-color: #ef5350; animation: shake 0.4s; }}
    @keyframes shake {{
      0%,100%{{transform:translateX(0)}} 20%{{transform:translateX(-8px)}} 60%{{transform:translateX(8px)}}
    }}
    .login-btn {{
      width: 100%; padding: 14px;
      background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 100%);
      color: var(--navy); border: none; border-radius: 10px;
      font-size: 1rem; font-weight: 700; cursor: pointer;
      letter-spacing: 0.05em; transition: opacity 0.2s;
    }}
    .login-btn:hover {{ opacity: 0.9; }}
    .login-btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
    .login-error {{
      color: #ef9a9a; font-size: 0.82rem;
      margin-top: 10px; min-height: 20px;
    }}

    /* ===== APP SHELL ===== */
    #app-shell {{ display: none; }}

    /* ===== HEADER ===== */
    .site-header {{
      background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
      color: var(--white);
      box-shadow: var(--shadow2);
      position: sticky; top: 0; z-index: 100;
    }}
    .header-inner {{
      max-width: 1600px; margin: 0 auto;
      padding: 16px 32px;
      display: flex; align-items: center; gap: 18px;
    }}
    .header-logo {{
      width: 52px; height: 52px;
      background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 100%);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem; flex-shrink: 0;
    }}
    .header-text h1 {{ font-size: 1.25rem; font-weight: 700; letter-spacing: -0.3px; }}
    .header-text p {{ font-size: 0.80rem; opacity: 0.70; margin-top: 2px; }}
    .header-stats {{ margin-left: auto; display: flex; gap: 28px; }}
    .hstat {{ text-align: center; }}
    .hstat-num {{ font-size: 1.5rem; font-weight: 800; color: var(--gold2); line-height: 1; }}
    .hstat-label {{ font-size: 0.70rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* ===== NAV TABS ===== */
    .nav-tabs {{
      background: var(--navy);
      border-top: 1px solid rgba(255,255,255,0.08);
    }}
    .nav-tabs-inner {{
      max-width: 1600px; margin: 0 auto;
      padding: 0 32px;
      display: flex; gap: 4px;
    }}
    .nav-tab {{
      padding: 12px 20px;
      color: rgba(255,255,255,0.65);
      font-size: 0.88rem; font-weight: 500;
      cursor: pointer; border-bottom: 3px solid transparent;
      transition: all 0.2s; background: none;
      border-top: none; border-left: none; border-right: none;
      white-space: nowrap;
    }}
    .nav-tab:hover {{ color: var(--white); }}
    .nav-tab.active {{ color: var(--white); border-bottom-color: var(--gold); font-weight: 600; }}
    .signout-btn {{
      margin-left: auto;
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.25);
      color: #fff; border-radius: 8px;
      padding: 7px 18px; font-size: 0.82rem;
      font-weight: 600; cursor: pointer;
      transition: background 0.2s; white-space: nowrap;
    }}
    .signout-btn:hover {{ background: rgba(201,168,76,0.5); }}

    /* ===== MAIN LAYOUT ===== */
    .main-content {{ max-width: 1600px; margin: 0 auto; padding: 28px 32px; }}
    .view {{ display: none; }}
    .view.active {{ display: block; }}

    /* ===== FILTER BAR ===== */
    .filter-bar {{
      background: var(--white); border-radius: 14px;
      padding: 20px 24px; box-shadow: var(--shadow);
      margin-bottom: 24px;
      display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-end;
    }}
    .filter-group {{ display: flex; flex-direction: column; gap: 5px; min-width: 150px; }}
    .filter-group label {{
      font-size: 0.75rem; font-weight: 600; color: var(--navy);
      text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .filter-group select, .filter-group input {{
      padding: 9px 12px; border: 1.5px solid var(--border);
      border-radius: 8px; font-size: 0.88rem; color: var(--text);
      background: var(--white); outline: none; transition: border-color 0.2s;
    }}
    .filter-group select:focus, .filter-group input:focus {{ border-color: var(--navy2); }}
    .filter-group.search {{ flex: 1; min-width: 220px; }}
    .filter-actions {{ display: flex; gap: 10px; align-items: flex-end; }}
    .btn {{
      padding: 9px 18px; border-radius: 8px;
      font-size: 0.88rem; font-weight: 600;
      cursor: pointer; border: none; transition: all 0.2s;
      display: inline-flex; align-items: center; gap: 6px;
    }}
    .btn-primary {{ background: var(--gold); color: var(--navy); }}
    .btn-primary:hover {{ background: var(--gold2); }}
    .btn-secondary {{ background: var(--gray2); color: var(--navy); }}
    .btn-secondary:hover {{ background: var(--border); }}

    /* ===== TABLE ===== */
    .table-wrap {{ background: var(--white); border-radius: 14px; box-shadow: var(--shadow); overflow: hidden; }}
    .table-meta {{
      padding: 14px 20px; display: flex; align-items: center;
      justify-content: space-between; border-bottom: 1px solid var(--gray2);
      flex-wrap: wrap; gap: 10px;
    }}
    .table-meta-left {{ font-size: 0.85rem; color: var(--gray3); }}
    .table-meta-left strong {{ color: var(--text); }}
    .table-meta-right {{ display: flex; gap: 10px; align-items: center; }}
    .shortlist-count-badge {{
      background: var(--gold-light); color: var(--gold);
      border-radius: 20px; padding: 4px 12px;
      font-size: 0.8rem; font-weight: 600;
    }}
    .btn-select-all {{
      background: var(--navy); color: var(--white);
      border: none; border-radius: 8px;
      padding: 7px 14px; font-size: 0.82rem;
      font-weight: 600; cursor: pointer;
    }}
    .btn-select-all:hover {{ background: var(--navy2); }}
    .table-scroll {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 1000px; }}
    thead th {{
      background: var(--navy); color: var(--white);
      padding: 12px 14px; font-size: 0.78rem;
      text-transform: uppercase; letter-spacing: 0.5px;
      font-weight: 600; white-space: nowrap;
      cursor: pointer; user-select: none;
    }}
    thead th:hover {{ background: var(--navy2); }}
    tbody tr {{ border-bottom: 1px solid var(--gray2); transition: background 0.15s; }}
    tbody tr:hover {{ background: var(--gray); }}
    tbody tr.shortlisted {{ background: #fffde7; }}
    tbody tr.shortlisted:hover {{ background: #fff9c4; }}
    td {{ padding: 11px 14px; font-size: 0.88rem; vertical-align: middle; }}
    .td-name {{ font-weight: 600; color: var(--navy); font-size: 0.92rem; }}
    .td-date {{ font-size: 0.80rem; color: var(--gray3); }}
    .td-amount {{ font-weight: 700; color: var(--green); font-size: 0.90rem; }}

    /* ===== BADGES ===== */
    .badge {{
      display: inline-block; padding: 3px 9px;
      border-radius: 20px; font-size: 0.75rem; font-weight: 600;
      white-space: nowrap; margin: 2px 1px;
    }}
    .badge-navy   {{ background: #e8edf5; color: var(--navy); }}
    .badge-gold   {{ background: var(--gold-light); color: #7a5c00; }}
    .badge-teal   {{ background: #e0f2f1; color: #00695c; }}
    .badge-green  {{ background: #e8f5e9; color: #2e7d32; }}
    .badge-purple {{ background: #ede7f6; color: #4527a0; }}
    .badge-orange {{ background: #fff3e0; color: #e65100; }}
    .badge-blue   {{ background: #e3f2fd; color: #1565c0; }}
    .badge-red    {{ background: #ffebee; color: #c62828; }}
    .badge-gray   {{ background: var(--gray2); color: var(--gray3); }}
    .files-cell {{ display: flex; flex-wrap: wrap; gap: 4px; }}
    .file-link {{
      display: inline-block; max-width: 150px;
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
      color: var(--navy2); font-size: 0.78rem; font-weight: 500;
      text-decoration: none; padding: 2px 6px;
      background: #e8edf5; border-radius: 4px;
    }}
    .file-link:hover {{ background: var(--gold-light); color: #7a5c00; }}

    /* ===== ACTION BUTTONS ===== */
    .action-btns {{ display: flex; gap: 6px; }}
    .btn-view {{
      padding: 5px 12px; background: var(--navy); color: #fff;
      border: none; border-radius: 6px; font-size: 0.80rem;
      font-weight: 600; cursor: pointer; transition: background 0.2s;
    }}
    .btn-view:hover {{ background: var(--navy2); }}
    .btn-shortlist {{
      padding: 5px 12px; background: var(--gray2); color: var(--navy);
      border: none; border-radius: 6px; font-size: 0.80rem;
      font-weight: 600; cursor: pointer; transition: all 0.2s;
    }}
    .btn-shortlist:hover {{ background: var(--gold-light); color: #7a5c00; }}
    .btn-shortlist.active {{ background: var(--gold); color: var(--navy); }}

    /* ===== PAGINATION ===== */
    .pagination {{ display: flex; justify-content: center; gap: 6px; padding: 16px; flex-wrap: wrap; }}
    .page-btn {{
      padding: 6px 12px; border-radius: 6px; border: 1.5px solid var(--border);
      background: var(--white); color: var(--text); font-size: 0.85rem;
      cursor: pointer; transition: all 0.2s;
    }}
    .page-btn:hover {{ border-color: var(--navy); color: var(--navy); }}
    .page-btn.active {{ background: var(--navy); color: #fff; border-color: var(--navy); }}
    .page-btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}

    /* ===== SHORTLIST VIEW ===== */
    .shortlist-header {{
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 20px; flex-wrap: wrap; gap: 12px;
    }}
    .shortlist-header h2 {{ font-size: 1.2rem; color: var(--navy); }}
    .shortlist-empty {{
      text-align: center; padding: 60px 20px;
      color: var(--gray3); font-size: 0.95rem;
    }}
    .shortlist-export-bar {{ display: flex; gap: 10px; flex-wrap: wrap; }}

    /* ===== STATUS DROPDOWN ===== */
    .status-select {{
      font-size: 0.75rem; padding: 4px 6px;
      border: 1.5px solid var(--gray2); border-radius: 6px;
      background: #fff; color: var(--navy); cursor: pointer; min-width: 120px;
    }}
    .status-select.status-approved {{ border-color: var(--green); background: #e8f5e9; color: var(--green); font-weight: 600; }}
    .status-select.status-pending  {{ border-color: #e65100; background: #fff3e0; color: #e65100; font-weight: 600; }}
    .status-select.status-review   {{ border-color: #1565c0; background: #e3f2fd; color: #1565c0; font-weight: 600; }}
    .status-select.status-declined {{ border-color: var(--red); background: #ffebee; color: var(--red); font-weight: 600; }}
    .status-select:focus {{ outline: none; border-color: var(--navy2); }}

    /* ===== CHARTS VIEW ===== */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 24px;
    }}
    .chart-card {{
      background: var(--white); border-radius: 14px;
      padding: 22px 24px; box-shadow: var(--shadow);
    }}
    .chart-card h3 {{
      font-size: 0.95rem; font-weight: 700; color: var(--navy);
      margin-bottom: 16px;
    }}
    .chart-wrap {{ height: 240px; position: relative; }}

    /* ===== MODAL ===== */
    .modal-overlay {{
      position: fixed; inset: 0; z-index: 500;
      background: rgba(10,35,66,0.55);
      display: none; align-items: center; justify-content: center;
      padding: 20px;
    }}
    .modal-overlay.open {{ display: flex; }}
    .modal {{
      background: var(--white); border-radius: 18px;
      width: 100%; max-width: 780px;
      max-height: 90vh; overflow-y: auto;
      box-shadow: var(--shadow2);
    }}
    .modal-header {{
      background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
      color: #fff; padding: 22px 28px;
      display: flex; align-items: center; gap: 16px;
      border-radius: 18px 18px 0 0;
      position: sticky; top: 0; z-index: 10;
    }}
    .modal-avatar {{
      width: 52px; height: 52px; border-radius: 14px;
      background: linear-gradient(135deg, var(--gold) 0%, var(--gold2) 100%);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; font-weight: 800; color: var(--navy);
      flex-shrink: 0;
    }}
    .modal-header-text h2 {{ font-size: 1.2rem; font-weight: 700; }}
    .modal-header-text p {{ font-size: 0.82rem; opacity: 0.75; margin-top: 2px; }}
    .modal-close {{
      margin-left: auto; background: rgba(255,255,255,0.15);
      border: none; color: #fff; width: 34px; height: 34px;
      border-radius: 50%; font-size: 1.1rem; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: background 0.2s; flex-shrink: 0;
    }}
    .modal-close:hover {{ background: rgba(201,168,76,0.5); }}
    .modal-body {{ padding: 24px 28px; }}
    .modal-section {{ margin-bottom: 22px; }}
    .modal-section-title {{
      font-size: 0.78rem; font-weight: 700; color: var(--gold);
      text-transform: uppercase; letter-spacing: 1px;
      margin-bottom: 12px; padding-bottom: 6px;
      border-bottom: 2px solid var(--gold-light);
    }}
    .modal-grid {{
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    .modal-field label {{
      font-size: 0.72rem; font-weight: 600; color: var(--gray3);
      text-transform: uppercase; letter-spacing: 0.5px;
      display: block; margin-bottom: 3px;
    }}
    .modal-field p {{ font-size: 0.88rem; color: var(--text); }}
    .modal-field.full {{ grid-column: 1 / -1; }}
    .modal-text-block {{
      background: var(--gray); border-radius: 8px;
      padding: 12px 14px; font-size: 0.85rem;
      line-height: 1.6; color: var(--text);
      white-space: pre-wrap; word-break: break-word;
    }}
    .modal-files {{
      display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;
    }}
    .modal-file-btn {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 7px 12px; background: #e8edf5;
      border-radius: 8px; text-decoration: none;
      color: var(--navy); font-size: 0.82rem; font-weight: 500;
      transition: all 0.2s; border: 1.5px solid transparent;
    }}
    .modal-file-btn:hover {{
      background: var(--gold-light); color: #7a5c00;
      border-color: var(--gold);
    }}
    .modal-footer {{
      padding: 16px 28px; border-top: 1px solid var(--gray2);
      display: flex; justify-content: flex-end; gap: 10px;
      position: sticky; bottom: 0; background: var(--white);
      border-radius: 0 0 18px 18px;
    }}

    /* ===== EXPORT MODAL ===== */
    .export-modal-overlay {{
      position: fixed; inset: 0; z-index: 600;
      background: rgba(10,35,66,0.55);
      display: none; align-items: center; justify-content: center;
      padding: 20px;
    }}
    .export-modal-overlay.open {{ display: flex; }}
    .export-modal {{
      background: var(--white); border-radius: 16px;
      padding: 28px 32px; width: 100%; max-width: 480px;
      box-shadow: var(--shadow2);
    }}
    .export-modal h3 {{ font-size: 1.1rem; color: var(--navy); margin-bottom: 8px; }}
    .export-modal p {{ font-size: 0.88rem; color: var(--gray3); margin-bottom: 20px; }}
    .export-options {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
    .export-option {{
      border: 2px solid var(--border); border-radius: 10px;
      padding: 14px; cursor: pointer; transition: all 0.2s;
    }}
    .export-option:hover {{ border-color: var(--navy); }}
    .export-option.selected {{ border-color: var(--gold); background: var(--gold-light); }}
    .export-option-title {{ font-size: 0.88rem; font-weight: 600; color: var(--navy); }}
    .export-option-desc {{ font-size: 0.78rem; color: var(--gray3); margin-top: 3px; }}
    .export-footer {{ display: flex; justify-content: flex-end; gap: 10px; }}

    /* ===== TOAST ===== */
    .toast {{
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      background: var(--navy); color: #fff;
      padding: 12px 20px; border-radius: 10px;
      font-size: 0.88rem; font-weight: 500;
      box-shadow: var(--shadow2);
      transform: translateY(80px); opacity: 0;
      transition: all 0.3s; pointer-events: none;
    }}
    .toast.show {{ transform: translateY(0); opacity: 1; }}
    .toast.success {{ background: #2e7d32; }}
    .toast.info {{ background: var(--navy2); }}

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {{
      .header-inner {{ padding: 12px 16px; flex-wrap: wrap; }}
      .header-stats {{ gap: 16px; }}
      .main-content {{ padding: 16px; }}
      .filter-bar {{ padding: 14px 16px; }}
      .modal-grid {{ grid-template-columns: 1fr; }}
      .charts-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<!-- ===== LOGIN SCREEN ===== -->
<div id="login-screen">
  <div class="login-box">
    <div class="login-logo">🏅</div>
    <h1>Elite Athlete Sponsorship</h1>
    <p>Bermuda Department of Youth, Sport &amp; Recreation<br>2025 Applications Dashboard</p>
    <input class="login-input" id="access-code-input" type="password"
      placeholder="Enter Access Code"
      onkeydown="if(event.key==='Enter')attemptLogin()"
      autocomplete="off" />
    <button class="login-btn" id="login-btn" onclick="attemptLogin()">Sign In</button>
    <div class="login-error" id="login-error"></div>
  </div>
</div>

<!-- ===== APP SHELL ===== -->
<div id="app-shell">

<header class="site-header">
  <div class="header-inner">
    <div class="header-logo">🏅</div>
    <div class="header-text">
      <h1>Elite Athlete Sponsorship Applications</h1>
      <p>Bermuda Department of Youth, Sport &amp; Recreation — 2025</p>
    </div>
    <div class="header-stats">
      <div class="hstat">
        <div class="hstat-num">46</div>
        <div class="hstat-label">Applicants</div>
      </div>
      <div class="hstat">
        <div class="hstat-num" id="stat-shortlisted">0</div>
        <div class="hstat-label">Shortlisted</div>
      </div>
      <div class="hstat">
        <div class="hstat-num">46</div>
        <div class="hstat-label">With Docs</div>
      </div>
      <div class="hstat">
        <div class="hstat-num">{total_str}</div>
        <div class="hstat-label">Total Requested</div>
      </div>
    </div>
  </div>
  <nav class="nav-tabs">
    <div class="nav-tabs-inner">
      <button class="nav-tab active" onclick="switchView('applications', event)">Applications</button>
      <button class="nav-tab" onclick="switchView('shortlist', event)">Shortlist</button>
      <button class="nav-tab" onclick="switchView('charts', event)">Analytics</button>
      <button class="signout-btn" onclick="signOut()">Sign Out</button>
    </div>
  </nav>
</header>

<main class="main-content">

  <!-- APPLICATIONS VIEW -->
  <div class="view active" id="view-applications">
    <div class="filter-bar">
      <div class="filter-group search">
        <label>Search</label>
        <input id="search-input" type="text" placeholder="Name, sport, NSGB, email…" oninput="applyFilters()" />
      </div>
      <div class="filter-group">
        <label>Sport</label>
        <select id="filter-sport" onchange="applyFilters()">
          <option value="">All Sports</option>
          {sport_options}
        </select>
      </div>
      <div class="filter-group">
        <label>Has Documents</label>
        <select id="filter-docs" onchange="applyFilters()">
          <option value="">All</option>
          <option value="yes">Has Documents</option>
          <option value="no">No Documents</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Status</label>
        <select id="filter-status" onchange="applyFilters()">
          <option value="">All Statuses</option>
          <option value="Pending">Pending</option>
          <option value="Under Review">Under Review</option>
          <option value="Approved">Approved</option>
          <option value="Declined">Declined</option>
        </select>
      </div>
      <div class="filter-actions">
        <button class="btn btn-secondary" onclick="clearFilters()">Clear</button>
        <button class="btn btn-primary" onclick="openExportModal()">Export</button>
      </div>
    </div>

    <div class="table-wrap">
      <div class="table-meta">
        <div class="table-meta-left">Showing <strong id="results-showing">46</strong> of 46 applicants</div>
        <div class="table-meta-right">
          <span class="shortlist-count-badge" id="shortlist-count-badge">0 shortlisted</span>
          <button class="btn-select-all" onclick="selectAllFiltered()">Select All Filtered</button>
        </div>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th style="width:36px;"><input type="checkbox" id="select-all-cb" onchange="toggleSelectAll(this)" /></th>
              <th onclick="sortTable('id')">#</th>
              <th onclick="sortTable('fullName')">ATHLETE ↕</th>
              <th onclick="sortTable('sport')">SPORT ↕</th>
              <th>NSGB</th>
              <th onclick="sortTable('totalAmountNum')">AMOUNT ↕</th>
              <th>PERIOD</th>
              <th>DOCUMENTS</th>
              <th>STATUS</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody id="table-body"></tbody>
        </table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>

  <!-- SHORTLIST VIEW -->
  <div class="view" id="view-shortlist">
    <div class="shortlist-header">
      <h2>Shortlist (<span id="shortlist-total">0</span> applicants)</h2>
      <div class="shortlist-export-bar">
        <button class="btn btn-primary" onclick="exportShortlist('csv')">Export CSV</button>
        <button class="btn btn-secondary" onclick="exportShortlist('print')">Print</button>
        <button class="btn btn-secondary" onclick="clearShortlist()">Clear All</button>
      </div>
    </div>
    <div id="shortlist-content"></div>
  </div>

  <!-- ANALYTICS VIEW -->
  <div class="view" id="view-charts">
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Applications by Sport</h3>
        <div class="chart-wrap"><canvas id="chart-sports"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Amount Requested by Sport</h3>
        <div class="chart-wrap"><canvas id="chart-amounts"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Applications by NSGB</h3>
        <div class="chart-wrap"><canvas id="chart-nsgb"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>BOA Elite Athlete Category</h3>
        <div class="chart-wrap"><canvas id="chart-boa"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Amount Distribution</h3>
        <div class="chart-wrap"><canvas id="chart-dist"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Application Status Overview</h3>
        <div class="chart-wrap"><canvas id="chart-status"></canvas></div>
      </div>
    </div>
  </div>

</main>

<!-- APPLICANT MODAL -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModalOnOverlay(event)">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-avatar" id="modal-avatar">?</div>
      <div class="modal-header-text">
        <h2 id="modal-name"></h2>
        <p id="modal-subtitle"></p>
      </div>
      <button class="modal-close" onclick="closeModal()">&#x2715;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Close</button>
      <button class="btn btn-primary" id="modal-shortlist-btn" onclick="toggleShortlistFromModal()">Add to Shortlist</button>
    </div>
  </div>
</div>

<!-- EXPORT MODAL -->
<div class="export-modal-overlay" id="export-modal-overlay" onclick="closeExportModalOnOverlay(event)">
  <div class="export-modal">
    <h3>Export Applications</h3>
    <p>Exporting <strong id="export-count">46</strong> filtered applicants</p>
    <div class="export-options">
      <div class="export-option selected" id="exp-csv" onclick="selectExport('csv')">
        <div class="export-option-title">CSV Spreadsheet</div>
        <div class="export-option-desc">Open in Excel or Google Sheets</div>
      </div>
      <div class="export-option" id="exp-print" onclick="selectExport('print')">
        <div class="export-option-title">Print / PDF</div>
        <div class="export-option-desc">Print-ready formatted report</div>
      </div>
      <div class="export-option" id="exp-json" onclick="selectExport('json')">
        <div class="export-option-title">JSON Data</div>
        <div class="export-option-desc">Raw structured data file</div>
      </div>
      <div class="export-option" id="exp-shortlist" onclick="selectExport('shortlist')">
        <div class="export-option-title">Shortlist Only</div>
        <div class="export-option-desc">Export shortlisted applicants</div>
      </div>
    </div>
    <div class="export-footer">
      <button class="btn btn-secondary" onclick="closeExportModal()">Cancel</button>
      <button class="btn btn-primary" onclick="doExport()">Export</button>
    </div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ============================================================
// DATA
// ============================================================
const APPLICANTS = {applicants_json};

// ============================================================
// STATE
// ============================================================
let filtered = [...APPLICANTS];
let shortlisted = new Set();
let appStatuses = {{}};
let currentPage = 1;
const PAGE_SIZE = 20;
let sortCol = 'id';
let sortDir = 1;
let currentModalId = null;
let exportFormat = 'csv';
let chartsInitialized = false;

// ============================================================
// NAVIGATION
// ============================================================
function switchView(name, e) {{
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');
  if (e && e.target) e.target.classList.add('active');
  if (name === 'charts' && !chartsInitialized) {{ initCharts(); chartsInitialized = true; }}
  if (name === 'shortlist') renderShortlist();
}}

// ============================================================
// FILTER & SORT
// ============================================================
function applyFilters() {{
  const q = document.getElementById('search-input').value.toLowerCase().trim();
  const sport = document.getElementById('filter-sport').value.toLowerCase();
  const docs = document.getElementById('filter-docs').value;
  const status = document.getElementById('filter-status').value;

  filtered = APPLICANTS.filter(a => {{
    if (q) {{
      const hay = [a.fullName, a.sport, a.nsgb, a.email, a.boaCategory, a.performanceLevel].join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    if (sport && a.sport.toLowerCase() !== sport) return false;
    if (docs === 'yes' && a.uploadedFiles.length === 0) return false;
    if (docs === 'no' && a.uploadedFiles.length > 0) return false;
    if (status) {{
      const st = appStatuses[a.id] || 'Pending';
      if (st !== status) return false;
    }}
    return true;
  }});

  sortData();
  currentPage = 1;
  renderTable();
  document.getElementById('results-showing').textContent = filtered.length;
}}

function sortTable(col) {{
  if (sortCol === col) sortDir *= -1;
  else {{ sortCol = col; sortDir = 1; }}
  sortData();
  renderTable();
}}

function sortData() {{
  filtered.sort((a, b) => {{
    let av = a[sortCol], bv = b[sortCol];
    if (typeof av === 'number') return (av - bv) * sortDir;
    return String(av||'').localeCompare(String(bv||'')) * sortDir;
  }});
}}

function clearFilters() {{
  document.getElementById('search-input').value = '';
  document.getElementById('filter-sport').value = '';
  document.getElementById('filter-docs').value = '';
  document.getElementById('filter-status').value = '';
  applyFilters();
}}

// ============================================================
// TABLE RENDER
// ============================================================
function renderTable() {{
  const tbody = document.getElementById('table-body');
  const start = (currentPage - 1) * PAGE_SIZE;
  const page = filtered.slice(start, start + PAGE_SIZE);

  tbody.innerHTML = page.map(a => renderRow(a)).join('');
  renderPagination();
}}

function renderRow(a) {{
  const isShortlisted = shortlisted.has(a.id);
  const status = appStatuses[a.id] || 'Pending';
  const statusClass = 'status-' + status.toLowerCase().replace(' ', '-');

  const filesHtml = a.uploadedFiles.slice(0, 3).map((f, i) =>
    `<a class="file-link" href="${{a.uploadedFilePaths[i]}}" target="_blank" title="${{escHtml(f)}}">${{shortFileName(f)}}</a>`
  ).join('') + (a.uploadedFiles.length > 3 ? `<span class="badge badge-gray">+${{a.uploadedFiles.length - 3}}</span>` : '');

  const sportBadge = sportBadgeClass(a.sport);
  const period = a.startPeriod && a.endPeriod ? `${{a.startPeriod}} – ${{a.endPeriod}}` : (a.startPeriod || a.endPeriod || '—');

  return `<tr class="${{isShortlisted ? 'shortlisted' : ''}}">
    <td><input type="checkbox" ${{isShortlisted ? 'checked' : ''}} onchange="toggleShortlist(${{a.id}}, this.checked)" /></td>
    <td class="td-date">${{a.id}}</td>
    <td>
      <div class="td-name">${{escHtml(a.fullName)}}</div>
      <div class="td-date">${{escHtml(a.email)}}</div>
    </td>
    <td><span class="badge ${{sportBadge}}">${{escHtml(a.sport)}}</span></td>
    <td style="font-size:0.82rem; max-width:160px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${{escHtml(a.nsgb)}}">${{escHtml(a.nsgb) || '—'}}</td>
    <td class="td-amount">${{escHtml(a.totalAmount) || '—'}}</td>
    <td style="font-size:0.80rem; color:var(--gray3); white-space:nowrap;">${{escHtml(period)}}</td>
    <td><div class="files-cell">${{filesHtml || '<span style="color:var(--gray3);font-size:0.80rem;">—</span>'}}</div></td>
    <td>
      <select class="status-select ${{statusClass}}" data-id="${{a.id}}" onchange="setStatus(${{a.id}}, this)">
        <option ${{status==='Pending'?'selected':''}}>Pending</option>
        <option ${{status==='Under Review'?'selected':''}}>Under Review</option>
        <option ${{status==='Approved'?'selected':''}}>Approved</option>
        <option ${{status==='Declined'?'selected':''}}>Declined</option>
      </select>
    </td>
    <td>
      <div class="action-btns">
        <button class="btn-view" onclick="openModal(${{a.id}})">View</button>
        <button class="btn-shortlist ${{isShortlisted ? 'active' : ''}}" onclick="toggleShortlist(${{a.id}}, ${{!isShortlisted}})">
          ${{isShortlisted ? '★' : '☆'}}
        </button>
      </div>
    </td>
  </tr>`;
}}

function renderPagination() {{
  const total = Math.ceil(filtered.length / PAGE_SIZE);
  const pag = document.getElementById('pagination');
  if (total <= 1) {{ pag.innerHTML = ''; return; }}
  let html = `<button class="page-btn" onclick="goPage(${{currentPage-1}})" ${{currentPage===1?'disabled':''}}>&#8249;</button>`;
  for (let i = 1; i <= total; i++) {{
    if (i === 1 || i === total || Math.abs(i - currentPage) <= 2) {{
      html += `<button class="page-btn ${{i===currentPage?'active':''}}" onclick="goPage(${{i}})">${{i}}</button>`;
    }} else if (Math.abs(i - currentPage) === 3) {{
      html += `<span style="padding:6px 4px;color:var(--gray3)">…</span>`;
    }}
  }}
  html += `<button class="page-btn" onclick="goPage(${{currentPage+1}})" ${{currentPage===total?'disabled':''}}>&#8250;</button>`;
  pag.innerHTML = html;
}}

function goPage(p) {{
  const total = Math.ceil(filtered.length / PAGE_SIZE);
  if (p < 1 || p > total) return;
  currentPage = p;
  renderTable();
  document.querySelector('.table-wrap').scrollIntoView({{behavior:'smooth', block:'start'}});
}}

// ============================================================
// SHORTLIST
// ============================================================
function toggleShortlist(id, add) {{
  if (add) shortlisted.add(id);
  else shortlisted.delete(id);
  saveShortlist();
  dbToggleShortlist(id, add);
  updateStats();
  renderTable();
  const badge = document.getElementById('shortlist-count-badge');
  badge.textContent = shortlisted.size + ' shortlisted';
}}

function toggleShortlistFromModal() {{
  if (!currentModalId) return;
  const isIn = shortlisted.has(currentModalId);
  toggleShortlist(currentModalId, !isIn);
  document.getElementById('modal-shortlist-btn').textContent = isIn ? 'Add to Shortlist' : 'Remove from Shortlist';
}}

function selectAllFiltered() {{
  filtered.forEach(a => shortlisted.add(a.id));
  saveShortlist();
  updateStats();
  renderTable();
  document.getElementById('shortlist-count-badge').textContent = shortlisted.size + ' shortlisted';
  showToast('Added ' + filtered.length + ' applicants to shortlist', 'success');
}}

function toggleSelectAll(cb) {{
  const page = filtered.slice((currentPage-1)*PAGE_SIZE, currentPage*PAGE_SIZE);
  page.forEach(a => {{ if (cb.checked) shortlisted.add(a.id); else shortlisted.delete(a.id); }});
  saveShortlist();
  updateStats();
  renderTable();
  document.getElementById('shortlist-count-badge').textContent = shortlisted.size + ' shortlisted';
}}

function clearShortlist() {{
  shortlisted = new Set();
  saveShortlist();
  dbClearShortlist();
  updateStats();
  renderTable();
  renderShortlist();
  document.getElementById('shortlist-count-badge').textContent = '0 shortlisted';
  showToast('Shortlist cleared', 'info');
}}

function saveShortlist() {{
  try {{ sessionStorage.setItem('eas_shortlist', JSON.stringify([...shortlisted])); }} catch(e) {{}}
}}
function loadShortlist() {{
  try {{
    const s = sessionStorage.getItem('eas_shortlist');
    if (s) shortlisted = new Set(JSON.parse(s));
  }} catch(e) {{ shortlisted = new Set(); }}
}}

function renderShortlist() {{
  const items = APPLICANTS.filter(a => shortlisted.has(a.id));
  document.getElementById('shortlist-total').textContent = items.length;
  const el = document.getElementById('shortlist-content');
  if (!items.length) {{
    el.innerHTML = '<div class="shortlist-empty">No applicants shortlisted yet.<br>Use the ☆ button in the Applications tab to add athletes.</div>';
    return;
  }}
  el.innerHTML = `<div class="table-wrap"><div class="table-scroll"><table>
    <thead><tr>
      <th>#</th><th>ATHLETE</th><th>SPORT</th><th>NSGB</th><th>AMOUNT</th><th>PERIOD</th><th>STATUS</th><th>ACTIONS</th>
    </tr></thead>
    <tbody>
      ${{items.map(a => {{
        const status = appStatuses[a.id] || 'Pending';
        const statusClass = 'status-' + status.toLowerCase().replace(' ', '-');
        const period = a.startPeriod && a.endPeriod ? `${{a.startPeriod}} – ${{a.endPeriod}}` : (a.startPeriod || a.endPeriod || '—');
        return `<tr>
          <td class="td-date">${{a.id}}</td>
          <td><div class="td-name">${{escHtml(a.fullName)}}</div><div class="td-date">${{escHtml(a.email)}}</div></td>
          <td><span class="badge ${{sportBadgeClass(a.sport)}}">${{escHtml(a.sport)}}</span></td>
          <td style="font-size:0.82rem;">${{escHtml(a.nsgb)||'—'}}</td>
          <td class="td-amount">${{escHtml(a.totalAmount)||'—'}}</td>
          <td style="font-size:0.80rem;color:var(--gray3);">${{escHtml(period)}}</td>
          <td><select class="status-select ${{statusClass}}" data-id="${{a.id}}" onchange="setStatus(${{a.id}}, this)">
            <option ${{status==='Pending'?'selected':''}}>Pending</option>
            <option ${{status==='Under Review'?'selected':''}}>Under Review</option>
            <option ${{status==='Approved'?'selected':''}}>Approved</option>
            <option ${{status==='Declined'?'selected':''}}>Declined</option>
          </select></td>
          <td><div class="action-btns">
            <button class="btn-view" onclick="openModal(${{a.id}})">View</button>
            <button class="btn-shortlist active" onclick="toggleShortlist(${{a.id}}, false); renderShortlist();">Remove</button>
          </div></td>
        </tr>`;
      }}).join('')}}
    </tbody>
  </table></div></div>`;
}}

// ============================================================
// STATUS
// ============================================================
function setStatus(id, sel) {{
  const val = sel.value;
  appStatuses[id] = val;
  const cls = 'status-' + val.toLowerCase().replace(' ', '-');
  sel.className = 'status-select ' + cls;
  saveStatuses();
  dbSaveStatus(id, val);
  showToast('Status updated: ' + val, 'success');
}}
function saveStatuses() {{
  try {{ sessionStorage.setItem('eas_statuses', JSON.stringify(appStatuses)); }} catch(e) {{}}
}}
function loadStatuses() {{
  try {{
    const s = sessionStorage.getItem('eas_statuses');
    if (s) appStatuses = JSON.parse(s);
  }} catch(e) {{ appStatuses = {{}}; }}
}}

// ============================================================
// MODAL
// ============================================================
function openModal(id) {{
  const a = APPLICANTS.find(x => x.id === id);
  if (!a) return;
  currentModalId = id;
  const initials = (a.firstName[0]||'') + (a.lastName[0]||'');
  document.getElementById('modal-avatar').textContent = initials.toUpperCase() || '?';
  document.getElementById('modal-name').textContent = a.fullName;
  document.getElementById('modal-subtitle').textContent = a.sport + (a.nsgb ? ' · ' + a.nsgb : '');
  const isShortlisted = shortlisted.has(id);
  document.getElementById('modal-shortlist-btn').textContent = isShortlisted ? 'Remove from Shortlist' : 'Add to Shortlist';

  const filesHtml = a.uploadedFiles.length
    ? a.uploadedFiles.map((f, i) =>
        `<a class="modal-file-btn" href="${{a.uploadedFilePaths[i]}}" target="_blank">
          📄 ${{escHtml(f)}}
        </a>`).join('')
    : '<span style="color:var(--gray3);font-size:0.88rem;">No documents uploaded</span>';

  const status = appStatuses[a.id] || 'Pending';
  const statusClass = 'status-' + status.toLowerCase().replace(' ', '-');

  document.getElementById('modal-body').innerHTML = `
    <div class="modal-section">
      <div class="modal-section-title">Athlete Information</div>
      <div class="modal-grid">
        <div class="modal-field"><label>Full Name</label><p>${{escHtml(a.fullName)}}</p></div>
        <div class="modal-field"><label>Age</label><p>${{escHtml(a.age) || '—'}}</p></div>
        <div class="modal-field"><label>Email</label><p>${{escHtml(a.email) || '—'}}</p></div>
        <div class="modal-field"><label>Phone</label><p>${{escHtml(a.phone) || '—'}}</p></div>
        <div class="modal-field"><label>Sport</label><p><span class="badge ${{sportBadgeClass(a.sport)}}">${{escHtml(a.sport)}}</span></p></div>
        <div class="modal-field"><label>NSGB Affiliation</label><p>${{escHtml(a.nsgb) || '—'}}</p></div>
        <div class="modal-field"><label>BOA Category</label><p>${{escHtml(a.boaCategory) || '—'}}</p></div>
        <div class="modal-field"><label>Performance Level</label><p>${{escHtml(a.performanceLevel) || '—'}}</p></div>
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Sponsorship Request</div>
      <div class="modal-grid">
        <div class="modal-field"><label>Total Amount Requested</label><p class="td-amount">${{escHtml(a.totalAmount) || '—'}}</p></div>
        <div class="modal-field"><label>Requested Amount (Alt)</label><p>${{escHtml(a.requestedAmount) || '—'}}</p></div>
        <div class="modal-field"><label>Start Period</label><p>${{escHtml(a.startPeriod) || '—'}}</p></div>
        <div class="modal-field"><label>End Period</label><p>${{escHtml(a.endPeriod) || '—'}}</p></div>
        <div class="modal-field"><label>Application Status</label>
          <select class="status-select ${{statusClass}}" onchange="setStatus(${{a.id}}, this)">
            <option ${{status==='Pending'?'selected':''}}>Pending</option>
            <option ${{status==='Under Review'?'selected':''}}>Under Review</option>
            <option ${{status==='Approved'?'selected':''}}>Approved</option>
            <option ${{status==='Declined'?'selected':''}}>Declined</option>
          </select>
        </div>
        <div class="modal-field"><label>Submission Date</label><p>${{escHtml(a.submissionDate) || '—'}}</p></div>
      </div>
    </div>

    ${{a.accomplishments ? `<div class="modal-section">
      <div class="modal-section-title">Accomplishments (Last 5 Years)</div>
      <div class="modal-text-block">${{escHtml(a.accomplishments)}}</div>
    </div>` : ''}}

    ${{a.goals ? `<div class="modal-section">
      <div class="modal-section-title">Goals for Next 2 Years</div>
      <div class="modal-text-block">${{escHtml(a.goals)}}</div>
    </div>` : ''}}

    ${{a.purpose ? `<div class="modal-section">
      <div class="modal-section-title">Intended Purpose of Sponsorship</div>
      <div class="modal-text-block">${{escHtml(a.purpose)}}</div>
    </div>` : ''}}

    ${{a.budgetDetails ? `<div class="modal-section">
      <div class="modal-section-title">Budget Details</div>
      <div class="modal-text-block">${{escHtml(a.budgetDetails)}}</div>
    </div>` : ''}}

    <div class="modal-section">
      <div class="modal-section-title">Uploaded Documents (${{a.uploadedFiles.length}} file${{a.uploadedFiles.length !== 1 ? 's' : ''}})</div>
      <div class="modal-files">${{filesHtml}}</div>
    </div>

    ${{a.submitterName ? `<div class="modal-section">
      <div class="modal-section-title">Submitted By</div>
      <div class="modal-grid">
        <div class="modal-field"><label>Name</label><p>${{escHtml(a.submitterName)}}</p></div>
        <div class="modal-field"><label>Position</label><p>${{escHtml(a.submitterPosition) || '—'}}</p></div>
      </div>
    </div>` : ''}}
  `;

  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
  currentModalId = null;
}}
function closeModalOnOverlay(e) {{
  if (e.target === document.getElementById('modal-overlay')) closeModal();
}}

// ============================================================
// EXPORT
// ============================================================
function openExportModal() {{
  document.getElementById('export-count').textContent = filtered.length;
  document.getElementById('export-modal-overlay').classList.add('open');
}}
function closeExportModal() {{ document.getElementById('export-modal-overlay').classList.remove('open'); }}
function closeExportModalOnOverlay(e) {{
  if (e.target === document.getElementById('export-modal-overlay')) closeExportModal();
}}
function selectExport(fmt) {{
  exportFormat = fmt;
  document.querySelectorAll('.export-option').forEach(el => el.classList.remove('selected'));
  document.getElementById('exp-' + fmt).classList.add('selected');
}}
function doExport() {{
  closeExportModal();
  if (exportFormat === 'csv') exportCSV(filtered);
  else if (exportFormat === 'json') exportJSON(filtered);
  else if (exportFormat === 'print') exportPrint(filtered);
  else if (exportFormat === 'shortlist') exportCSV(APPLICANTS.filter(a => shortlisted.has(a.id)));
}}
function exportShortlist(fmt) {{
  const items = APPLICANTS.filter(a => shortlisted.has(a.id));
  if (!items.length) {{ showToast('No applicants in shortlist', 'info'); return; }}
  if (fmt === 'csv') exportCSV(items); else exportPrint(items);
}}
function exportCSV(data) {{
  const headers = ['ID','Full Name','Email','Phone','Age','Sport','NSGB','BOA Category',
    'Performance Level','Total Amount','Start Period','End Period','Status',
    'Submission Date','Submitter Name','Submitter Position','Document Count','Document Paths'];
  const rows = data.map(a => [
    a.id, a.fullName, a.email, a.phone, a.age, a.sport, a.nsgb, a.boaCategory,
    a.performanceLevel, a.totalAmount, a.startPeriod, a.endPeriod,
    appStatuses[a.id]||'Pending', a.submissionDate, a.submitterName, a.submitterPosition,
    a.uploadedFiles.length, a.uploadedFilePaths.join('; ')
  ].map(v => '"' + String(v||'').replace(/"/g,'""') + '"'));
  const csv = [headers.map(h=>'"'+h+'"').join(','), ...rows.map(r=>r.join(','))].join('\\n');
  const blob = new Blob([csv], {{type:'text/csv;charset=utf-8;'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'elite_athlete_sponsorship_2025.csv'; a.click();
  URL.revokeObjectURL(url);
  showToast('CSV exported — ' + data.length + ' applicants', 'success');
}}
function exportJSON(data) {{
  const blob = new Blob([JSON.stringify(data, null, 2)], {{type:'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'elite_athlete_sponsorship_2025.json'; a.click();
  URL.revokeObjectURL(url);
  showToast('JSON exported', 'success');
}}
function exportPrint(data) {{
  const win = window.open('', '_blank');
  const rows = data.map(a => `<tr>
    <td>${{a.id}}</td>
    <td><strong>${{escHtml(a.fullName)}}</strong><br><small>${{escHtml(a.email)}}</small></td>
    <td>${{escHtml(a.sport)}}</td>
    <td>${{escHtml(a.nsgb)||'—'}}</td>
    <td><strong>${{escHtml(a.totalAmount)||'—'}}</strong></td>
    <td>${{escHtml(a.startPeriod)||'—'}} – ${{escHtml(a.endPeriod)||'—'}}</td>
    <td>${{appStatuses[a.id]||'Pending'}}</td>
    <td>${{a.uploadedFiles.length}} file(s)</td>
  </tr>`).join('');
  win.document.write(`<!DOCTYPE html><html><head><title>Elite Athlete Sponsorship 2025</title>
  <style>body{{font-family:Arial,sans-serif;font-size:11px;}}
  table{{width:100%;border-collapse:collapse;}}
  th{{background:#0A2342;color:white;padding:8px;text-align:left;}}
  td{{padding:6px 8px;border-bottom:1px solid #eee;}}
  tr:nth-child(even){{background:#f9f9f9;}}
  h1{{color:#0A2342;font-size:16px;}}
  .meta{{color:#666;font-size:10px;margin-bottom:12px;}}
  </style></head><body>
  <h1>Elite Athlete Sponsorship Applications 2025</h1>
  <p class="meta">Bermuda Department of Youth, Sport &amp; Recreation | Exported: ${{new Date().toLocaleDateString()}} | Total: ${{data.length}} applicants</p>
  <table><thead><tr><th>#</th><th>Athlete</th><th>Sport</th><th>NSGB</th><th>Amount</th><th>Period</th><th>Status</th><th>Documents</th></tr></thead>
  <tbody>${{rows}}</tbody></table></body></html>`);
  win.document.close(); win.print();
}}

// ============================================================
// CHARTS
// ============================================================
function initCharts() {{
  const navy='#0A2342', gold='#C9A84C', navy2='#123363', gold2='#E8C96A';
  const colors=['#0A2342','#C9A84C','#123363','#E8C96A','#1565C0','#7a5c00','#283593','#C62828','#00695C','#4527A0','#558B2F','#F57F17','#AD1457','#0277BD','#2E7D32'];

  // Sports
  const sportCounts={{}};
  APPLICANTS.forEach(a=>{{ const s=a.sport||'Unknown'; sportCounts[s]=(sportCounts[s]||0)+1; }});
  const sportLabels=Object.keys(sportCounts).sort((a,b)=>sportCounts[b]-sportCounts[a]);
  new Chart(document.getElementById('chart-sports'),{{
    type:'bar',
    data:{{labels:sportLabels,datasets:[{{label:'Applicants',data:sportLabels.map(k=>sportCounts[k]),
      backgroundColor:sportLabels.map((_,i)=>colors[i%colors.length]),borderRadius:6}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},
      scales:{{x:{{ticks:{{maxRotation:40,font:{{size:9}}}}}},y:{{beginAtZero:true}}}}}}
  }});

  // Amounts by sport
  const amountBySport={{}};
  APPLICANTS.forEach(a=>{{ const s=a.sport||'Unknown'; amountBySport[s]=(amountBySport[s]||0)+a.totalAmountNum; }});
  const amtLabels=Object.keys(amountBySport).sort((a,b)=>amountBySport[b]-amountBySport[a]).slice(0,12);
  new Chart(document.getElementById('chart-amounts'),{{
    type:'bar',
    data:{{labels:amtLabels,datasets:[{{label:'Amount ($)',data:amtLabels.map(k=>amountBySport[k]),
      backgroundColor:amtLabels.map((_,i)=>colors[i%colors.length]),borderRadius:6}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},
      scales:{{x:{{ticks:{{maxRotation:40,font:{{size:9}}}}}},y:{{beginAtZero:true,ticks:{{callback:v=>'$'+v.toLocaleString()}}}}}}}}
  }});

  // NSGB
  const nsgbCounts={{}};
  APPLICANTS.forEach(a=>{{ const n=a.nsgb||'Unknown'; nsgbCounts[n]=(nsgbCounts[n]||0)+1; }});
  const nsgbLabels=Object.keys(nsgbCounts).sort((a,b)=>nsgbCounts[b]-nsgbCounts[a]).slice(0,12);
  new Chart(document.getElementById('chart-nsgb'),{{
    type:'doughnut',
    data:{{labels:nsgbLabels,datasets:[{{data:nsgbLabels.map(k=>nsgbCounts[k]),
      backgroundColor:colors,borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'right',labels:{{font:{{size:9}},boxWidth:10}}}}}}}}
  }});

  // BOA Category
  const boaCounts={{}};
  APPLICANTS.forEach(a=>{{ const b=a.boaCategory||'Not Specified'; boaCounts[b]=(boaCounts[b]||0)+1; }});
  const boaLabels=Object.keys(boaCounts).sort((a,b)=>boaCounts[b]-boaCounts[a]);
  new Chart(document.getElementById('chart-boa'),{{
    type:'pie',
    data:{{labels:boaLabels,datasets:[{{data:boaLabels.map(k=>boaCounts[k]),
      backgroundColor:colors,borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom',labels:{{font:{{size:10}},boxWidth:12}}}}}}}}
  }});

  // Amount distribution
  const brackets={{'< $5k':0,'$5k–$10k':0,'$10k–$20k':0,'$20k–$30k':0,'$30k–$50k':0,'> $50k':0}};
  APPLICANTS.forEach(a=>{{
    const v=a.totalAmountNum;
    if(v<5000)brackets['< $5k']++;
    else if(v<10000)brackets['$5k–$10k']++;
    else if(v<20000)brackets['$10k–$20k']++;
    else if(v<30000)brackets['$20k–$30k']++;
    else if(v<50000)brackets['$30k–$50k']++;
    else brackets['> $50k']++;
  }});
  new Chart(document.getElementById('chart-dist'),{{
    type:'bar',
    data:{{labels:Object.keys(brackets),datasets:[{{label:'Applicants',data:Object.values(brackets),
      backgroundColor:colors,borderRadius:6}}]}},
    options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},
      scales:{{x:{{ticks:{{font:{{size:10}}}}}},y:{{beginAtZero:true}}}}}}
  }});

  // Status
  const statusCounts={{'Pending':0,'Under Review':0,'Approved':0,'Declined':0}};
  APPLICANTS.forEach(a=>{{ const s=appStatuses[a.id]||'Pending'; statusCounts[s]=(statusCounts[s]||0)+1; }});
  new Chart(document.getElementById('chart-status'),{{
    type:'doughnut',
    data:{{labels:Object.keys(statusCounts),datasets:[{{data:Object.values(statusCounts),
      backgroundColor:[navy,'#1565c0','#2e7d32','#c62828'],borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'bottom',labels:{{font:{{size:11}},boxWidth:14}}}}}}}}
  }});
}}

// ============================================================
// HELPERS
// ============================================================
function updateStats() {{
  document.getElementById('stat-shortlisted').textContent = shortlisted.size;
}}
function escHtml(str) {{
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
function shortFileName(f) {{
  if (!f) return '';
  const name = f.replace(/\\.pdf$/i,'').replace(/\\.docx?$/i,'').replace(/\\.xlsx?$/i,'').replace(/\\.jpe?g$/i,'').replace(/\\.png$/i,'');
  return name.length > 18 ? name.slice(0,16)+'…' : name;
}}
function sportBadgeClass(sport) {{
  const s = (sport||'').toLowerCase();
  if (s.includes('cycling') || s.includes('bike')) return 'badge-teal';
  if (s.includes('swim')) return 'badge-blue';
  if (s.includes('golf')) return 'badge-green';
  if (s.includes('tennis')) return 'badge-orange';
  if (s.includes('hockey')) return 'badge-purple';
  if (s.includes('athletics') || s.includes('track') || s.includes('field')) return 'badge-gold';
  if (s.includes('sailing')) return 'badge-navy';
  if (s.includes('rugby')) return 'badge-red';
  if (s.includes('archery')) return 'badge-purple';
  if (s.includes('triathlon')) return 'badge-teal';
  return 'badge-navy';
}}
function showToast(msg, type='info') {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + type + ' show';
  setTimeout(() => t.className = 'toast', 3000);
}}

// ============================================================
// SUPABASE
// ============================================================
const SUPABASE_URL = 'https://iqwbxhzgbhzhrcxrqenw.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlxd2J4aHpnYmh6aHJjeHJxZW53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5NTE5NzMsImV4cCI6MjA5MDUyNzk3M30.BXyXRHYteEz-NoM4sHDP4-MR1CnFix4mYnIaRblZqZQ';
const db = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
let currentUserCode = null;

async function dbLoadUserData(code) {{
  try {{
    const {{ data: slData }} = await db.from('eas_shortlists').select('applicant_id').eq('access_code', code);
    if (slData) shortlisted = new Set(slData.map(r => r.applicant_id));
    const {{ data: stData }} = await db.from('eas_statuses').select('applicant_id, status').eq('access_code', code);
    if (stData) {{ appStatuses = {{}}; stData.forEach(r => {{ appStatuses[r.applicant_id] = r.status; }}); }}
  }} catch(e) {{ console.warn('DB load failed:', e); }}
}}
async function dbToggleShortlist(id, adding) {{
  if (!currentUserCode) return;
  try {{
    if (adding) {{ await db.from('eas_shortlists').upsert({{ access_code: currentUserCode, applicant_id: id }}, {{ onConflict: 'access_code,applicant_id' }}); }}
    else {{ await db.from('eas_shortlists').delete().eq('access_code', currentUserCode).eq('applicant_id', id); }}
  }} catch(e) {{ console.warn('DB shortlist sync failed:', e); }}
}}
async function dbSaveStatus(id, status) {{
  if (!currentUserCode) return;
  try {{
    await db.from('eas_statuses').upsert({{ access_code: currentUserCode, applicant_id: id, status: status }}, {{ onConflict: 'access_code,applicant_id' }});
  }} catch(e) {{ console.warn('DB status sync failed:', e); }}
}}
async function dbClearShortlist() {{
  if (!currentUserCode) return;
  try {{ await db.from('eas_shortlists').delete().eq('access_code', currentUserCode); }}
  catch(e) {{ console.warn('DB clear shortlist failed:', e); }}
}}

// ============================================================
// AUTH
// ============================================================
const ACCESS_CODES = [
  'EAS001','EAS002','EAS003','EAS004','EAS005',
  'ELITE1','ELITE2','ELITE3','ADMIN1','REVIEW1'
];
async function attemptLogin() {{
  const input = document.getElementById('access-code-input');
  const errEl = document.getElementById('login-error');
  const btn   = document.getElementById('login-btn');
  const code  = input.value.trim().toUpperCase();
  if (ACCESS_CODES.includes(code)) {{
    btn.textContent = 'Loading...'; btn.disabled = true;
    currentUserCode = code;
    sessionStorage.setItem('eas_auth','1');
    sessionStorage.setItem('eas_code', code);
    loadShortlist();
    loadStatuses();
    await dbLoadUserData(code);
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-shell').style.display = 'block';
    errEl.textContent = '';
    btn.textContent = 'Sign In'; btn.disabled = false;
    renderTable(); updateStats();
    document.getElementById('shortlist-count-badge').textContent = shortlisted.size + ' shortlisted';
  }} else {{
    errEl.textContent = 'Invalid access code. Please try again.';
    input.classList.add('error');
    input.value = '';
    setTimeout(() => input.classList.remove('error'), 600);
    input.focus();
  }}
}}
function signOut() {{
  sessionStorage.removeItem('eas_auth');
  sessionStorage.removeItem('eas_code');
  currentUserCode = null;
  shortlisted = new Set();
  appStatuses = {{}};
  document.getElementById('app-shell').style.display = 'none';
  document.getElementById('login-screen').style.display = 'flex';
  document.getElementById('access-code-input').value = '';
  document.getElementById('login-error').textContent = '';
}}
(async function() {{
  const code = sessionStorage.getItem('eas_code');
  if (sessionStorage.getItem('eas_auth') === '1' && code) {{
    currentUserCode = code;
    loadShortlist();
    loadStatuses();
    await dbLoadUserData(code);
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-shell').style.display = 'block';
    renderTable(); updateStats();
    document.getElementById('shortlist-count-badge').textContent = shortlisted.size + ' shortlisted';
  }}
}})();
</script>
</div><!-- /app-shell -->
</body>
</html>'''

out_path = '/home/ubuntu/elite-athlete-work/index.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Built {out_path} ({len(html):,} chars)')
