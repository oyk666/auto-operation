# Complete Setup Guide - Automation Tool

This guide walks you through setting up and using both the Python desktop application and the React web dashboard for the Automation Tool.

## Project Structure

```
project/
├── Python Desktop App (Standalone automation with GUI)
│   ├── main.py                 # Entry point
│   ├── gui.py                  # Main UI using customtkinter
│   ├── automation_engine.py    # Core automation logic
│   ├── supabase_client.py      # Database integration
│   ├── coordinate_picker.py    # Visual coordinate selector
│   ├── requirements.txt        # Python dependencies
│   └── AUTOMATION_TOOL_README.md
│
├── React Web Dashboard (Modern web interface)
│   ├── src/
│   │   ├── App.tsx             # Main React component
│   │   ├── components/
│   │   │   ├── AuthPanel.tsx       # Login/Register
│   │   │   ├── OperationsList.tsx  # Manage operations
│   │   │   ├── OperationEditor.tsx # Edit operations
│   │   │   └── ExecutionMonitor.tsx # Monitor batch jobs
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── Database
│   └── Supabase (PostgreSQL with RLS)
│       ├── automation_operations
│       ├── operation_actions
│       └── execution_logs
```

## Quick Start

### Option 1: Python Desktop Application (Recommended for Power Users)

#### Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment** (already set up in `.env`)

3. **Run the application**:
```bash
python main.py
```

**Features:**
- Real-time screen coordinate picker
- Fast local execution with pyautogui
- Full offline capability (cloud sync optional)
- Professional UI with darkmode support

### Option 2: React Web Dashboard (Recommended for Teams)

#### Installation

1. **Install Node dependencies** (already done):
```bash
npm install
```

2. **Run development server**:
```bash
npm run dev
```

3. **Build for production**:
```bash
npm run build
```

**Features:**
- Cloud synchronization with Supabase
- Access from any device
- Team collaboration (with proper RLS)
- Execution monitoring from dashboard

## Database Setup

The Supabase database is already configured with three tables:

### 1. automation_operations
Stores operation definitions:
- `id`: UUID primary key
- `user_id`: Operation owner
- `name`: Operation name
- `description`: What the operation does
- `created_at`: Creation timestamp
- `updated_at`: Last modification

### 2. operation_actions
Stores individual actions within operations:
- `id`: UUID primary key
- `operation_id`: Parent operation FK
- `order`: Execution sequence number
- `action_type`: 'click', 'type', 'wait', 'screenshot'
- `config`: JSON configuration

### 3. execution_logs
Tracks execution history:
- `id`: UUID primary key
- `operation_id`: Which operation was executed
- `user_id`: Who ran it
- `batch_item`: What item was processed
- `status`: 'pending', 'running', 'success', 'error'
- `error_message`: Error details if failed
- `started_at`: Execution start time
- `completed_at`: Execution end time

## Authentication

Both applications use Supabase's built-in authentication:

### Sign Up / Sign In
- Enter email and password
- If account doesn't exist, it will be created
- No email verification required (disabled by default)
- Session persists across browser refreshes

### API Key Security
- Credentials stored in `.env` (never in code)
- RLS policies restrict data access to authenticated users
- Each user can only see/modify their own operations

## Using the Python Desktop App

### Creating Your First Operation

1. **Launch the app**: `python main.py`

2. **Sign in** with your email and password

3. **Click "New Operation"** and enter:
   - Operation name (e.g., "Search Database")
   - Description (e.g., "Searches our database for items")

4. **Add actions** by clicking "Add Action":

   **Click Action:**
   - Click "Pick from Screen" to visually select coordinates
   - Or manually enter X and Y values
   - Supports multiple clicks and different mouse buttons

   **Type Action:**
   - Enter text to type
   - Use `{item}` placeholder for batch items
   - Example: "Search for {item}" becomes "Search for apple"

   **Wait Action:**
   - Specify duration in seconds
   - Useful for allowing interfaces to respond

   **Screenshot Action:**
   - Capture screen and save to file
   - Useful for verification or debugging

5. **Save Operation** - saves to cloud if logged in

6. **Execute Batch**:
   - Enter search items (one per line)
   - Click "Execute"
   - Watch progress in real-time
   - Use Pause/Resume/Stop as needed

### Example: Automated Search Operation

Create operation "Search Items":

**Actions:**
1. Click at (550, 300) - Focus search box
2. Type "{item}" - Enter the search term
3. Click at (750, 300) - Click search button
4. Wait 2 seconds - Let results load
5. Screenshot "result_{item}.png" - Save result

**Batch execution:**
```
apple
banana
orange
grape
```

**Result:** Automatically searches for all 4 items and saves screenshots

## Using the Web Dashboard

### Access the Dashboard

1. **Development**: Run `npm run dev` and open `http://localhost:5173`
2. **Production**: Build with `npm run build` and deploy the `dist/` folder

### Dashboard Workflow

1. **Sign In** - Use same credentials as desktop app
2. **Create Operation** - Click "New Operation" button
3. **Name & Describe** - Set operation details
4. **Add Actions** - Build your workflow
5. **Save** - Cloud synchronizes automatically
6. **Monitor** - View execution logs in real-time

### Web-Specific Features

- **Live Logs**: See execution status across all devices
- **Team View**: Manage operations accessible to team members
- **History**: View past executions and results
- **Remote Triggering**: Trigger desktop app from web dashboard

## Action Types Reference

### Click
- **Purpose**: Click at specific screen location
- **Config**: x, y coordinates, clicks (1-3), button (left/right/middle)
- **Use Case**: Clicking buttons, dropdown menus, links
- **Tip**: Use coordinate picker for precision

### Type
- **Purpose**: Type text into focused field
- **Config**: Text string (supports `{item}` placeholder)
- **Use Case**: Entering search terms, filling forms
- **Tip**: Add wait action before if field needs time to focus

### Wait
- **Purpose**: Pause execution
- **Config**: Duration in seconds (0.1 - 60)
- **Use Case**: Letting interface load, animations to complete
- **Tip**: Start with 1s, reduce if too slow

### Screenshot
- **Purpose**: Capture and save screen
- **Config**: Output filename
- **Use Case**: Verification, debugging, documentation
- **Tip**: Use `{item}` in filename to differentiate results

## Execution Flow

### Local Execution (Python Desktop)
1. Load operation and actions
2. For each batch item:
   - Replace `{item}` placeholders
   - Execute each action in order
   - Handle errors gracefully
   - Log result to database
3. Display summary statistics

### Remote Monitoring (Web Dashboard)
1. Create execution logs in Supabase
2. Desktop app reads queue from database
3. Updates status in real-time
4. Web dashboard shows live progress

## Troubleshooting

### Python App Won't Start
```bash
# Verify Python version
python --version  # Should be 3.8+

# Check dependencies installed
pip list | grep -i "pyautogui\|customtkinter"

# Check Supabase credentials
cat .env  # Should have VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
```

### Web Dashboard Not Loading
```bash
# Clear browser cache and refresh
# Check browser console for errors
# Verify npm dependencies installed
npm install

# Run dev server
npm run dev
```

### Coordinate Picker Not Working
- Ensure application has screen access permissions
- Try running with administrator/sudo privileges
- Verify pynput is installed: `pip show pynput`
- Close and reopen the picker dialog

### Actions Executing Too Fast
- Add wait actions between operations
- Increase wait duration if interface lags
- Check if target application needs more time

### Cloud Sync Not Working
- Verify `.env` has correct Supabase credentials
- Check internet connection
- Verify Supabase project is active
- Check browser console for auth errors

## Performance Tips

1. **Test with small batches first** (5-10 items) before large runs
2. **Add strategic waits** between fast operations
3. **Use specific coordinates** - more reliable than guessing
4. **Take screenshots** at key points to verify
5. **Monitor first execution** - watch to ensure timing is right
6. **Close unnecessary applications** - reduces system load
7. **Run during off-hours** - if operation is slow

## Advanced Usage

### Multiple Operations Workflow
1. Create "Prepare" operation
2. Create "Main" operation
3. Create "Cleanup" operation
4. Execute in sequence with batch items

### Conditional Execution
- Not directly supported yet
- Workaround: Use separate operations

### Custom Delays
- Add "Wait" actions between operations
- Duration can be decimal (0.5, 1.5, etc)

### Batch Item Processing
- Items processed sequentially
- Each iteration replaces `{item}`
- Full error handling and logging
- Can pause/resume at any time

## Security Best Practices

1. **Protect `.env` file** - Contains sensitive credentials
2. **Use strong passwords** - Supabase auth requires secure passwords
3. **Don't share operation files** - May contain sensitive coordinates
4. **Review screenshots** - May contain sensitive information
5. **Monitor execution logs** - Track what operations are running
6. **Use RLS policies** - Data restricted to authenticated users

## Deployment

### Python Desktop App
- Distribute `*.py` files and `requirements.txt`
- Users install dependencies: `pip install -r requirements.txt`
- Users run: `python main.py`

### Web Dashboard
```bash
npm run build
# Deploy `dist/` folder to:
# - Vercel
# - Netlify
# - AWS S3
# - Any static host
```

## Support & Resources

### Python Desktop App
- See `AUTOMATION_TOOL_README.md` for detailed docs
- Check logs for error messages
- Verify Supabase connectivity

### Web Dashboard
- Check browser console for errors (F12)
- Review React DevTools for state
- Inspect network tab for API calls

### Database
- Visit Supabase dashboard
- Check table contents
- Review RLS policies
- Monitor authentication

## Next Steps

1. **Set up your first operation**
2. **Test with 2-3 batch items**
3. **Expand to larger batches**
4. **Share operations with team** (requires RLS updates)
5. **Monitor execution logs**
6. **Optimize timing as needed**

## Frequently Asked Questions

**Q: Can I use this on multiple computers?**
A: Yes! Same account on different computers, operations sync via cloud.

**Q: What if click coordinates change between screens?**
A: You'll need to re-pick coordinates for different screen resolutions.

**Q: Can I edit operations while they're executing?**
A: Not in the current execution, but you can modify them for next run.

**Q: How long can operations be?**
A: No hard limit - test with realistic numbers (10-100 actions typical).

**Q: Is there a rate limit on execution?**
A: No - run as fast as your system can handle (Python app is fastest).

**Q: Can I share operations with team members?**
A: With current setup: No. Future update will add team collaboration via RLS.

**Q: What happens if operation fails mid-batch?**
A: Status is logged, next item in batch continues. You can review logs afterward.

**Q: How do I delete old execution logs?**
A: Use Supabase dashboard → execution_logs table → delete rows manually
