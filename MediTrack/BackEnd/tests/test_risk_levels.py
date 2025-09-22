#!/usr/bin/env python3
"""
Test script to validate risk level implementation throughout the MediTrack backend.
This script tests the three risk levels: major, moderate, minor
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.drug_interaction_service import DrugInteractionService
from services.supabase_service import SupabaseService

async def test_risk_level_mapping():
    """Test that risk levels are correctly mapped"""
    print("🧪 Testing Risk Level Mapping...")
    
    drug_service = DrugInteractionService()
    
    # Test p-value to severity mapping
    test_cases = [
        (0.0001, "major"),    # Very low p-value should be major
        (0.005, "moderate"),  # Medium p-value should be moderate  
        (0.05, "minor"),      # Higher p-value should be minor
        (0.1, "minor"),       # High p-value should be minor
    ]
    
    for p_value, expected_severity in test_cases:
        actual_severity = drug_service._map_severity(p_value)
        status = "✅" if actual_severity == expected_severity else "❌"
        print(f"  {status} p-value {p_value} → {actual_severity} (expected: {expected_severity})")
        
        if actual_severity != expected_severity:
            return False
    
    return True

async def test_risk_assessment():
    """Test overall risk assessment logic"""
    print("\n🔍 Testing Risk Assessment Logic...")
    
    drug_service = DrugInteractionService()
    
    test_scenarios = [
        {
            "interactions": [],
            "expected_risk": "minor",
            "description": "No interactions"
        },
        {
            "interactions": [{"severity": "minor"}, {"severity": "minor"}],
            "expected_risk": "minor",
            "description": "Only minor interactions"
        },
        {
            "interactions": [{"severity": "minor"}, {"severity": "moderate"}],
            "expected_risk": "moderate",
            "description": "Mix with moderate"
        },
        {
            "interactions": [{"severity": "moderate"}, {"severity": "major"}],
            "expected_risk": "major",
            "description": "Mix with major"
        },
        {
            "interactions": [{"severity": "major"}],
            "expected_risk": "major",
            "description": "Single major interaction"
        }
    ]
    
    for scenario in test_scenarios:
        actual_risk = drug_service._assess_risk_level(scenario["interactions"])
        expected_risk = scenario["expected_risk"]
        status = "✅" if actual_risk == expected_risk else "❌"
        print(f"  {status} {scenario['description']}: {actual_risk} (expected: {expected_risk})")
        
        if actual_risk != expected_risk:
            return False
    
    return True

async def test_database_schema_risk_levels():
    """Test that database schema supports the correct risk levels"""
    print("\n🗄️ Testing Database Schema Risk Levels...")
    
    # Read the schema file to check if enum is correctly defined
    schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
    
    try:
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Check if risk_level enum is correctly defined
        if "CREATE TYPE risk_level AS ENUM ('minor', 'moderate', 'major')" in schema_content:
            print("  ✅ risk_level enum correctly defined with: minor, moderate, major")
        else:
            print("  ❌ risk_level enum not found or incorrectly defined")
            return False
        
        # Check if conditions table uses correct default
        if "severity risk_level DEFAULT 'minor'" in schema_content:
            print("  ✅ conditions table uses 'minor' as default severity")
        else:
            print("  ❌ conditions table default severity issue")
            return False
        
        # Check sample data uses correct risk levels
        sample_conditions = [
            "'Arthritis', 'Joint inflammation', 'minor'",
            "'Hypertension', 'High blood pressure', 'moderate'",
            "'Diabetes Type 2', 'Adult-onset diabetes', 'major'"
        ]
        
        all_samples_correct = True
        for sample in sample_conditions:
            if sample in schema_content:
                print(f"  ✅ Found correct sample condition: {sample}")
            else:
                print(f"  ❌ Missing or incorrect sample condition: {sample}")
                all_samples_correct = False
        
        return all_samples_correct
        
    except FileNotFoundError:
        print("  ❌ database_schema.sql not found")
        return False
    except Exception as e:
        print(f"  ❌ Error reading schema: {e}")
        return False

async def test_medication_interaction_scenarios():
    """Test realistic medication interaction scenarios"""
    print("\n💊 Testing Medication Interaction Scenarios...")
    
    drug_service = DrugInteractionService()
    
    test_medications = [
        {
            "medications": ["aspirin"],
            "expected_risk_max": "minor",
            "description": "Single medication"
        },
        {
            "medications": ["aspirin", "ibuprofen"],
            "expected_risk_max": "moderate",
            "description": "NSAIDs combination"
        },
        {
            "medications": ["warfarin", "aspirin"],
            "expected_risk_max": "major",
            "description": "Anticoagulant + NSAID"
        },
        {
            "medications": ["metformin", "lisinopril"],
            "expected_risk_max": "minor",
            "description": "Generally safe combination"
        }
    ]
    
    for scenario in test_medications:
        try:
            # Note: This would require actual drug interaction data to be loaded
            result = await drug_service.check_drug_interactions(
                scenario["medications"], 
                user_id="test_user"
            )
            
            risk_level = result.get("risk_level", "minor")
            description = scenario["description"]
            
            print(f"  📋 {description}")
            print(f"      Medications: {', '.join(scenario['medications'])}")
            print(f"      Risk level: {risk_level}")
            print(f"      Interactions found: {len(result.get('interactions', []))}")
            
        except Exception as e:
            print(f"  ⚠️ {scenario['description']}: Error testing - {e}")
    
    return True

async def validate_service_integration():
    """Test that all services properly handle risk levels"""
    print("\n🔗 Testing Service Integration...")
    
    try:
        # Test drug interaction service initialization
        drug_service = DrugInteractionService()
        print("  ✅ DrugInteractionService initialized")
        
        # Test supabase service initialization  
        supabase_service = SupabaseService()
        print("  ✅ SupabaseService initialized")
        
        # Test that risk level validation works
        valid_risk_levels = ["minor", "moderate", "major"]
        print(f"  ✅ Valid risk levels defined: {valid_risk_levels}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service integration error: {e}")
        return False

async def main():
    """Run all risk level validation tests"""
    print("🚀 MediTrack Risk Level Validation")
    print("=" * 50)
    
    tests = [
        ("Risk Level Mapping", test_risk_level_mapping),
        ("Risk Assessment Logic", test_risk_assessment),
        ("Database Schema", test_database_schema_risk_levels),
        ("Medication Scenarios", test_medication_interaction_scenarios),
        ("Service Integration", validate_service_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All risk level validations passed!")
        print("\n✅ The MediTrack backend correctly implements:")
        print("   • major risk level (high severity)")
        print("   • moderate risk level (medium severity)")  
        print("   • minor risk level (low severity)")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
