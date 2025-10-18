# Ques Backend Documentation

## 📁 Documentation Structure

### 🧪 Testing (`../tests/`)
- **`database/`** - Database verification and checking scripts
  - `check_db_state.py` - Database state verification
  - `check_new_tables.py` - New tables validation
  - `check_user_swipes.py` - User swipes table verification
  - `verify_chat_tables.py` - Chat system tables verification

- **`integration/`** - Integration testing scripts
  - `test_api_endpoints.py` - API endpoints testing
  - `test_chat_integration.py` - Chat system integration tests
  - `test_final_integration.py` - Complete system integration tests
  - `test_tpns_integration.py` - TPNS integration testing

### 📚 API Documentation (`api/`)
- `api_specification.yaml` - Complete OpenAPI/Swagger specification
- `AVAILABLE_API_ENDPOINTS.md` - List of all available endpoints
- `BACKEND_SERVICE_ENDPOINT_MAPPING.md` - Service to endpoint mapping
- `CURRENT_API_ENDPOINTS_STATUS.md` - Endpoint status and health

### 🔧 Implementation Guides (`implementation/`)
- `CHAT_SYSTEM_COMPLETE.md` - Chat system implementation details
- `NEW_SWIPE_SYSTEM_IMPLEMENTATION.md` - Swipe mechanics implementation
- `PAYMENT_SYSTEM_IMPLEMENTATION_COMPLETE.md` - Payment system guide
- `PROJECT_MANAGEMENT_IMPLEMENTATION.md` - Project management features
- `TPNS_IMPLEMENTATION_SUMMARY.md` - Push notification system

### 📊 Analysis Reports (`analysis/`)
- `INTEGRATION_ANALYSIS.md` - System integration analysis
- `PAYMENT_AND_MATCHING_ANALYSIS.md` - Payment and matching logic analysis
- `UNIVERSITY_VERIFICATION_ANALYSIS.md` - University verification system
- `FRONTEND_API_REQUIREMENTS_ANALYSIS.md` - Frontend integration requirements

### 🛠️ Maintenance (`maintenance/`)
- `CLEANUP_SUMMARY.md` - System cleanup and maintenance guide

## � Quick Start

### For Developers
1. **API Documentation**: Start with `api/api_specification.yaml`
2. **Implementation**: Check `implementation/` for system guides
3. **Testing**: Use scripts in `../tests/` for verification

### For Frontend Developers
1. **API Spec**: `api/api_specification.yaml` - Complete endpoint documentation
2. **Requirements**: `analysis/FRONTEND_API_REQUIREMENTS_ANALYSIS.md`
3. **Integration**: Follow authentication and data model patterns in API spec

### For DevOps/Testing
1. **Database Tests**: `../tests/database/` - Verify database integrity
2. **Integration Tests**: `../tests/integration/` - End-to-end testing
3. **Maintenance**: `maintenance/` - System cleanup guides

## 📋 Key Features Documented

- ✅ **AI-Powered Chat System** with intelligent user recommendations
- ✅ **Swipe Mechanics** with advanced analytics
- ✅ **Payment System** with subscription management
- ✅ **Push Notifications** via TPNS integration
- ✅ **User Authentication** with JWT tokens
- ✅ **University Verification** system
- ✅ **Project Management** features

## 🔗 Related Files

- **Main Application**: `../main.py`
- **Database Models**: `../models/`
- **API Routers**: `../routers/`
- **Services**: `../services/`
- **Configuration**: `../config/`

---

*Last Updated: October 17, 2025*
*Documentation organized for better maintainability and clarity*
4. Place general guides and architecture in `/guides`
5. Update this index file with new content