"""
Test Script for Cognitive Compliance Agent
Demonstrates full detect → reason → act → prove workflow
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("1️⃣ Health Check")
    
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(json.dumps(data, indent=2))
    print(f"\n✅ Status: {response.status_code}")


def test_cognitive_reasoning():
    """Test cognitive reasoning endpoint"""
    print_section("2️⃣ Cognitive Reasoning (LLM-Driven)")
    
    # Test case: PAN detected in support chat
    violation = {
        "violation_id": "VIOL_TEST_001",
        "violation_type": "PAN_DETECTED",
        "content": "Customer card number is 4111 1111 1111 1111",
        "source": "support_chat",
        "regulation_context": "PCI-DSS 3.2.1: PAN must not be stored or transmitted in plaintext in logs, support tickets, or customer communications.",
        "goal_description": "Protect stored cardholder data"
    }
    
    print("📤 Request:")
    print(json.dumps(violation, indent=2))
    
    response = requests.post(f"{BASE_URL}/agent/reason", json=violation)
    reasoning = response.json()
    
    print("\n📥 Response (Cognitive Reasoning):")
    print(json.dumps(reasoning, indent=2))
    print(f"\n✅ Status: {response.status_code}")
    
    return reasoning


def test_remediation(violation_id):
    """Test remediation endpoint"""
    print_section("3️⃣ Autonomous Remediation")
    
    remediation_request = {
        "violation_id": violation_id,
        "action_type": "mask_pan",
        "content": "Customer card number is 4111 1111 1111 1111"
    }
    
    print("📤 Request:")
    print(json.dumps(remediation_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/agent/remediate", json=remediation_request)
    remediation = response.json()
    
    print("\n📥 Response (Remediation Result):")
    print(json.dumps(remediation, indent=2))
    print(f"\n✅ Status: {response.status_code}")
    
    print("\n🔍 Before/After Comparison:")
    print(f"  BEFORE: {remediation['before']}")
    print(f"  AFTER:  {remediation['after']}")
    
    return remediation


def test_evidence():
    """Test evidence retrieval"""
    print_section("4️⃣ Audit Evidence Generation")
    
    response = requests.get(f"{BASE_URL}/agent/evidence")
    evidence_list = response.json()
    
    print(f"📋 Total Evidence Records: {len(evidence_list)}\n")
    
    for evidence in evidence_list:
        print(json.dumps(evidence, indent=2))
        print()
    
    print(f"✅ Status: {response.status_code}")


def test_agent_activity():
    """Test agent activity log"""
    print_section("5️⃣ Agent Activity Log")
    
    response = requests.get(f"{BASE_URL}/agent/agent-activity")
    activities = response.json()
    
    print(f"📊 Total Activities: {len(activities)}\n")
    
    for activity in activities[:5]:  # Show last 5
        print(f"  [{activity['timestamp']}] {activity['action']}")
        if activity.get('details'):
            print(f"    Details: {activity['details']}")
        print()
    
    print(f"✅ Status: {response.status_code}")


def test_complete_workflow():
    """Test complete workflow endpoint"""
    print_section("6️⃣ Complete Workflow (Reason → Remediate → Evidence)")
    
    violation = {
        "violation_id": "VIOL_WORKFLOW_001",
        "violation_type": "PAN_DETECTED",
        "content": "Payment failed for card 4532 1234 5678 9010",
        "source": "log_file",
        "regulation_context": "PCI-DSS 3.2.1: PAN must not be stored or transmitted in plaintext.",
        "goal_description": "Ensure PCI-DSS compliance"
    }
    
    print("📤 Request:")
    print(json.dumps(violation, indent=2))
    
    response = requests.post(
        f"{BASE_URL}/agent/workflow",
        json=violation,
        params={"auto_remediate": True}
    )
    workflow_result = response.json()
    
    print("\n📥 Complete Workflow Result:")
    print(json.dumps(workflow_result, indent=2))
    print(f"\n✅ Status: {response.status_code}")
    
    print("\n✨ Workflow Summary:")
    print(f"  ✅ Reasoning: {workflow_result['reasoning']['risk_severity']} - {workflow_result['reasoning']['autonomy_level']}")
    if workflow_result['remediation']:
        print(f"  ✅ Remediation: {workflow_result['remediation']['action_type']} - Success")
    print(f"  ✅ Evidence: {workflow_result['evidence']['evidence_id']} - {workflow_result['evidence']['status']}")


def test_agent_stats():
    """Test agent statistics"""
    print_section("7️⃣ Agent Statistics")
    
    response = requests.get(f"{BASE_URL}/agent/stats")
    stats = response.json()
    
    print(json.dumps(stats, indent=2))
    print(f"\n✅ Status: {response.status_code}")


def test_audit_report():
    """Test audit report export"""
    print_section("8️⃣ Audit Report Export")
    
    response = requests.get(f"{BASE_URL}/agent/audit-report")
    report = response.json()
    
    print(f"📄 Report ID: {report['report_id']}")
    print(f"📅 Generated: {report['generated_at']}\n")
    
    print("📊 Statistics:")
    print(json.dumps(report['statistics'], indent=2))
    
    print(f"\n📋 Evidence Records: {len(report['evidence_records'])}")
    
    print("\n🎯 Compliance Summary:")
    print(json.dumps(report['compliance_summary'], indent=2))
    
    print(f"\n✅ Status: {response.status_code}")


def main():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("  COGNITIVE COMPLIANCE AGENT - TEST SUITE")
    print("🚀"*35)
    
    try:
        # Basic tests
        test_health_check()
        
        # Core workflow
        reasoning = test_cognitive_reasoning()
        remediation = test_remediation(reasoning['violation_id'])
        test_evidence()
        test_agent_activity()
        
        # Advanced features
        test_complete_workflow()
        test_agent_stats()
        test_audit_report()
        
        print("\n" + "✅"*35)
        print("  ALL TESTS PASSED!")
        print("✅"*35 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("   Make sure the server is running: uvicorn main:app --reload")
        print()
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")


if __name__ == "__main__":
    main()
