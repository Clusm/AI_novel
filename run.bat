@echo off
echo 正在启动网文AI工厂...
echo.
set CREWAI_TRACING_ENABLED=false
set CREWAI_TELEMETRY_OPT_OUT=true
set CREWAI_DISABLE_TELEMETRY=true
set OTEL_SDK_DISABLED=true
set OTEL_TRACES_EXPORTER=none
set OTEL_METRICS_EXPORTER=none
set OTEL_LOGS_EXPORTER=none
streamlit run app.py
pause
