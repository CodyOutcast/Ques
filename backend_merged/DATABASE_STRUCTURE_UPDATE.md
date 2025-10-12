# Database Structure Update: Location, Statistics, and Birthday System

This document describes the new database structure for handling user locations, project/institution statistics, and birthday-based age calculation.

## Overview

The update introduces several new features:

1. **Location System**: Structured province/city selection based on Chinese administrative divisions
2. **User Statistics**: Tracking of user projects and institutions 
3. **Birthday-based Age System**: Automatic age calculation with birthday triggers

## New Tables

### 1. Location Tables

#### `provinces`
Stores Chinese provinces and municipalities.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `name_en` | VARCHAR(100) | English name |
| `name_cn` | VARCHAR(100) | Chinese name |

#### `cities`
Stores Chinese cities with province references.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `province_id` | INTEGER | Foreign key to provinces |
| `name_en` | VARCHAR(100) | English name |
| `name_cn` | VARCHAR(100) | Chinese name |

### 2. Statistics Tables

#### `user_project_counts`
Tracks project counts for each user.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | Foreign key to users (unique) |
| `owned_projects` | INTEGER | Projects user created/owns |
| `collaborated_projects` | INTEGER | Projects user collaborates on |
| `total_projects` | INTEGER | Total projects associated with |
| `created_at` | DATETIME | Record creation time |
| `updated_at` | DATETIME | Last update time |

#### `user_institution_counts`
Tracks institution counts for each user.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `user_id` | INTEGER | Foreign key to users (unique) |
| `educational_institutions` | INTEGER | Schools, universities |
| `work_institutions` | INTEGER | Companies, organizations |
| `other_institutions` | INTEGER | Other types |
| `total_institutions` | INTEGER | Total institutions |
| `created_at` | DATETIME | Record creation time |
| `updated_at` | DATETIME | Last update time |

### 3. Institution Tables

#### `institutions`
Stores institution information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `name` | VARCHAR(255) | Institution name |
| `name_en` | VARCHAR(255) | English name (optional) |
| `type` | VARCHAR(50) | Type: "university", "company", etc. |
| `city_id` | INTEGER | Foreign key to cities |
| `province_id` | INTEGER | Foreign key to provinces |
| `description` | TEXT | Institution description |
| `website` | VARCHAR(512) | Website URL |
| `logo_url` | VARCHAR(512) | Logo image URL |
| `is_verified` | INTEGER | Verification status (0/1) |
| `is_active` | INTEGER | Active status (0/1) |
| `created_at` | DATETIME | Record creation time |
| `updated_at` | DATETIME | Last update time |

#### `user_institutions`
Junction table linking users to institutions.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | Primary key, foreign key to users |
| `institution_id` | INTEGER | Primary key, foreign key to institutions |
| `role` | VARCHAR(100) | Role: "student", "employee", etc. |
| `start_date` | DATETIME | When user joined/started |
| `end_date` | DATETIME | When user left/graduated (null if current) |
| `is_current` | INTEGER | Current status (0/1) |
| `position` | VARCHAR(100) | Job title, degree, etc. |
| `department` | VARCHAR(100) | Department or major |
| `description` | TEXT | Additional details |
| `created_at` | DATETIME | Record creation time |
| `updated_at` | DATETIME | Last update time |

## Updated Tables

### `users` Table Updates

New columns added:

| Column | Type | Description |
|--------|------|-------------|
| `birthday` | DATE | User's birthday for age calculation |
| `age` | INTEGER | Auto-calculated age via trigger |
| `province_id` | INTEGER | Foreign key to provinces |
| `city_id` | INTEGER | Foreign key to cities |

## Database Triggers and Functions

### 1. Age Calculation Trigger

**Function**: `calculate_age_from_birthday()`
- Automatically calculates age from birthday when inserted/updated
- Triggered on INSERT or UPDATE of birthday column

**Trigger**: `trigger_update_age_on_birthday`
- Executes before INSERT or UPDATE on users table
- Updates age column based on birthday

### 2. Birthday Checker Function

**Function**: `check_birthday_and_increment_age()`
- Checks for users with birthdays today
- Increments age by 1 for birthday users
- Should be called daily via cron job

### 3. Project Count Triggers

**Function**: `update_user_project_counts()`
- Updates project counts when projects or user_projects change
- Maintains accurate statistics automatically

**Triggers**:
- `trigger_update_project_counts_on_user_project`: On user_projects table changes
- `trigger_update_project_counts_on_project`: On projects table changes

## Location Data

The location data is based on Chinese administrative divisions:

- **31 Provinces/Municipalities**: Including Beijing, Shanghai, Guangdong, etc.
- **50 Cities**: Major cities across all provinces
- **Hierarchical Structure**: Cities belong to provinces

### Data Population

Use the provided script to populate location data:

```bash
python populate_locations.py
```

## Migration and Setup

### 1. Run the Migration

```bash
alembic upgrade head
```

### 2. Populate Location Data

```bash
python populate_locations.py
```

### 3. Initialize User Statistics

```bash
python initialize_user_statistics.py
```

### 4. Set Up Birthday Checker (Optional)

Add to crontab for daily birthday checks:

```bash
# Run daily at 1:00 AM
0 1 * * * /path/to/python /path/to/birthday_checker.py
```

## API Usage Examples

### 1. User Location Selection

Users select from predefined provinces and cities:

```python
# Get all provinces
provinces = session.query(Province).all()

# Get cities for a specific province
cities = session.query(City).filter(City.province_id == province_id).all()

# Update user location
user.province_id = selected_province_id
user.city_id = selected_city_id
```

### 2. Birthday and Age Management

```python
from datetime import date

# Set user birthday
user.birthday = date(1990, 5, 15)  # Age will be calculated automatically

# Check if today is user's birthday
if user.is_birthday_today():
    print("Happy Birthday!")

# Get current calculated age
current_age = user.current_age
```

### 3. Statistics Queries

```python
# Get user's project statistics
project_stats = session.query(UserProjectCount).filter(
    UserProjectCount.user_id == user_id
).first()

print(f"Owned: {project_stats.owned_projects}")
print(f"Collaborated: {project_stats.collaborated_projects}")
print(f"Total: {project_stats.total_projects}")

# Get user's institution statistics
institution_stats = session.query(UserInstitutionCount).filter(
    UserInstitutionCount.user_id == user_id
).first()
```

### 4. Institution Management

```python
# Create an institution
institution = Institution(
    name="Beijing University",
    name_en="Beijing University", 
    type="university",
    city_id=1,  # Beijing
    province_id=1  # Beijing Municipality
)

# Link user to institution
user_institution = UserInstitution(
    user_id=user_id,
    institution_id=institution.id,
    role="student",
    position="Computer Science Major",
    is_current=1
)
```

## Model Relationships

### User Model New Relationships

```python
# Location relationships
user.province  # Province object
user.city      # City object

# Statistics relationships  
user.project_count     # UserProjectCount object
user.institution_count # UserInstitutionCount object

# Institution relationships
user.user_institutions # List of UserInstitution objects
```

### Location Relationships

```python
# Province to cities
province.cities  # List of City objects
province.users   # List of User objects

# City to province and users
city.province    # Province object
city.users       # List of User objects
```

## Data Integrity

The system maintains data integrity through:

1. **Foreign Key Constraints**: Ensure valid references between tables
2. **Triggers**: Automatically update statistics and age calculations
3. **Unique Constraints**: Prevent duplicate statistics records
4. **Default Values**: Provide sensible defaults for new records

## Performance Considerations

1. **Indexes**: Created on primary keys and foreign keys
2. **Efficient Queries**: Use joins to minimize database calls
3. **Batch Updates**: Birthday checker processes all users at once
4. **Cached Calculations**: Age stored as column rather than calculated each time

## Backward Compatibility

The update maintains backward compatibility:

1. **Legacy Location Fields**: Old city/state fields preserved
2. **Property Methods**: Old age property still works
3. **Fallback Logic**: Location property checks new structure first, then legacy

This ensures existing code continues to work while new features are available.