# Automation Tool - Batch Automation for Repetitive Software Operations

A modern Python application that automates repetitive software operations. Define reusable workflows with point-and-click actions, then execute them in batch mode with multiple search terms.

## Features

- **Operation Builder**: Create named workflows with multiple sequential actions
- **Visual Coordinate Picker**: Point-and-click interface to capture exact screen coordinates
- **Batch Processing**: Execute operations on multiple items (search terms) in one go
- **Action Types**:
  - Click at specific coordinates
  - Type text with placeholder support
  - Wait/pause between actions
  - Screenshot capture
- **Modern GUI**: Beautiful, intuitive interface using customtkinter
- **Cloud Sync**: Save and load operations using Supabase
- **Execution Controls**: Start, pause, resume, and stop batch operations
- **Logging**: Track execution progress and errors

## Installation

### Prerequisites
- Python 3.8+
- Pip (Python package manager)

### Setup Steps

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Supabase** (optional, for cloud sync):
   - Ensure your `.env` file has valid Supabase credentials:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

3. **Run the application**:
```bash
python main.py
```

## Usage Guide

### Creating a New Operation

1. Click **"+ New Operation"** in the sidebar
2. Enter operation name and description
3. Add actions by clicking **"+ Add Action"** button
4. For each action:
   - Select action type (Click, Type, Wait, Screenshot)
   - Configure action settings
   - For Click actions, use "📍 Pick from Screen" to capture coordinates visually
5. Click **"💾 Save Operation"** to save (requires Supabase login)

### Action Types

#### Click Action
- Click at a specific screen coordinate
- Configure: X position, Y position, number of clicks, mouse button
- Use coordinate picker to visually select where to click

#### Type Action
- Type text into the current field
- Supports `{item}` placeholder for batch items
- Example: "Search for {item}" will be replaced with each batch item

#### Wait Action
- Pause execution for specified duration
- Useful for waiting for interface to respond
- Configure: duration in seconds

#### Screenshot Action
- Capture screen and save to file
- Configure: filename for saved image
- Useful for debugging or verification

### Batch Execution

1. Click on an existing operation to load it
2. Enter items to process in the **"Batch Items"** text area (one per line)
3. Click **"▶ Execute"** to start batch processing
4. Monitor progress in the status bar
5. Use **"⏸ Pause"** and **"⏹ Stop"** buttons to control execution

### Example Workflow

To automate searching a software tool:

1. **Create operation "Search Items"**
2. **Add actions**:
   - Click at search box location (550, 300)
   - Type "{item}"
   - Click search button (750, 300)
   - Wait 2 seconds
   - Click results to view
3. **Save operation**
4. **Enter batch items**:
   ```
   apple
   banana
   orange
   ```
5. **Execute** - the tool automatically searches for each item

## Database Schema

Operations are stored in Supabase with the following structure:

### automation_operations
- `id`: Unique operation identifier
- `user_id`: Owner's user ID
- `name`: Operation name
- `description`: Operation description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### operation_actions
- `id`: Action identifier
- `operation_id`: Reference to parent operation
- `order`: Action sequence number
- `action_type`: Type of action (click, type, wait, screenshot)
- `config`: JSON configuration for action

### execution_logs
- `id`: Log entry identifier
- `operation_id`: Reference to executed operation
- `user_id`: User who ran operation
- `batch_item`: The item that was processed
- `status`: Execution status (pending, running, success, error)
- `error_message`: Error details if failed
- `started_at`: Execution start time
- `completed_at`: Execution end time

## Architecture

### Core Components

**automation_engine.py**
- Executes actions using pyautogui
- Manages workflow execution
- Handles pause/resume functionality
- Supports context variables for batch processing

**supabase_client.py**
- Manages authentication
- Performs CRUD operations on operations and actions
- Logs execution history
- Syncs data to cloud

**coordinate_picker.py**
- Visual tool for capturing screen coordinates
- Shows real-time cursor position with preview
- Global mouse listener for point-and-click selection

**gui.py**
- Modern UI using customtkinter framework
- Operation management (create, edit, delete, load)
- Action builder with configuration forms
- Batch item input and execution controls
- Real-time status updates

**main.py**
- Application entry point
- Initializes logging and starts GUI

## Safety Features

- **Fail-safe**: Move cursor to screen corner to instantly stop execution
- **Execution delays**: Built-in pauses between actions to allow system response
- **Error handling**: Comprehensive error logging and recovery
- **Pause/Resume**: Control execution flow without losing progress
- **Screen bounds checking**: Validates coordinates are within screen size

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed: `python --version`
- Install all dependencies: `pip install -r requirements.txt`
- Check `.env` file exists and is readable

### Supabase connection fails
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in `.env`
- Check internet connection
- Verify Supabase project is active

### Coordinate picker not working
- Ensure pynput is installed: `pip install pynput`
- Try running with administrator privileges
- Check for screen display issues

### Actions not executing
- Verify target application is visible and in focus
- Check coordinate values are correct (use picker tool)
- Add wait actions between fast operations
- Review execution logs for errors

### Batch execution too fast
- Add wait actions between operations
- Increase wait duration if interface lags

## Advanced Usage

### Multiple Actions in Sequence
Operations can contain many actions. They execute in order:
1. Click to focus window
2. Type search query
3. Wait for results
4. Click result item
5. Take screenshot for verification

### Placeholder Variables
Use `{item}` in type actions to insert batch items:
- Text: "Search for {item} in database"
- Result: "Search for apple in database", "Search for banana in database", etc.

### File Import
Batch items can be:
- Pasted directly in text area
- Imported from text files (one item per line)
- CSV files (use appropriate parsing)

### Screenshot Verification
- Take screenshots at key points
- Review output files to verify automation worked correctly
- Useful for debugging

## Performance Tips

1. **Add appropriate waits**: Prevent actions before interface is ready
2. **Use specific coordinates**: More precise than image recognition
3. **Batch similar items**: Group related searches for efficiency
4. **Test with small batches**: Verify operation before processing large batches
5. **Monitor first execution**: Watch initial run to ensure proper timing

## Security Notes

- Credentials stored in `.env` file (not in code)
- Supabase RLS policies restrict data access to authenticated users
- Sensitive operations (type, click) logged with minimal details
- Screenshots saved locally by default

## System Requirements

- **OS**: Windows, macOS, Linux
- **Python**: 3.8 or higher
- **RAM**: 512 MB minimum
- **Display**: 1024x768 or higher resolution
- **Network**: Required for Supabase sync (optional for local-only use)

## License

Copyright 2024. All rights reserved.

## Support

For issues or questions:
1. Check troubleshooting section
2. Review execution logs
3. Verify configuration in `.env`
4. Test coordinate picker independently
