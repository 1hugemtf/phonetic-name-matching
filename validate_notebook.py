"""Execute the notebook from scratch and verify the name matching and chart."""
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

root = Path(__file__).resolve().parent
nb = nbformat.read(root / "notebook.ipynb", as_version=4)
nbformat.validate(nb)
for cell in nb.cells:
    if cell.cell_type == "code":
        cell.outputs = []
        cell.execution_count = None
nb.cells.append(nbformat.v4.new_code_cell("""
assert normalize_name(' Élodie ') == 'ELODIE'
assert normalize_name(None) == ''
assert first_token('J.K. Rowling') == ''
assert first_token('J. Smith') == ''
assert first_token('Anne-Marie Smith') == 'ANNEMARIE'
assert first_token('  ') == ''
assert match_status('') == 'Initial or unparseable'
assert match_status('A') == 'Initial or unparseable'
assert match_status('MARY') == 'Exact spelling'
assert len(entries) == 603
assert summary.tolist() == [589, 4, 9, 1]
assert set(t.get_text() for t in fig.legends[0].get_texts()) == set(categories)
assert set(entries['match_status']).issubset(categories)
assert int(summary.sum()) == len(entries)
assert int(yearly.to_numpy().sum()) == len(entries)
assert yearly.sum(axis=1).equals(entries.groupby('Year').size())
assert set(entries.loc[entries.match_status.eq('Exact spelling'), 'first_token']).issubset(exact_names)
phonetic_only = entries.loc[entries.match_status.eq('Phonetic only')]
assert not phonetic_only['first_token'].isin(exact_names).any()
assert phonetic_only['phonetic_key'].isin(reference_keys).all()
assert not entries.loc[entries.match_status.eq('No reference match'),'phonetic_key'].isin(reference_keys).any()
assert (collisions['Distinct spellings'] > 1).all()
assert set(pd.read_csv('name_frequencies.csv').columns) == {'Name', 'Frequency'}
assert Path('matching_coverage.png').is_file()
assert abs(sum(p.get_height() for p in axes[0].patches) - len(entries)) < 1e-8
print('PASS: normalization, initials, matching partitions, reference coverage and chart totals')
"""))
km = KernelManager(kernel_name="python3")
km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
client = NotebookClient(nb, km=km, timeout=180,
    resources={"metadata": {"path": str(root)}})
try:
    client.execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nb.cells.pop()
nbformat.write(nb, root / "notebook.ipynb")
print("PASS: notebook executed from cleared outputs; name-matching and chart checks passed.")
