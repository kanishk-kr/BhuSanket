/**
 * Mock data for frontend development before backend connection.
 * Matches the API response schemas exactly.
 */

export const mockCommandCenter = {
  total_projects: 127,
  at_risk_projects: 43,
  critical_clock_threats: 12,
  blocking_parcels_count: 156,
  pending_interventions: 28,
  data_contradictions: 7,
  hero_metrics: {
    land_acquired_pct: 78.4,
    construction_enabling_pct: 64.2,
    critical_parcels_resolved_pct: 71.3,
    avg_risk_score: 0.54,
    statutory_clocks_at_risk: 12,
  },
  top_alerts: [
    {
      id: 'a1', project_id: 'p1', alert_type: 'clock.deadline_risk', title: 'Statutory deadline CRITICAL: Award clock expiring in 34 days',
      description: 'Section 25 clock for NH-48 Jaipur Bypass — probability of completion within deadline: 41%', severity: 'critical',
      priority_index: 96.2, owner_role: 'collector', state: 'open', created_at: '2026-09-28T10:00:00Z',
    },
    {
      id: 'a2', project_id: 'p2', alert_type: 'risk.threshold_crossed', title: 'Rapid deterioration: Pune Industrial Corridor',
      description: 'Risk accelerated +18 pts in 14 days. Now 82%. 10 blocking parcels on critical workfront.', severity: 'high',
      priority_index: 91.5, owner_role: 'collector', state: 'open', created_at: '2026-09-28T08:30:00Z',
    },
    {
      id: 'a3', project_id: 'p3', alert_type: 'court.stay_detected', title: 'Court stay detected: Ahmedabad Ring Road Segment 3',
      description: 'High Court stay on 12 parcels. Clocks paused. Next hearing: 15 Oct 2026.', severity: 'high',
      priority_index: 88.7, owner_role: 'legal_officer', state: 'open', created_at: '2026-09-27T14:20:00Z',
    },
    {
      id: 'a4', project_id: 'p4', alert_type: 'contradiction.raised', title: 'Payment contradiction: ₹2.4Cr disbursed vs ₹1.6Cr in PFMS',
      description: 'High severity cross-source mismatch on compensation records.', severity: 'medium',
      priority_index: 72.3, owner_role: 'data_steward', state: 'open', created_at: '2026-09-27T11:00:00Z',
    },
  ],
  deteriorating_projects: [
    { id: 'p1', name: 'NH-48 Jaipur Bypass Extension', code: 'LA-RJ-JAI-0012', state: 'Rajasthan', district: 'Jaipur', sector: 'highways', status: 'active', current_risk_score: 0.82, risk_momentum: 18.3, risk_momentum_class: 'accelerating', model_confidence: 0.87, data_confidence: 0.72, land_acquired_pct: 94.8, construction_enabling_pct: 71.2, created_at: '2025-03-15T00:00:00Z' },
    { id: 'p2', name: 'Pune Industrial Corridor Phase 2', code: 'LA-MH-PUN-0034', state: 'Maharashtra', district: 'Pune', sector: 'industrial', status: 'delayed', current_risk_score: 0.79, risk_momentum: 12.1, risk_momentum_class: 'rising', model_confidence: 0.82, data_confidence: 0.65, land_acquired_pct: 87.2, construction_enabling_pct: 58.9, created_at: '2024-11-20T00:00:00Z' },
    { id: 'p3', name: 'Ahmedabad Ring Road Phase 3', code: 'LA-GJ-AHM-0021', state: 'Gujarat', district: 'Ahmedabad', sector: 'highways', status: 'active', current_risk_score: 0.74, risk_momentum: 9.8, risk_momentum_class: 'rising', model_confidence: 0.79, data_confidence: 0.81, land_acquired_pct: 91.5, construction_enabling_pct: 74.1, created_at: '2025-01-10T00:00:00Z' },
  ],
};

export const mockProjects = {
  projects: [
    { id: 'p1', name: 'NH-48 Jaipur Bypass Extension', code: 'LA-RJ-JAI-0012', state: 'Rajasthan', district: 'Jaipur', sector: 'highways', status: 'active', current_risk_score: 0.82, risk_momentum: 18.3, risk_momentum_class: 'accelerating', model_confidence: 0.87, data_confidence: 0.72, land_acquired_pct: 94.8, construction_enabling_pct: 71.2, budget: 847.5, total_parcels: 234, created_at: '2025-03-15T00:00:00Z' },
    { id: 'p2', name: 'Pune Industrial Corridor Phase 2', code: 'LA-MH-PUN-0034', state: 'Maharashtra', district: 'Pune', sector: 'industrial', status: 'delayed', current_risk_score: 0.79, risk_momentum: 12.1, risk_momentum_class: 'rising', model_confidence: 0.82, data_confidence: 0.65, land_acquired_pct: 87.2, construction_enabling_pct: 58.9, budget: 1250.0, total_parcels: 412, created_at: '2024-11-20T00:00:00Z' },
    { id: 'p3', name: 'Ahmedabad Ring Road Phase 3', code: 'LA-GJ-AHM-0021', state: 'Gujarat', district: 'Ahmedabad', sector: 'highways', status: 'active', current_risk_score: 0.74, risk_momentum: 9.8, risk_momentum_class: 'rising', model_confidence: 0.79, data_confidence: 0.81, land_acquired_pct: 91.5, construction_enabling_pct: 74.1, budget: 632.0, total_parcels: 178, created_at: '2025-01-10T00:00:00Z' },
    { id: 'p4', name: 'Bhopal-Indore Expressway', code: 'LA-MP-BHO-0007', state: 'Madhya Pradesh', district: 'Bhopal', sector: 'highways', status: 'active', current_risk_score: 0.45, risk_momentum: -2.1, risk_momentum_class: 'stable', model_confidence: 0.91, data_confidence: 0.88, land_acquired_pct: 96.1, construction_enabling_pct: 92.3, budget: 1830.0, total_parcels: 523, created_at: '2024-06-01T00:00:00Z' },
    { id: 'p5', name: 'Chennai Outer Ring Road Extension', code: 'LA-TN-CHE-0045', state: 'Tamil Nadu', district: 'Chennai', sector: 'highways', status: 'active', current_risk_score: 0.61, risk_momentum: 5.7, risk_momentum_class: 'rising', model_confidence: 0.84, data_confidence: 0.76, land_acquired_pct: 89.7, construction_enabling_pct: 68.4, budget: 2100.0, total_parcels: 367, created_at: '2025-02-20T00:00:00Z' },
    { id: 'p6', name: 'Lucknow Metro Extension Corridor', code: 'LA-UP-LUC-0019', state: 'Uttar Pradesh', district: 'Lucknow', sector: 'urban_development', status: 'active', current_risk_score: 0.38, risk_momentum: -4.2, risk_momentum_class: 'stable', model_confidence: 0.89, data_confidence: 0.82, land_acquired_pct: 97.8, construction_enabling_pct: 95.1, budget: 3200.0, total_parcels: 145, created_at: '2024-09-15T00:00:00Z' },
  ],
  total: 127,
  page: 1,
  page_size: 20,
};

export const mockClocks = [
  { id: 'c1', clock_code: 'AWARD', section_reference: '25', description: "Collector's award within 12 months of declaration", start_date: '2026-01-15', deadline: '2027-01-15', days_remaining: 34, deadline_risk: 0.83, alert_state: 'CRITICAL', extension_count: 1, total_paused_days: 45, breached: false, consequence: 'LAPSE' },
  { id: 'c2', clock_code: 'DECLARATION', section_reference: '19(7)', description: 'Declaration within 12 months of preliminary notification', start_date: '2025-11-01', deadline: '2026-11-01', days_remaining: 128, deadline_risk: 0.42, alert_state: 'AMBER', extension_count: 0, total_paused_days: 0, breached: false, consequence: 'RESCISSION' },
  { id: 'c3', clock_code: 'COMPENSATION_PAYMENT', section_reference: '38(1)', description: 'Compensation within 3 months of award', start_date: '2026-08-01', deadline: '2026-11-01', days_remaining: 68, deadline_risk: 0.31, alert_state: 'AMBER', extension_count: 0, total_paused_days: 0, breached: false, consequence: 'REVIEW' },
];

export const mockExplanation = {
  project_id: 'p1',
  risk_score: 0.82,
  summary: 'Risk score: 82%. Primary driver: Compensation Processing Delay (contributing 24% to risk). Also affected by: Active Litigation, Ownership Complexity.',
  drivers: [
    { feature_name: 'compensation_delay_days', display_name: 'Compensation Processing Delay', contribution: 0.24, direction: 'positive', description: 'Compensation processing has taken 211 days vs comparable median of 74 days', evidence: [{ source: 'Payment System', record_type: 'payment_record', description: '23 of 34 affected owners have pending payments exceeding 180 days', confidence: 0.95, grade: 'HIGH' }], grade: 'HIGH' },
    { feature_name: 'litigation_active', display_name: 'Active Litigation', contribution: 0.19, direction: 'positive', description: '2 active cases with stay orders affecting 12 parcels', evidence: [{ source: 'Court Data', record_type: 'court_order', description: 'WP No. 4521/2026 — Stay on possession for survey nos. 142-153', confidence: 0.92, grade: 'HIGH' }], grade: 'HIGH' },
    { feature_name: 'ownership_complexity', display_name: 'Ownership Complexity', contribution: 0.15, direction: 'positive', description: 'Fragmented holdings: avg 4.2 co-owners, 3 deceased owners pending mutation', evidence: [{ source: 'Land Records', record_type: 'land_record', description: '3 parcels with deceased owners, heirs not recorded', confidence: 0.88, grade: 'MEDIUM' }], grade: 'MEDIUM' },
    { feature_name: 'grievance_count', display_name: 'Active Grievances', contribution: 0.11, direction: 'positive', description: '7 active grievances, 2 regarding valuation disputes', evidence: [{ source: 'Grievance Portal', record_type: 'grievance', description: '7 unresolved grievances filed since June 2026', confidence: 0.82, grade: 'MEDIUM' }], grade: 'MEDIUM' },
  ],
  total_evidence_records: 8,
};

export const mockRiskTimeline = [
  { date: '2026-06-01', risk_score: 0.42 },
  { date: '2026-06-15', risk_score: 0.45 },
  { date: '2026-07-01', risk_score: 0.48 },
  { date: '2026-07-15', risk_score: 0.52 },
  { date: '2026-08-01', risk_score: 0.58 },
  { date: '2026-08-15', risk_score: 0.64 },
  { date: '2026-09-01', risk_score: 0.72 },
  { date: '2026-09-15', risk_score: 0.78 },
  { date: '2026-09-28', risk_score: 0.82 },
];
