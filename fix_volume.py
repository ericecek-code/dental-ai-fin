import modal
import os
import shutil

volume = modal.Volume.from_name('dentex-dataset')

app = modal.App("fix-dentex-volume")

@app.function(volumes={'/data': volume})
def move_files():
    # Move contents of /data/dentex to /data/
    src = '/data/dentex'
    dst = '/data'
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.move(s, d)
        print(f'Moved {s} -> {d}')
    
    # Remove empty dentex dir
    os.rmdir(src)
    print('Done moving files')
    
    # Verify
    print('New structure:')
    for root, dirs, files in os.walk('/data'):
        level = root.replace('/data', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:
            print(f'{subindent}{file}')

@app.local_entrypoint()
def main():
    print("Starting volume fix...")
    move_files.remote()
    print("Volume fix complete!")