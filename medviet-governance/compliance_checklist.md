# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [ ] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [ ] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [ ] Alert tự động khi phát hiện breach
- [ ] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | ✅ Done | Infra Team |
| Audit logging | API access logs + immutable object storage retention (365 days) | 🚧 In Progress | Platform Team |
| Breach detection | Anomaly monitoring with Prometheus alert rules + on-call paging | 🚧 In Progress | Security Team |

## F. Technical Solutions For Remaining Items
1. **Cross-border transfer logging (A):** triển khai middleware ghi `user`, `resource`, `destination_country`, `timestamp` vào log stream; cấu hình SIEM rule để cảnh báo khi `destination_country != "VN"`.
2. **Consent withdrawal workflow (B):** bổ sung endpoint `DELETE /api/consent/{patient_id}` và job bất đồng bộ để xóa khỏi training datasets, feature store, và snapshots.
3. **Breach auto-alerting (C):** dùng Prometheus + Alertmanager, trigger theo ngưỡng truy cập bất thường và lỗi auth tăng đột biến; gửi cảnh báo qua PagerDuty/Slack.
4. **72h reporting playbook (C):** tạo runbook phân vai (DPO, Security Lead, Legal), checklist evidence, và template báo cáo gửi cơ quan quản lý trong 72 giờ.
5. **Audit logging completion (E):** chuẩn hóa structured JSON logs, ký hash chain theo ngày, và bật policy WORM cho bucket lưu trữ log.
6. **Breach detection completion (E):** thêm detector cho exfiltration patterns, model inference abuse, và baseline drift trên truy cập PII.
