import unittest
import json
from datetime import datetime, timezone
from core.intelligence_engine import IntelligenceEngine

class TestInformationIntelligencePilot(unittest.TestCase):
    def setUp(self):
        self.engine = IntelligenceEngine("tests/fixtures/intelligence_mock.duckdb")
        self.now = datetime.now(timezone.utc).isoformat()
        
    def test_get_exposures(self):
        # A. Can it map Entity -> Exposure?
        exposures = self.engine.get_exposures('ENT_PTBA', self.now)
        self.assertEqual(len(exposures), 1)
        self.assertEqual(exposures[0]['target'], 'Coal (Newcastle)')
        self.assertEqual(exposures[0]['basis'], 'REVENUE')

    def test_get_contextual_peers(self):
        # H. Can it determine contextual peers?
        peers = self.engine.get_contextual_peers('ENT_PTBA', self.now)
        self.assertIn('ENT_ADRO', peers)
        
    def test_asymmetric_beneficiary_detection(self):
        # J. Can it detect asymmetric beneficiary candidates?
        # K. Can it detect counterfactual non-reactions?
        result = self.engine.analyze_event_impact('EVT_COAL_BAN', self.now)
        self.assertEqual(result['status'], 'ANALYSIS_COMPLETE')
        
        # We expect 2 entities to be analyzed (PTBA, ADRO)
        self.assertEqual(len(result['results']), 2)
        
        ptba_result = next(r for r in result['results'] if r['entity'] == 'ENT_PTBA')
        adro_result = next(r for r in result['results'] if r['entity'] == 'ENT_ADRO')
        
        # PTBA dropped 10, ADRO dropped 2. Differential = -10 - (-2) = -8. 
        self.assertEqual(ptba_result['differential'], -8.0)
        self.assertEqual(ptba_result['specificity_status'], 'ASYMMETRIC_DETRIMENT_CANDIDATE')
        
        # ADRO dropped 2, PTBA dropped 10. Differential = -2 - (-10) = +8.
        self.assertEqual(adro_result['differential'], 8.0)
        self.assertEqual(adro_result['specificity_status'], 'ASYMMETRIC_BENEFICIARY_CANDIDATE')
        
        print("\n[VALIDATION RESULT]")
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    unittest.main()
