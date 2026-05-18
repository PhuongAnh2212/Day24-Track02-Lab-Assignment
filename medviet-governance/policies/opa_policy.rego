package medviet.data_access

import future.keywords.if
import future.keywords.in

# Default: deny all
default allow := false

# Additional deny guardrails
deny if {
    input.user.role == "ml_engineer"
    input.resource == "production_data"
    input.action == "delete"
}

deny if {
    input.data_classification == "restricted"
    input.destination_country != "VN"
}

# Admin được phép tất cả, trừ deny rules bên trên
allow if {
    input.user.role == "admin"
    not deny
}

# ML Engineer: training data + model artifacts + aggregated metrics (read/write theo nhu cầu)
allow if {
    input.user.role == "ml_engineer"
    input.resource in {"training_data", "model_artifacts", "aggregated_metrics"}
    input.action in {"read", "write"}
    not deny
}

# Data Analyst: chỉ đọc aggregated metrics và ghi reports
allow if {
    input.user.role == "data_analyst"
    (
        (input.resource == "aggregated_metrics"; input.action == "read")
        or
        (input.resource == "reports"; input.action == "write")
    )
    not deny
}

# Intern: chỉ sandbox
allow if {
    input.user.role == "intern"
    input.resource == "sandbox_data"
    input.action in {"read", "write"}
    not deny
}
