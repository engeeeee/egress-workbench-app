# Shared one-directory runtime: both entry points use the same DLLs and assets.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH)
data = [(str(root / 'containers'), 'containers'), (str(root / 'assets'), 'assets')]
data += collect_data_files('tzdata')
a = Analysis([str(root / 'entry.py')], pathex=[str(root)], binaries=[], datas=data, hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=['PIL', 'cairosvg', 'pytest'])
pyz = PYZ(a.pure)
common = dict(exclude_binaries=True, debug=False, strip=False, upx=False,
              icon=str(root / 'assets/app.ico'), version=str(root / 'version-info.txt'))
gui = EXE(pyz, a.scripts, [], name='EgressWorkbench', console=False, **common)
cli = EXE(pyz, a.scripts, [], name='ewb', console=True, **common)
coll = COLLECT(gui, cli, a.binaries, a.datas, strip=False, upx=False, name='EgressWorkbench')
