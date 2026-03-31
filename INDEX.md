# Automation Tool - Complete Project Index

## Start Here

**New to this project?** Start with these in order:

1. **[README.md](./README.md)** - 5 minute overview
2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick cheat sheet
3. **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Detailed setup (30 minutes)

## Documentation Map

### Overview Documents
- **[README.md](./README.md)** - Project overview, features, quick start
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - Architecture, technology stack, roadmap
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Cheat sheet for quick lookup
- **[DELIVERABLES.md](./DELIVERABLES.md)** - Complete checklist of what's included

### Detailed Guides
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete setup and usage guide
- **[AUTOMATION_TOOL_README.md](./AUTOMATION_TOOL_README.md)** - Python app detailed reference
- **[INDEX.md](./INDEX.md)** - This file

## Python Application Files

### Core Files (Start Here)
- **[main.py](./main.py)** - Entry point
  - Application launcher
  - Logging setup
  - Dependency checks

### Main Application
- **[gui.py](./gui.py)** - Main UI and components
  - MainWindow class
  - AuthPanel for login
  - OperationsList sidebar
  - ActionListFrame for actions
  - ActionBuilder dialog
  - Execution monitoring

- **[automation_engine.py](./automation_engine.py)** - Core automation
  - ActionType enum
  - Action dataclass
  - AutomationEngine class
  - Action execution (click, type, wait, screenshot)
  - Workflow management
  - Pause/resume/stop controls

### Integration & Tools
- **[supabase_client.py](./supabase_client.py)** - Database integration
  - SupabaseManager class
  - Authentication
  - Operation CRUD
  - Action management
  - Execution logging

- **[coordinate_picker.py](./coordinate_picker.py)** - Visual tools
  - CoordinatePicker class
  - Global mouse listener
  - Preview with crosshair
  - PickerDialog component

### Configuration
- **[requirements.txt](./requirements.txt)** - Python dependencies
  - pyautogui for automation
  - customtkinter for GUI
  - supabase-py for backend
  - pynput for input monitoring
  - pillow for image handling

## React Web Dashboard Files

### Main Application
- **[src/App.tsx](./src/App.tsx)** - Main React component
  - Authentication state
  - Operation management
  - Component routing
  - Supabase client initialization

### Components
- **[src/components/AuthPanel.tsx](./src/components/AuthPanel.tsx)**
  - Sign in interface
  - Registration form
  - Error handling
  - Mode toggle

- **[src/components/OperationsList.tsx](./src/components/OperationsList.tsx)**
  - Operation list sidebar
  - Create new operation
  - Delete operation
  - Select operation

- **[src/components/OperationEditor.tsx](./src/components/OperationEditor.tsx)**
  - Edit operation details
  - Add/delete actions
  - Action configuration forms
  - Save changes
  - Execute button

- **[src/components/ExecutionMonitor.tsx](./src/components/ExecutionMonitor.tsx)**
  - Batch input
  - Execution logs
  - Statistics display
  - Real-time status

### Entry Points
- **[src/main.tsx](./src/main.tsx)** - React entry point
- **[src/index.css](./src/index.css)** - Tailwind styles

## Configuration Files

### Application Configuration
- **[.env](./.env)** - Environment variables
  - VITE_SUPABASE_URL
  - VITE_SUPABASE_ANON_KEY

### Build Configuration
- **[vite.config.ts](./vite.config.ts)** - Vite build config
- **[tailwind.config.js](./tailwind.config.js)** - Tailwind CSS setup
- **[package.json](./package.json)** - Node.js dependencies

### TypeScript Configuration
- **[tsconfig.json](./tsconfig.json)** - Base TypeScript config
- **[tsconfig.app.json](./tsconfig.app.json)** - App-specific config
- **[tsconfig.node.json](./tsconfig.node.json)** - Build-specific config

## Database Schema

### Tables Created (via migration)
All stored in Supabase PostgreSQL:

1. **automation_operations** - Operation definitions
   - id, user_id, name, description
   - created_at, updated_at
   - RLS: User ownership

2. **operation_actions** - Individual actions
   - id, operation_id, order
   - action_type, config
   - RLS: Through operation ownership

3. **execution_logs** - Execution history
   - id, operation_id, user_id
   - batch_item, status
   - error_message, timestamps
   - RLS: User and operation checks

## How Files Work Together

```
User starts application
         ↓
main.py (entry point)
         ↓
gui.py (UI initialization)
         ├→ supabase_client.py (authentication)
         ├→ automation_engine.py (setup)
         └→ coordinate_picker.py (initialization)
         ↓
User interactions
         ├→ Create operation → supabase_client saves
         ├→ Add actions → automation_engine stores
         ├→ Pick coordinates → coordinate_picker
         └→ Execute → automation_engine runs
         ↓
Results logged to Supabase (execution_logs)
         ↓
Web dashboard (React) reads live updates
```

## File Size Reference

| File | Size | Purpose |
|------|------|---------|
| gui.py | 27 KB | Main UI (1000+ lines) |
| OperationEditor.tsx | 12 KB | Action editor |
| SETUP_GUIDE.md | 12 KB | Setup documentation |
| PROJECT_SUMMARY.md | 13 KB | Architecture docs |
| supabase_client.py | 7.5 KB | Database integration |
| AUTOMATION_TOOL_README.md | 7.9 KB | Python guide |
| coordinate_picker.py | 7.3 KB | Coordinate picker |
| ExecutionMonitor.tsx | 6.7 KB | Monitor UI |
| App.tsx | 6.0 KB | Main React component |
| AuthPanel.tsx | 5.7 KB | Auth UI |
| automation_engine.py | 5.4 KB | Core automation |
| OperationsList.tsx | 4.5 KB | List UI |
| README.md | 4 KB | Overview |
| main.py | 901 bytes | Entry point |
| requirements.txt | 161 bytes | Dependencies |

## How to Navigate This Project

### I want to...

**...get started immediately**
→ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

**...set up the application**
→ [SETUP_GUIDE.md](./SETUP_GUIDE.md)

**...understand the architecture**
→ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)

**...use the Python desktop app**
→ [AUTOMATION_TOOL_README.md](./AUTOMATION_TOOL_README.md)

**...deploy the web dashboard**
→ See "Deployment" in [SETUP_GUIDE.md](./SETUP_GUIDE.md#deployment)

**...debug an issue**
→ See "Troubleshooting" in relevant guide

**...extend the system**
→ See "Extending" in [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md#extending-the-system)

**...see what's included**
→ [DELIVERABLES.md](./DELIVERABLES.md)

## Execution Flow Diagram

```
┌─────────────────────────────────────────────────┐
│  User (Desktop App or Web Dashboard)            │
└──────────────┬──────────────────────────────────┘
               │
               ├─→ Create Operation
               │   └─→ supabase_client.save_operation()
               │       └─→ Supabase DB
               │
               ├─→ Add Actions
               │   └─→ supabase_client.update_operation()
               │       └─→ Supabase DB
               │
               ├─→ Pick Coordinates
               │   └─→ coordinate_picker
               │       └─→ Get mouse position
               │
               └─→ Execute Batch
                   ├─→ Load operation from DB
                   ├─→ Load actions from DB
                   ├─→ For each batch item:
                   │   ├─→ automation_engine.execute_workflow()
                   │   ├─→ Execute each action:
                   │   │   ├─→ Click at X, Y
                   │   │   ├─→ Type {item} text
                   │   │   ├─→ Wait N seconds
                   │   │   └─→ Screenshot
                   │   └─→ Log result to DB
                   └─→ Display status to user
```

## Key Classes & Functions

### Python Application

**automation_engine.py**
- `AutomationEngine` - Main automation class
  - `load_actions()` - Load action sequence
  - `execute_workflow()` - Run all actions
  - `execute_action()` - Run single action
  - `pause()`, `resume()`, `stop()` - Control

**supabase_client.py**
- `SupabaseManager` - Database integration
  - `sign_in()`, `sign_up()` - Auth
  - `save_operation()` - Create operation
  - `get_operation_with_actions()` - Load
  - `log_execution()` - Track execution

**gui.py**
- `MainWindow` - Application window
- `OperationsList` - Operation list UI
- `ActionListFrame` - Action list display
- `ActionBuilder` - Action creation dialog
- `CoordinatePicker` - Visual picker

### React Application

**App.tsx**
- `App` - Main component
  - `checkAuth()` - Verify login
  - `loadOperations()` - Fetch from DB
  - `handleOperationSaved()` - Update list

**Components**
- `AuthPanel` - Login screen
- `OperationsList` - Operation list
- `OperationEditor` - Edit operation
- `ExecutionMonitor` - Track execution

## Dependencies

### Python (9 packages)
- pyautogui, pillow, pynput - Automation
- customtkinter - GUI
- supabase, postgrest-py - Backend
- python-dotenv - Configuration

### Node.js (15+ packages)
- react, react-dom - UI framework
- @supabase/supabase-js - Backend
- tailwindcss - Styling
- vite - Build tool
- lucide-react - Icons
- typescript - Type checking

## Environment Setup

Required environment variables (in .env):
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...your_key...
```

These are already configured!

## Version Information

- Python: 3.8+
- Node.js: 16+
- React: 18.3.1
- TypeScript: 5.5.3
- Vite: 5.4.2
- Tailwind: 3.4.1

## License & Usage

This is a production-ready automation platform. All files are included and ready to use.

## Next Steps

1. **Read**: [README.md](./README.md)
2. **Setup**: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
3. **Reference**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
4. **Run**: `python main.py` or `npm run dev`
5. **Create**: Your first automation operation
6. **Execute**: A batch of items
7. **Celebrate**: Your first successful automation!

---

**Last Updated**: March 2024
**Status**: Production Ready
**All Files**: Included & Complete
