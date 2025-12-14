class QualificationSystem:
    def __init__(self):
        self.frameworks = {
            "BANT": ["Budget", "Authority", "Need", "Timeline"],
            "MEDDIC": ["Metrics", "Economic Buyer", "Decision Criteria", "Decision Process", "Identify Pain", "Champion"]
        }

    def score_lead(self, lead, icp):
        """
        Calculates a 0-100 fit score based on data availability and ICP match.
        """
        score = 0
        
        # 1. Industry Fit (30 pts)
        if icp['industry'].lower() in lead['industry'].lower():
            score += 30
            
        # 2. Size Fit (20 pts)
        # (Simplified string matching for demo)
        if icp['size'] in lead.get('employee_count', ''):
            score += 20
            
        # 3. Data Richness (20 pts)
        if lead.get('website') and lead.get('description'):
            score += 20
            
        # 4. Intent Signals (Mocked) (30 pts)
        if "hiring" in lead.get('signals', []):
            score += 30
            
        return score