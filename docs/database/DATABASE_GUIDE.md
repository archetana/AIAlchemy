# Database Guide

Complete documentation for AIAlchemy's database setup and configuration.

## Table of Contents
- [Overview](#overview)
- [Setup Instructions](#setup-instructions)
- [Vector Database](#vector-database)
- [Supabase Integration](#supabase-integration)
- [Migration Guide](#migration-guide)

## Overview

AIAlchemy supports two database backends:
1. SQLite (Development)
2. PostgreSQL/Supabase (Production)

## Setup Instructions

### Local Development (SQLite)

```bash
# Initialize database
python init_database.py
```

[Content merged from DATABASE_INIT_REQUIREMENTS.md...]

## Vector Database

AIAlchemy uses pgvector for efficient similarity search:

1. Installation
2. Configuration
3. Performance optimization

[Content merged from setup_vector_database.md and vector_db_comparison.md...]

## Supabase Integration

Steps for setting up Supabase:
1. Create project
2. Configure database
3. Set up authentication

[Content merged from SUPABASE_SETUP.md...]

## Migration Guide

Instructions for migrating between database systems...

[Additional content merged from other database documentation...]