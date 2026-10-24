"""Record per-test results without inventing workbook execution statuses."""
import json
import unittest
from pathlib import Path
from django.test.runner import DiscoverRunner

class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({'test': test.id(), 'status': 'Pass', 'actual': 'All assertions passed.'})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({'test': test.id(), 'status': 'Fail', 'actual': str(err[1])})
    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({'test': test.id(), 'status': 'Fail', 'actual': str(err[1])})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({'test': test.id(), 'status': 'Not Run', 'actual': reason})

class EvidenceRunner(DiscoverRunner):
    def get_resultclass(self):
        return EvidenceResult
    def suite_result(self, suite, result, **kwargs):
        Path('evidence').mkdir(exist_ok=True)
        Path('evidence/test-results.json').write_text(json.dumps(result.records, indent=2), encoding='utf-8')
        return super().suite_result(suite, result, **kwargs)
