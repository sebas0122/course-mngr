#!/usr/bin/env python3
##
# @file test_sqlmodel_integration.py
# @brief Integration test suite for SQLModel data models
#
# This script verifies that the Course and Professor SQLModel classes work correctly
# and integrate properly with the courses_functions module. It performs a series of
# tests including object creation, serialization, validation, and function imports.
#
# Test coverage:
# - Course model creation and methods
# - Professor model creation and validation
# - SQLModel serialization (model_dump)
# - Input validation and normalization
# - Function imports from courses_functions
#
# @author Nelson Parra (nelson.parra@udea.edu.co)
# @date 2025

"""
Test script to verify SQLModel integration works correctly.
"""

from course import Course
from professor import Professor

print("=" * 60)
print("Testing SQLModel Integration")
print("=" * 60)

# Test 1: Create a Course object
print("\n1. Testing Course Model:")
print("-" * 40)
try:
    course = Course(
        nombre="INFORMÁTICA I",
        facultad=2,
        dependencia=2,
        ide="IIE",
        materia=1,
        grupo=1,
        tipo="T-P",
        es_lab=False,
        nivel=1,
        horas_teoricas=4,
        horas_practicas=3,
        horas_tp=0,
        electiva=False,
        es_dept=True,
        horario="L16-18|M8-10",
        profesor=[123456, 789012],
        aula="A101"
    )
    print(f"✓ Course created successfully")
    print(f"  Name: {course.nombre}")
    print(f"  Code: {course.get_codigo()}")
    print(f"  Schedule: {course.horario}")
    print(f"  Professors: {course.profesor}")
except Exception as e:
    print(f"✗ Failed to create course: {e}")

# Test 2: Create a Professor object
print("\n2. Testing Professor Model:")
print("-" * 40)
try:
    prof = Professor(
        nombre="Dr. John Doe",
        identificacion=123456,
        correo="johndoe@example.com",
        catedra=True,
        contratacion="ocasional",
        formacion="doctorado"
    )
    print(f"✓ Professor created successfully")
    print(f"  Name: {prof.nombre}")
    print(f"  ID: {prof.identificacion}")
    print(f"  Email: {prof.correo}")
    print(f"  Hiring: {prof.contratacion}")
    print(f"  Education: {prof.formacion}")
except Exception as e:
    print(f"✗ Failed to create professor: {e}")

# Test 3: Test model_dump
print("\n3. Testing SQLModel serialization:")
print("-" * 40)
try:
    course_dict = course.model_dump(exclude_none=True, exclude={'id'})
    print(f"✓ Course serialized to dict")
    print(f"  Keys: {list(course_dict.keys())}")
    
    prof_dict = prof.model_dump(exclude_none=True, exclude={'id'})
    print(f"✓ Professor serialized to dict")
    print(f"  Keys: {list(prof_dict.keys())}")
except Exception as e:
    print(f"✗ Failed to serialize: {e}")

# Test 4: Test validation
print("\n4. Testing validation:")
print("-" * 40)
try:
    # Test invalid hiring type
    invalid_prof = Professor(
        nombre="Jane Smith",
        identificacion=999999,
        correo="jane@example.com",
        contratacion="invalid_type",  # This should be normalized
        formacion="maestría"
    )
    if invalid_prof.contratacion == "NO ESPECIFICADO":
        print(f"✓ Invalid hiring type properly handled")
    else:
        print(f"✗ Validation not working properly")
except Exception as e:
    print(f"✗ Validation test failed: {e}")

# Test 5: Test course_functions imports
print("\n5. Testing courses_functions integration:")
print("-" * 40)
try:
    from courses_functions import (
        connectSQL, 
        retrieveDBTable, 
        getClassesList, 
        getProfessorsData,
        addProfessorToDB
    )
    print(f"✓ All functions imported successfully")
    print(f"  - connectSQL")
    print(f"  - retrieveDBTable")
    print(f"  - getClassesList")
    print(f"  - getProfessorsData")
    print(f"  - addProfessorToDB")
except Exception as e:
    print(f"✗ Failed to import functions: {e}")

# Test 6: Test mixed schedule formats
print("\n6. Testing mixed schedule formats:")
print("-" * 40)

from courses_functions import normalize_schedule, getHoursLong

cases = [
    ("LM8-10", "L8-10|M8-10", 4),
    ("L16-18|M8-10", "L16-18|M8-10", 4),
    ("L10-12|M10-12|W10-12", "L10-12|M10-12|W10-12", 6),
]

for raw, expected_norm, expected_hours in cases:
    try:
        norm = normalize_schedule(raw)
        hrs = getHoursLong(raw)
        ok = (norm == expected_norm and hrs == expected_hours)
        print(f"{'✓' if ok else '✗'} {raw} -> norm={norm}, hours={hrs}")
    except Exception as e:
        print(f"✗ {raw} -> Error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
