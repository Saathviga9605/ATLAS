"""
Test Examples - Demonstrates all key functionality with expected outputs
Run this after setting up the main agent to verify everything works
"""

import os
import json
from regulation_intelligence_agent import (
    RegulationIntelligenceAgent,
    ObligationExtractor,
    ComplianceGoal
)

# Set your API key
os.environ["OPENROUTER_API_KEY"] = "your-openrouter-api-key-here"

# Optional: set model
# os.environ["LLM_MODEL"] = "anthropic/claude-3-haiku"


def test_single_text_extraction():
    """Test 1: Extract from single regulatory text"""
    print("\n" + "="*60)
    print("TEST 1: Single Text Extraction")
    print("="*60)
    
    extractor = ObligationExtractor()
    
    # Test case 1: PCI-DSS text
    pci_text = """
Requirement 3.2: Sensitive authentication data must not be stored after authorization.
After authorization, do not store the full contents of any track from the magnetic stripe 
located on the back of a card, the equivalent data on a chip, or elsewhere. This includes 
the card verification value (CVV2), PIN, and PIN block.
    """
    
    goals = extractor.extract_from_text(
        text=pci_text,
        regulation="PCI-DSS v4.0",
        section="Requirement 3.2"
    )
    
    print(f"\n✓ Extracted {len(goals)} goals from PCI-DSS text")
    print("\nStructured Output:")
    for goal in goals:
        print(json.dumps(goal.model_dump(), indent=2))
    
    # Test case 2: GDPR text
    gdpr_text = """
Article 32 - Security of processing
The controller shall implement appropriate technical and organisational measures to ensure 
a level of security appropriate to the risk, including:
(a) the pseudonymisation and encryption of personal data;
(b) the ability to ensure the ongoing confidentiality, integrity, availability and resilience.
    """
    
    goals = extractor.extract_from_text(
        text=gdpr_text,
        regulation="GDPR",
        section="Article 32"
    )
    
    print(f"\n✓ Extracted {len(goals)} goals from GDPR text")
    for goal in goals:
        print(f"\n{goal.goal_id}: {goal.goal_description}")
        print(f"  Risk: {goal.risk_level} | Verb: {goal.verb}")
    
    return goals


def test_rag_queries():
    """Test 2: RAG queries on both knowledge bases"""
    print("\n" + "="*60)
    print("TEST 2: RAG Queries")
    print("="*60)
    
    agent = RegulationIntelligenceAgent()
    agent.setup(download_pdfs=False, use_existing=False)
    
    # Test regulatory queries
    print("\n--- Regulatory Knowledge Base ---")
    questions = [
        "What data must not be stored according to PCI-DSS?",
        "How should cardholder data be protected?",
        "What are the encryption requirements?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = agent.rag_engine.query_regulations(q)
        print(f"A: {answer[:200]}...")
    
    # Test policy queries
    print("\n--- Company Policy Knowledge Base ---")
    policy_questions = [
        "What is the MFA requirement?",
        "How long do we retain data?",
        "What is the incident response timeline?"
    ]
    
    for q in policy_questions:
        print(f"\nQ: {q}")
        answer = agent.rag_engine.query_policies(q)
        print(f"A: {answer[:200]}...")
    
    return agent


def test_obligation_mining(agent=None):
    """Test 3: Full obligation mining pipeline"""
    print("\n" + "="*60)
    print("TEST 3: Obligation Mining")
    print("="*60)
    
    if agent is None:
        agent = RegulationIntelligenceAgent()
        agent.setup(download_pdfs=False, use_existing=False)
    
    # Mine from regulatory KB
    print("\n--- Mining Regulatory Obligations ---")
    reg_goals = agent.mine_obligations("PCI-DSS v4.0", source_type="regulatory")
    
    print(f"\n✓ Extracted {len(reg_goals)} regulatory goals")
    
    # Analyze results
    high_risk = [g for g in reg_goals if g.risk_level == "High"]
    medium_risk = [g for g in reg_goals if g.risk_level == "Medium"]
    low_risk = [g for g in reg_goals if g.risk_level == "Low"]
    
    print(f"\nRisk Distribution:")
    print(f"  High Risk: {len(high_risk)}")
    print(f"  Medium Risk: {len(medium_risk)}")
    print(f"  Low Risk: {len(low_risk)}")
    
    # Show sample high-risk goals
    print("\n--- Sample High-Risk Goals ---")
    for goal in high_risk[:3]:
        print(f"\n{goal.goal_id}: {goal.goal_description}")
        print(f"  Verb: {goal.verb}")
        print(f"  Subject: {goal.subject}")
        print(f"  Object: {goal.object}")
        print(f"  Entities: {', '.join(goal.applicable_entities)}")
    
    # Mine from policy KB
    print("\n--- Mining Policy Obligations ---")
    policy_goals = agent.mine_obligations("Company Policy v3.0", source_type="policy")
    
    print(f"\n✓ Extracted {len(policy_goals)} policy goals")
    
    # Save both to JSON
    agent.save_goals_to_json(reg_goals, "test_regulatory_goals.json")
    agent.save_goals_to_json(policy_goals, "test_policy_goals.json")
    
    return reg_goals, policy_goals


def test_chunk_retrieval(agent=None):
    """Test 4: Retrieve relevant document chunks"""
    print("\n" + "="*60)
    print("TEST 4: Chunk Retrieval")
    print("="*60)
    
    if agent is None:
        agent = RegulationIntelligenceAgent()
        agent.setup(download_pdfs=False, use_existing=False)
    
    queries = [
        "encryption requirements",
        "authentication data storage",
        "access control policies"
    ]
    
    for query in queries:
        print(f"\n--- Query: '{query}' ---")
        
        # Retrieve from regulatory KB
        reg_chunks = agent.rag_engine.retrieve_relevant_chunks(
            query=query,
            kb_type="regulatory",
            k=2
        )
        
        print(f"\nRegulatory KB ({len(reg_chunks)} chunks):")
        for i, chunk in enumerate(reg_chunks, 1):
            print(f"\nChunk {i} (score: similarity-based):")
            print(chunk.page_content[:200] + "...")
        
        # Retrieve from policy KB
        policy_chunks = agent.rag_engine.retrieve_relevant_chunks(
            query=query,
            kb_type="policy",
            k=2
        )
        
        print(f"\nPolicy KB ({len(policy_chunks)} chunks):")
        for i, chunk in enumerate(policy_chunks, 1):
            print(f"\nChunk {i}:")
            print(chunk.page_content[:200] + "...")


def test_goal_filtering(goals):
    """Test 5: Filter and analyze extracted goals"""
    print("\n" + "="*60)
    print("TEST 5: Goal Filtering & Analysis")
    print("="*60)
    
    # Filter by verb
    must_goals = [g for g in goals if g.verb in ["must", "must not"]]
    shall_goals = [g for g in goals if g.verb in ["shall", "shall not"]]
    should_goals = [g for g in goals if g.verb in ["should", "should not"]]
    
    print(f"\nVerb Distribution:")
    print(f"  Must/Must Not: {len(must_goals)}")
    print(f"  Shall/Shall Not: {len(shall_goals)}")
    print(f"  Should/Should Not: {len(should_goals)}")
    
    # Filter by subject
    subjects = {}
    for goal in goals:
        subjects[goal.subject] = subjects.get(goal.subject, 0) + 1
    
    print(f"\nSubject Distribution:")
    for subject, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True):
        print(f"  {subject}: {count}")
    
    # Group by regulation
    by_regulation = {}
    for goal in goals:
        if goal.regulation not in by_regulation:
            by_regulation[goal.regulation] = []
        by_regulation[goal.regulation].append(goal)
    
    print(f"\nGoals by Regulation:")
    for reg, reg_goals in by_regulation.items():
        print(f"  {reg}: {len(reg_goals)} goals")


def test_json_output_validation():
    """Test 6: Validate JSON output matches schema"""
    print("\n" + "="*60)
    print("TEST 6: JSON Output Validation")
    print("="*60)
    
    # Create a sample goal
    sample_goal = ComplianceGoal(
        goal_id="TEST-001",
        parent_goal_id=None,
        regulation="Test Regulation",
        section="Section 1",
        original_text="Organizations must implement security controls.",
        goal_description="Implement security controls",
        verb="must",
        subject="Organization",
        object="implement security controls",
        risk_level="High",
        applicable_entities=["All Entities"]
    )
    
    # Serialize to JSON
    goal_json = sample_goal.model_dump_json(indent=2)
    print("\nSample Goal JSON:")
    print(goal_json)
    
    # Validate it can be deserialized
    reconstructed = ComplianceGoal.model_validate_json(goal_json)
    print("\n✓ JSON validation successful")
    print(f"✓ Reconstructed goal: {reconstructed.goal_id}")
    
    # Check all required fields
    required_fields = ["goal_id", "regulation", "section", "original_text", 
                      "goal_description", "verb", "subject", "object", "risk_level"]
    
    goal_dict = json.loads(goal_json)
    missing_fields = [f for f in required_fields if f not in goal_dict]
    
    if missing_fields:
        print(f"\n✗ Missing required fields: {missing_fields}")
    else:
        print(f"\n✓ All required fields present")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print("REGULATION INTELLIGENCE AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test 1: Single text extraction
    goals = test_single_text_extraction()
    
    # Test 2: RAG queries
    agent = test_rag_queries()
    
    # Test 3: Obligation mining
    reg_goals, policy_goals = test_obligation_mining(agent)
    
    # Test 4: Chunk retrieval
    test_chunk_retrieval(agent)
    
    # Test 5: Goal filtering
    all_goals = reg_goals + policy_goals
    test_goal_filtering(all_goals)
    
    # Test 6: JSON validation
    test_json_output_validation()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED!")
    print("="*70)
    print(f"\nTotal Goals Extracted: {len(all_goals)}")
    print(f"  Regulatory: {len(reg_goals)}")
    print(f"  Policy: {len(policy_goals)}")
    print("\nOutput files created:")
    print("  - ./output/test_regulatory_goals.json")
    print("  - ./output/test_policy_goals.json")


if __name__ == "__main__":
    run_all_tests()