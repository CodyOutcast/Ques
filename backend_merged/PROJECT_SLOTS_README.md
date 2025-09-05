# Project Slots System

A comprehensive slot-based project management system with membership integration for the Questrial platform.

## Overview

The Project Slots System allows users to manage their project cards in dedicated slots with activation/deactivation functionality. The system integrates with membership tiers to provide different slot allowances.

## Features

- **Slot-Based Management**: Users manage projects in dedicated slots (2 for basic users, 10 for premium)
- **Activation System**: Projects can be activated/deactivated within slots (no separate publishing)
- **Membership Integration**: Automatic slot allocation based on membership level
- **Expiration Handling**: Premium slots automatically reduce to basic level when membership expires
- **AI Recommendations**: Save AI-recommended projects directly to slots
- **Admin Dashboard**: Administrative tools for slot system management

## Architecture

### Models

#### ProjectCardSlot
Main slot entity that holds project information:
- **Status**: EMPTY → OCCUPIED → ACTIVATED lifecycle
- **Content**: Project details (title, description, images, etc.)
- **Metadata**: AI recommendation data, activation timestamps

#### UserSlotConfiguration  
User-specific slot settings:
- **Base Slots**: Always 2 for all users
- **Bonus Slots**: 8 additional for premium users (total 10)
- **Membership Tracking**: Expiration dates and permanent status

#### AIRecommendationSwipe
Tracks user interactions with AI recommendations:
- **Swipe Direction**: LEFT (dislike) or RIGHT (like)
- **Auto-Save**: Automatic slot saving for right swipes

### Services

#### ProjectSlotsService
Core business logic:
- Slot lifecycle management (create, fill, activate, deactivate)
- Membership-aware slot allocation
- AI recommendation integration
- Statistics and reporting

#### MembershipSlotIntegrationService
Membership integration:
- Handle membership upgrades/downgrades
- Process subscription purchases/cancellations
- Automatic expiration handling
- Webhook event processing

#### TaskSchedulerService
Background task management:
- Daily membership expiration checks
- Cleanup of expired slots
- Scheduled maintenance tasks

## API Endpoints

### User Endpoints
```
GET    /slots                    # Get user's slots
POST   /slots                    # Create new slot
GET    /slots/{id}               # Get specific slot
PUT    /slots/{id}               # Update slot
DELETE /slots/{id}               # Delete slot
POST   /slots/{id}/activate      # Activate slot
POST   /slots/{id}/deactivate    # Deactivate slot
GET    /slots/statistics         # Get slot statistics
POST   /ai-recommendations/swipe # Swipe on AI recommendation
```

### Admin Endpoints
```
GET    /admin/slots/statistics/global           # Global slot statistics
GET    /admin/slots/users/{id}/info             # User slot information
POST   /admin/slots/membership/check            # Manual membership check
POST   /admin/slots/users/{id}/membership/update # Update user membership
GET    /admin/slots/users/with-active-memberships # List premium users
POST   /admin/slots/maintenance/clean-expired-slots # Cleanup expired slots
```

### Webhook Endpoints
```
POST   /webhooks/membership/change    # Handle membership changes
POST   /webhooks/membership/purchase  # Handle membership purchases
POST   /webhooks/membership/cancel    # Handle membership cancellations
GET    /webhooks/membership/health    # Webhook health check
```

## Usage Examples

### Basic User Flow
1. User signs up → Gets 2 basic slots
2. User saves AI recommendation → Fills slot (status: OCCUPIED)
3. User activates slot → Project visible publicly (status: ACTIVATED)
4. User deactivates → Project hidden but stays in slot (status: OCCUPIED)

### Premium User Flow
1. User purchases premium membership → Gets 10 slots total (2 base + 8 bonus)
2. User can fill and activate up to 10 projects
3. Membership expires → Automatically reduced to 2 slots, excess slots deactivated

### AI Recommendation Integration
```python
# User swipes right on AI recommendation
response = await swipe_ai_recommendation(
    recommendation_id="rec_123",
    direction="RIGHT",
    auto_save=True  # Automatically saves to next available slot
)
```

### Slot Activation
```python
# Activate a slot to make project public
response = await activate_slot(slot_id=456)
# Project becomes visible in public listings

# Deactivate slot to hide project
response = await deactivate_slot(slot_id=456) 
# Project hidden but remains in slot
```

## Membership Integration

### Slot Allocation Rules
- **Basic Users**: 2 slots total
- **Premium Users**: 10 slots total (2 base + 8 bonus)
- **Expired Premium**: Automatically reduced to 2 slots

### Membership Events
The system responds to membership service events:
- **Upgrade**: Increase slot allocation
- **Downgrade**: Reduce slots, deactivate excess
- **Purchase**: Grant bonus slots with expiration
- **Cancel**: Mark for expiration at end date
- **Expire**: Reduce to basic slot allocation

### Webhook Integration
```python
# Membership service sends webhook on changes
{
    "user_id": 123,
    "event_type": "upgrade",
    "old_membership": "basic",
    "new_membership": "pro",
    "subscription_end_date": "2024-12-31T23:59:59Z"
}
```

## Database Schema

### Migrations
- **20250905_1200_project_slots.py**: Creates slot system tables with membership support

### Key Tables
```sql
-- Project slots with activation tracking
project_card_slots (
    slot_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    slot_number INTEGER,
    status slot_status_enum,
    is_activated BOOLEAN DEFAULT FALSE,
    activated_at TIMESTAMP,
    -- ... project content fields
)

-- User slot configurations with membership
user_slot_configurations (
    config_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    base_slots INTEGER DEFAULT 2,
    bonus_slots INTEGER DEFAULT 0,
    bonus_expires_at TIMESTAMP,
    permanent BOOLEAN DEFAULT FALSE
)

-- AI recommendation interactions
ai_recommendation_swipes (
    swipe_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recommendation_id VARCHAR,
    direction swipe_direction_enum,
    saved_to_slot INTEGER REFERENCES project_card_slots(slot_id)
)
```

## Background Tasks

### Daily Membership Check
Runs at 2 AM daily to:
- Check for expired premium memberships
- Reduce slots from 10 to 2 for expired users  
- Deactivate excess slots (keeps newest activated slots)
- Log expiration activities

### Manual Admin Tasks
- Immediate membership expiration check
- Bulk slot cleanup operations
- User membership slot updates
- System statistics generation

## Configuration

### Environment Variables
```bash
# Database connection (standard)
PG_USER=questrial_user
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=questrial

# Slot system settings
DEFAULT_BASE_SLOTS=2
PREMIUM_BONUS_SLOTS=8
AI_RECOMMENDATION_AUTO_SAVE=true
```

### Service Dependencies
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Membership Service**: For membership status and changes
- **AI Recommendation Service**: For recommendation data
- **Background Tasks**: asyncio-based task scheduler

## Testing

### Unit Tests
Test individual service methods:
```python
def test_activate_slot():
    # Test slot activation
    pass

def test_membership_expiration():
    # Test membership expiration handling
    pass
```

### Integration Tests  
Test end-to-end workflows:
```python
def test_membership_upgrade_flow():
    # Test complete membership upgrade process
    pass

def test_ai_recommendation_save_flow():
    # Test AI recommendation to slot saving
    pass
```

## Monitoring

### Key Metrics
- Slot utilization rates
- Activation conversion rates  
- Membership expiration impact
- AI recommendation save rates

### Logging
- Membership change events
- Slot activation/deactivation activities
- Background task execution
- Error conditions and recoveries

## Future Enhancements

### Planned Features
- **Slot Templates**: Pre-configured slot layouts
- **Slot Sharing**: Collaborative slot management
- **Advanced Analytics**: Detailed slot performance metrics
- **Bulk Operations**: Mass slot management tools

### Scalability Considerations
- Slot archiving for inactive users
- Database partitioning for large slot counts
- Caching layer for slot statistics
- Event-driven architecture for real-time updates

## Support

### Common Issues
1. **Slots not updating after membership change**
   - Check webhook delivery and processing logs
   - Verify membership service integration
   - Run manual membership check

2. **AI recommendations not saving to slots**  
   - Verify auto_save configuration
   - Check available slot count
   - Review recommendation service integration

3. **Expired memberships not reducing slots**
   - Check background task scheduler
   - Review expiration date calculations  
   - Run manual cleanup operation

### Contact
For technical support or questions about the slot system implementation, contact the development team.
