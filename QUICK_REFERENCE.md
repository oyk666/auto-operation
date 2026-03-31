# Automation Tool - Quick Reference Card

## Getting Started (5 Minutes)

### Python Desktop App
```bash
pip install -r requirements.txt
python main.py
```

### Web Dashboard
```bash
npm run dev
# Open http://localhost:5173
```

## Main Concepts

### Operation
A named workflow with multiple actions that execute in sequence.

### Action
Individual task: click at coordinates, type text, wait, or screenshot.

### Batch Item
A value that gets substituted into `{item}` placeholders during execution.

## Creating Your First Operation

1. **Name it** - Give your operation a meaningful name
2. **Add actions** - Click "Add Action" and choose type
3. **Configure** - Set coordinates, text, duration, etc.
4. **Save** - Click "Save Operation"
5. **Execute** - Enter batch items and click "Execute"

## Action Types Cheat Sheet

| Type | Use Case | Config |
|------|----------|--------|
| **Click** | Buttons, links, menus | X, Y coordinates |
| **Type** | Input fields, search | Text (supports {item}) |
| **Wait** | Load time, animations | Duration (seconds) |
| **Screenshot** | Verify, document | Filename |

## Coordinate Picker

1. Click "📍 Pick from Screen" button
2. Click anywhere on your screen
3. Coordinates auto-filled
4. Done!

## Batch Processing

```
Item 1
Item 2
Item 3
```

Each item replaces `{item}` in type actions and screenshot filenames.

## Example: Quick Search

**Operation: "Search Database"**

```
1. Click (550, 300)           # Focus search box
2. Type "{item}"              # Enter search term
3. Click (750, 300)           # Click search
4. Wait 2                      # Let results load
5. Screenshot "result.png"    # Save result
```

**Batch Items:**
```
apple
banana
orange
```

**Result:** Searches 3 items automatically.

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| App won't start | `pip install -r requirements.txt` |
| Coordinates wrong | Use coordinate picker (📍 button) |
| Too fast | Add wait actions between operations |
| Can't pick coordinates | Run as administrator |
| Supabase won't connect | Check .env file and internet |
| Web dashboard blank | Clear browser cache (Ctrl+Shift+Del) |

## File Locations

| File | Purpose |
|------|---------|
| `main.py` | Desktop app launcher |
| `gui.py` | Desktop app interface |
| `automation_engine.py` | Core automation logic |
| `supabase_client.py` | Cloud database |
| `src/App.tsx` | Web dashboard |
| `.env` | Configuration (Supabase) |

## Keyboard Shortcuts (Desktop)

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New operation |
| `Ctrl+S` | Save operation |
| `Ctrl+E` | Execute batch |
| `Esc` | Close dialog |

## Directory Structure

```
Project Root
├── main.py                    # Start here
├── gui.py                     # Desktop UI
├── automation_engine.py       # Automation
├── supabase_client.py         # Database
├── coordinate_picker.py       # Picker tool
├── requirements.txt           # Python deps
├── src/
│   ├── App.tsx                # Web app
│   ├── components/            # Web components
│   └── main.tsx               # Web entry
├── .env                       # Config
├── package.json               # Node deps
├── tailwind.config.js         # CSS config
└── vite.config.ts             # Build config
```

## Status Icons

| Icon | Meaning |
|------|---------|
| 🟢 | Success |
| 🔴 | Error |
| 🟡 | Pending |
| ⏳ | Running |
| ⏸ | Paused |

## Tips & Tricks

### Faster Execution
- Reduce wait duration
- Remove unnecessary screenshots
- Use smaller batches for testing

### More Reliable
- Add waits between operations
- Use coordinate picker (not manual entry)
- Test with small batch first

### Better Organization
- Use descriptive operation names
- Add detailed descriptions
- Group related operations

### Debugging
- Take screenshots at key points
- Check execution logs
- Test operation manually first
- Watch first execution

## Performance

| Metric | Value |
|--------|-------|
| App startup | < 2 seconds |
| Action execution | 100-500ms |
| Web sync | < 2 seconds |
| Max batch size | 1000 items |
| Max actions/op | 500 |

## Security

✓ Credentials in .env
✓ No hardcoded secrets
✓ RLS on database
✓ User-owned data only
✓ Secure authentication

## Action Configuration Guide

### Click Action
```
X: 550          # Horizontal position
Y: 300          # Vertical position
Clicks: 1       # Number of clicks
Button: left    # left/right/middle
```

### Type Action
```
Text: "Search {item}"
# {item} gets replaced with batch item
```

### Wait Action
```
Duration: 2     # Seconds to wait
# Can be decimal: 0.5, 1.5, etc.
```

### Screenshot Action
```
Filename: "result_{item}.png"
# {item} can be used in filename
```

## Database Tables

### automation_operations
Stores operation definitions
- name, description
- created_at, updated_at

### operation_actions
Stores individual actions
- action_type, config, order

### execution_logs
Tracks execution history
- status, error_message, timestamps

## Getting Help

1. **Documentation**: Read SETUP_GUIDE.md
2. **Architecture**: See PROJECT_SUMMARY.md
3. **Python app**: Check AUTOMATION_TOOL_README.md
4. **Errors**: Check execution logs
5. **Database**: Check Supabase dashboard

## Links & Resources

- Supabase: https://supabase.io
- pyautogui Docs: https://pyautogui.readthedocs.io
- React: https://react.dev
- Tailwind: https://tailwindcss.com

## Production Checklist

- [ ] Test with 50+ items
- [ ] Verify error handling
- [ ] Check coordinate accuracy
- [ ] Review security settings
- [ ] Set up backups
- [ ] Train team
- [ ] Document operations
- [ ] Monitor first run

## One-Command Start

**Desktop**: `python main.py`
**Web**: `npm run dev`
**Build Web**: `npm run build`

---

**Pro Tip**: Start small, test thoroughly, then scale!
