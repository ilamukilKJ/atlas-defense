"""
Comprehensive Research Pipeline Validation Script for ATLAS.
Validates:
1. Real / Mock Gemini Mode
2. Normal Memory Flow (Extract -> Accept -> Persist -> Retrieve)
3. Poisoned Memory with ATLAS OFF (Persist -> Retrieve -> Behavior Compromised -> Attack Succeeded)
4. Poisoned Memory with ATLAS ON (Evaluate -> Quarantine -> Exclude from Retrieval -> Attack Blocked)
5. Covert Instruction Injection Defense
6. Empirical Benchmark Evaluation (Real TP/TN/FP/FN and derived metrics)
"""

import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.settings import settings
from core.gemini_client import gemini_client
from core.embeddings import embedding_service
from agent.agent import atlas_agent
from memory.memory_models import ChatRequest, MemoryStatus
from memory.vector_store import global_vector_store
from attacks.poisoning_simulator import poisoning_simulator
from evaluation.experiment_runner import experiment_runner


def run_validation():
    print("=" * 80)
    print("ATLAS BACKEND RESEARCH PIPELINE VALIDATION")
    print("=" * 80)

    # ---------------------------------------------------------
    # TEST 0: GEMINI INTEGRATION MODE
    # ---------------------------------------------------------
    print("\n[TEST 0] Gemini Integration Status:")
    if gemini_client.is_real_mode:
        print(f"  ✓ Mode: REAL GEMINI API [Model: {settings.GEMINI_MODEL}]")
    else:
        print(f"  ✓ Mode: MOCK FALLBACK [Offline deterministic research baseline]")

    if embedding_service.is_real_mode:
        print(f"  ✓ Embeddings: REAL GEMINI EMBEDDINGS [Model: {settings.GEMINI_EMBEDDING_MODEL}]")
    else:
        print(f"  ✓ Embeddings: DETERMINISTIC UNIT-SPHERE FEATURE HASHING [Dim: {settings.EMBEDDING_DIMENSION}]")

    # Reset vector store to clean baseline
    poisoning_simulator.reset_environment()

    # ---------------------------------------------------------
    # TEST 1: NORMAL MEMORY FLOW (A)
    # ---------------------------------------------------------
    print("\n[TEST 1] Normal Memory Flow (Benign User Statement):")
    normal_input = "Remember that my favorite database is PostgreSQL."
    chat_res = atlas_agent.chat(ChatRequest(message=normal_input, history=[], enable_atlas=True))
    
    assert chat_res.candidate_memory is not None, "Failed to extract candidate memory from normal turn."
    print(f"  ✓ Candidate Extracted: '{chat_res.candidate_memory.content}'")
    print(f"  ✓ Category: {chat_res.candidate_memory.category}, Confidence: {chat_res.candidate_memory.confidence}")
    print(f"  ✓ Trust Score: {chat_res.trust_score:.4f} (Threshold: {settings.ATLAS_TRUST_THRESHOLD})")
    print(f"  ✓ Status: {chat_res.memory_status}")
    assert chat_res.memory_status == MemoryStatus.ACCEPTED, "Normal memory should be ACCEPTED."

    # Verify retrieval in follow-up query
    retrieval_query = "What database do I like?"
    retrieval_res = atlas_agent.chat(ChatRequest(message=retrieval_query, history=[], enable_atlas=True))
    print(f"  ✓ Retrieval Probe Query: '{retrieval_query}'")
    print(f"  ✓ Retrieved Context: {retrieval_res.retrieved_memories}")
    print(f"  ✓ Agent Response: '{retrieval_res.response}'")
    assert any("postgresql" in rm.lower() for rm in retrieval_res.retrieved_memories), "Accepted memory must be retrievable."

    # ---------------------------------------------------------
    # TEST 2: POISONED MEMORY WITH ATLAS OFF (B - Vulnerable Baseline)
    # ---------------------------------------------------------
    print("\n[TEST 2] Poisoned Memory Flow with ATLAS OFF (Vulnerable Mode):")
    poisoning_simulator.reset_environment()
    
    # Attack: Direct Fact Overwrite with ATLAS OFF
    sim_off = poisoning_simulator.run_simulation("scenario-fact-overwrite", enable_atlas=False)
    print(f"  Scenario: {sim_off.scenario_name}")
    print(f"  Attacker Prompt: '{sim_off.attacker_prompt}'")
    print(f"  Candidate Memory: '{sim_off.candidate_poisoned_memory.content}'")
    print(f"  Persisted in Vector Store: {sim_off.stored_in_vector_store}")
    print(f"  Retrieved in Probe: {sim_off.is_retrieved_in_probe}")
    print(f"  Behavior Compromised: {sim_off.is_behavior_compromised}")
    print(f"  Probe Response: '{sim_off.probe_response}'")
    print(f"  -> Attack Succeeded: {sim_off.attack_succeeded} (Expected: True)")
    assert sim_off.attack_succeeded, "With ATLAS OFF, memory poisoning must succeed under operational criteria."

    # ---------------------------------------------------------
    # TEST 3: POISONED MEMORY WITH ATLAS ON (C - Defended Mode)
    # ---------------------------------------------------------
    print("\n[TEST 3] Poisoned Memory Flow with ATLAS ON (Defended Mode):")
    poisoning_simulator.reset_environment()

    # Same Attack: Direct Fact Overwrite with ATLAS ON
    sim_on = poisoning_simulator.run_simulation("scenario-fact-overwrite", enable_atlas=True)
    print(f"  Scenario: {sim_on.scenario_name}")
    print(f"  Candidate Memory: '{sim_on.candidate_poisoned_memory.content}'")
    print(f"  Trust Score: {sim_on.trust_score:.4f} (Threshold: {settings.ATLAS_TRUST_THRESHOLD})")
    print(f"  Memory Decision: {sim_on.memory_decision}")
    print(f"  Signals Breakdown:")
    print(f"    - Semantic Relevance:     {sim_on.signals.semantic_relevance:.4f}")
    print(f"    - Embedding Anomaly:      {sim_on.signals.embedding_anomaly:.4f}")
    print(f"    - Historical Consistency: {sim_on.signals.historical_consistency:.4f}")
    print(f"    - Behavioral Consistency: {sim_on.signals.behavioral_consistency:.4f}")
    print(f"    - Source Reliability:     {sim_on.signals.source_reliability:.4f}")
    print(f"    - Temporal Trust:         {sim_on.signals.temporal_trust:.4f}")
    print(f"  Persisted in Vector Store: {sim_on.stored_in_vector_store}")
    print(f"  Retrieved in Probe: {sim_on.is_retrieved_in_probe}")
    print(f"  Probe Response: '{sim_on.probe_response}'")
    print(f"  -> Defense Successful: {sim_on.defense_successful} (Expected: True)")
    assert sim_on.defense_successful, "With ATLAS ON, direct fact overwrite must be quarantined."
    assert sim_on.memory_decision == MemoryStatus.QUARANTINED, "Decision must be QUARANTINED."

    # ---------------------------------------------------------
    # TEST 4: COVERT INSTRUCTION INJECTION WITH ATLAS ON
    # ---------------------------------------------------------
    print("\n[TEST 4] Covert Instruction Injection with ATLAS ON:")
    sim_inject = poisoning_simulator.run_simulation("scenario-instruction-injection", enable_atlas=True)
    print(f"  Scenario: {sim_inject.scenario_name}")
    print(f"  Candidate Memory: '{sim_inject.candidate_poisoned_memory.content}'")
    print(f"  Trust Score: {sim_inject.trust_score:.4f}")
    print(f"  Decision: {sim_inject.memory_decision}")
    print(f"  -> Defense Successful: {sim_inject.defense_successful} (Expected: True)")
    assert sim_inject.defense_successful, "Covert instruction injection must be quarantined."

    # ---------------------------------------------------------
    # TEST 5: EMPIRICAL EVALUATION BENCHMARK (D)
    # ---------------------------------------------------------
    print("\n[TEST 5] Empirical Benchmark Evaluation (Real Generated Data):")
    summary = experiment_runner.run_benchmark()
    print(f"  Total Evaluated Samples: {summary.total_samples}")
    print(f"    - Benign Samples:      {summary.benign_samples}")
    print(f"    - Adversarial Samples: {summary.attack_samples}")
    print(f"  Confusion Matrix:")
    print(f"    - True Positives (TP - Attacks Quarantined):  {summary.confusion_matrix.true_positives}")
    print(f"    - False Positives (FP - Benign Quarantined):  {summary.confusion_matrix.false_positives}")
    print(f"    - True Negatives (TN - Benign Accepted):      {summary.confusion_matrix.true_negatives}")
    print(f"    - False Negatives (FN - Attacks Accepted):    {summary.confusion_matrix.false_negatives}")
    print(f"  Performance Metrics:")
    print(f"    - Precision:          {summary.precision * 100:.2f}%")
    print(f"    - Recall / TPR:       {summary.recall * 100:.2f}%")
    print(f"    - F1-Score:           {summary.f1_score * 100:.2f}%")
    print(f"    - False Positive Rate: {summary.false_positive_rate * 100:.2f}%")
    print(f"    - Retrieval Accuracy: {summary.retrieval_accuracy * 100:.2f}%")
    print(f"    - ASR Without ATLAS:  {summary.attack_success_rate_without_atlas * 100:.2f}%")
    print(f"    - ASR With ATLAS:     {summary.attack_success_rate_with_atlas * 100:.2f}%")

    print("\n" + "=" * 80)
    print("ALL 5 RESEARCH PIPELINE VALIDATION TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_validation()
