#!/bin/bash
# Smoke Test Script for GPTBuddyAI
# Validates all core functionality is working

set -e

echo "🔥 GPTBuddyAI Smoke Test Suite"
echo "==============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name=$1
    local test_command=$2

    echo -n "Testing: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
}

echo "📦 1. Environment Checks"
echo "------------------------"

run_test "Python 3.10+" "python --version | grep 'Python 3.1'"
run_test "ChromaDB installed" "python -c 'import chromadb'"
run_test "Sentence Transformers installed" "python -c 'import sentence_transformers'"
run_test "Streamlit installed" "python -c 'import streamlit'"
run_test "Plotly installed" "python -c 'import plotly'"
run_test "NetworkX installed" "python -c 'import networkx'"
run_test "Rich installed" "python -c 'import rich'"

echo ""
echo "📁 2. Artifact Checks"
echo "--------------------"

run_test "ChromaDB index exists" "[ -d artifacts/index ]"
run_test "OpenAI data exists" "[ -f artifacts/openai.parquet ]"
run_test "Docs data exists" "[ -f artifacts/docs.parquet ]"
run_test "Topic visualization exists" "[ -f artifacts/topic_clusters_2d.png ]"

echo ""
echo "🤖 3. Agent Module Checks"
echo "-------------------------"

run_test "Agents module imports" "python -c 'from agents import AgentCoordinator, ComplianceAgent, ResearchAgent, SynthesisAgent'"
run_test "Graph module imports" "python -c 'from graph import EntityExtractor, KnowledgeGraphBuilder, GraphEnhancedRAG'"
run_test "Coordinator creates workflows" "python -c 'from agents import AgentCoordinator; c = AgentCoordinator()'"

echo ""
echo "🧪 4. Integration Tests"
echo "-----------------------"

run_test "Unit tests pass" "python tests/test_integration.py"

echo ""
echo "🎨 5. UI Component Checks"
echo "-------------------------"

run_test "Topic browser imports" "python -c 'import sys; sys.path.append(\"src/ui/components\"); from topic_browser import render_topic_browser'"
run_test "Agent workflows imports" "python -c 'import sys; sys.path.append(\"src/ui/components\"); from agent_workflows import render_agent_workflows'"
run_test "Knowledge graph imports" "python -c 'import sys; sys.path.append(\"src/ui/components\"); from knowledge_graph import render_knowledge_graph'"
run_test "Compliance viz imports" "python -c 'import sys; sys.path.append(\"src/ui/components\"); from compliance_viz import render_compliance_heatmap'"
run_test "Temporal viz imports" "python -c 'import sys; sys.path.append(\"src/ui/components\"); from temporal_viz import render_activity_timeline'"

echo ""
echo "==============================="
echo "📊 Test Summary"
echo "==============================="
echo -e "Total Tests:  $((PASSED + FAILED))"
echo -e "${GREEN}✅ Passed:    $PASSED${NC}"
echo -e "${RED}❌ Failed:    $FAILED${NC}"

SUCCESS_RATE=$(( PASSED * 100 / (PASSED + FAILED) ))
echo "Success Rate: ${SUCCESS_RATE}%"
echo "==============================="

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All smoke tests passed! System is healthy.${NC}\n"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Review errors above.${NC}\n"
    exit 1
fi
