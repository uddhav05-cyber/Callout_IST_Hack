@echo off
echo ============================================================
echo FAKE NEWS DETECTOR - SIMPLE VERSION
echo ============================================================
echo.
echo Starting simple interface with clear TRUE/FALSE display...
echo.
echo Features:
echo - Clear TRUE or FALSE verdict
echo - Confidence score
echo - Evidence with proof
echo.
echo Once started, open your browser to:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

streamlit run app_simple.py
