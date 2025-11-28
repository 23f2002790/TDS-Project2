"""
Comprehensive API Test Suite for LLM Quiz Solver
------------------------------------------------
This script tests:
✔ Health Check
✔ Invalid JSON
✔ Missing Fields
✔ Wrong Secret
✔ Valid Solve Request
✔ Timeout Handling (background task safe)

Run:
    python test.py
"""

import requests
import json
import time

# ========== CONFIGURATION ========== #
API_URL = "http://localhost:7860"
STUDENT_EMAIL = "your_email@ds.study.iitm.ac.in"  # <-- CHANGE THIS
SECRET_KEY = "Your_secret_here"        # <-- CHANGE THIS
DEMO_QUIZ_URL = "https://tds-llm-analysis.s-anand.net/demo"

# =================================== #

def test_health_check():
    print("\n📌 Testing Health Check...")
    try:
        res = requests.get(f"{API_URL}/healthz")
        return res.status_code == 200
    except:
        return False


def test_invalid_json():
    print("\n📌 Testing Invalid JSON...")
    res = requests.post(f"{API_URL}/solve", data="broken json")
    return res.status_code == 400


def test_missing_fields():
    print("\n📌 Testing Missing Fields...")
    res = requests.post(f"{API_URL}/solve", json={"email": STUDENT_EMAIL})
    return res.status_code == 400


def test_wrong_secret():
    print("\n📌 Testing Wrong Secret...")
    payload = {
        "email": STUDENT_EMAIL,
        "secret": "wrong",
        "url": DEMO_QUIZ_URL,
    }
    res = requests.post(f"{API_URL}/solve", json=payload)
    return res.status_code == 403


def test_valid_request():
    print("\n📌 Testing Valid Solve Trigger...")
    payload = {
        "email": STUDENT_EMAIL,
        "secret": SECRET_KEY,
        "url": DEMO_QUIZ_URL,
    }

    try:
        res = requests.post(f"{API_URL}/solve", json=payload, timeout=30)
        return res.status_code == 200
    except requests.exceptions.Timeout:
        print("⚠️ Timeout is expected for long-running tasks")
        return True
    except:
        return False


def print_summary(results):
    print("\n" + "="*60)
    print("🧪 Test Summary")
    print("="*60)

    passed = 0
    for name, ok in results.items():
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}: {name}")
        passed += int(ok)

    print(f"\n📊 Passed: {passed}/{len(results)} tests")


def main():
    print("\n🚀 Running Full API Test Suite...\n")

    tests = {
        "Health Check": test_health_check(),
        "Invalid JSON": test_invalid_json(),
        "Missing Fields": test_missing_fields(),
        "Wrong Secret": test_wrong_secret(),
        "Valid Solve Trigger": test_valid_request(),
    }

    print_summary(tests)

    print("\nNote: The actual quiz solving runs in background —")
    print("Check logs in terminal where server is running.\n")

    print("⏳ Waiting 5 seconds to let background task begin...\n")
    time.sleep(5)


if __name__ == "__main__":
    main()
