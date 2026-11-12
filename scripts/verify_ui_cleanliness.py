import os
import re

course_codes = [
    'EC23C01', 'EC23C02', 'EC23C03', 'EC23C04', 'EC23C05', 'EC23C06',
    'EC23C07', 'EC23C08', 'EC23S01', 'EC23E04', 'EC8702', 'IOT8701',
    'HDL6001', 'VLSI6002', 'EMB5001', 'DSP4001', 'RF3001'
]

findings = []

for root, _, files in os.walk('src'):
    for f in files:
        if f.endswith(('.astro', '.jsx', '.tsx')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines, 1):
                # Ignore non-rendered metadata lines
                if any(k in line for k in ['import ', '//', '/*', 'id:', 'courseId:', 'activeSubjectId', 'activeCourseId', 'href=', 'courseKey', 'params', 'selectedCourse ===', 'item.id', 'targetCourseId', 'course_code', 'COURSE_LOOKUP', 'NPTEL_VIDEO_REGISTRY']):
                    continue
                for cc in course_codes:
                    pattern = rf'(?:>|\bspan\b|\bh\d\b|\bp\b|\bdiv\b|Badge)[^<]*\b{cc}\b'
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append((p, idx, line.strip()))

print(f"Total suspicious visible course code occurrences in UI markup: {len(findings)}")
for p, idx, l in findings:
    print(f"  {p}:{idx} -> {l}")
