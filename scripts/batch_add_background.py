"""
Batch utility: Adds ScientificMolecularBackground to all major page components.
"""
import re
from pathlib import Path

IMPORT_LINE = "import { ScientificMolecularBackground } from '../components/common/ScientificMolecularBackground';"
COMPONENT_JSX = "      <ScientificMolecularBackground intensity={0.55} />"

PAGES = [
    'frontend/src/pages/DesignStudioPage.tsx',
    'frontend/src/pages/AnalysisPipelinePage.tsx',
    'frontend/src/pages/GRNACandidatesPage.tsx',
    'frontend/src/pages/OffTargetPage.tsx',
    'frontend/src/pages/TOPSISRankingPage.tsx',
    'frontend/src/pages/ModelPerformancePage.tsx',
    'frontend/src/pages/AnalysisHistoryPage.tsx',
    'frontend/src/pages/MethodologyPage.tsx',
    'frontend/src/pages/ReportsPage.tsx',
]

for page in PAGES:
    p = Path(page)
    if not p.exists():
        print(f"SKIP (not found): {page}")
        continue

    text = p.read_text(encoding='utf-8')

    if 'ScientificMolecularBackground' in text:
        print(f"SKIP (already present): {page}")
        continue

    lines = text.split('\n')

    # Find last import line index
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import '):
            last_import_idx = i

    lines.insert(last_import_idx + 1, IMPORT_LINE)
    text = '\n'.join(lines)

    # Add 'relative' to first top-level return div className and insert background component
    def add_bg(match):
        cls = match.group(2)
        if 'relative' not in cls:
            cls = 'relative ' + cls
        inner = match.group(3)
        return f'{match.group(1)}{cls}{inner}\n{COMPONENT_JSX}'

    new_text = re.sub(
        r'(    <div className=")([^"]*?)("[ >])',
        add_bg,
        text,
        count=1
    )

    if new_text == text:
        # Try alternate indentation
        def add_bg2(match):
            cls = match.group(2)
            if 'relative' not in cls:
                cls = 'relative ' + cls
            inner = match.group(3)
            return f'{match.group(1)}{cls}{inner}\n{COMPONENT_JSX}'
        
        new_text = re.sub(
            r'(  <div className=")([^"]*?)("[ >])',
            add_bg2,
            text,
            count=1
        )

    if new_text != text:
        p.write_text(new_text, encoding='utf-8')
        print(f"UPDATED: {page}")
    else:
        print(f"NO MATCH for return div: {page}")
