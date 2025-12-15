# Icon File Setup

## You need an icon file (.ico) for your executable

### Option 1: Use an Existing Icon

If you have a logo/image:

1. **Convert to .ico format:**
   - Online: https://convertio.co/png-ico/
   - Or: https://www.icoconverter.com/

2. **Save as `icon.ico`** in this folder

3. **Recommended size:** 256x256 pixels

### Option 2: Download a Free Icon

Free icon resources:
- https://www.flaticon.com/
- https://icons8.com/
- https://www.iconfinder.com/

### Option 3: Create Your Own

Using GIMP (free):
1. Create/open image (256x256 recommended)
2. File → Export As → filename.ico

### Current Status

- [ ] No icon file yet - will build without custom icon
- [ ] Place your `icon.ico` file here
- [ ] Or edit `ICON_FILE` path in `build_exe.spec`

### Icon Requirements

✅ Format: .ico (not just .png renamed)
✅ Size: 16x16 to 256x256 (256x256 recommended)
✅ Transparency: Supported
✅ File name: `icon.ico` (or update in build_exe.spec)

### Without an Icon

The executable will build successfully with the default Python icon.
You can add a custom icon later and rebuild.
