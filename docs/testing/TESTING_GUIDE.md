# Testing Guide

Comprehensive guide for testing AIAlchemy components and features.

## Table of Contents
- [Overview](#overview)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Test Coverage](#test-coverage)

## Overview

AIAlchemy uses pytest for backend testing and Jest for frontend testing.

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

[Content merged from TESTING.md...]

## Writing Tests

Guidelines for writing effective tests:
1. Test structure
2. Best practices
3. Common patterns

[Content merged from TESTING_SUMMARY.md...]

## CI/CD Integration

How tests are integrated into the CI/CD pipeline:
1. GitHub Actions configuration
2. Test automation
3. Coverage reports

## Test Coverage

Current test coverage and goals:
1. Backend coverage targets
2. Frontend coverage targets
3. Integration test coverage

[Additional content merged from other testing documentation...]